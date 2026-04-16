import requests as req
import time
import io
import tarfile
from openbabel import openbabel
from gromorg.cache import SimpleCache
import numpy as np


def set_molecule_name(mol2_text, resname='LIG', resnum=1):
    lines = mol2_text.split('\n')
    new_lines = []
    atom_section = False
    for line in lines:
        if "@<TRIPOS>ATOM" in line:
            atom_section = True
            new_lines.append(line)
            continue
        if "@<TRIPOS>BOND" in line:
            atom_section = False

        if atom_section and len(line.split()) >= 8:
            parts = line.split()
            parts[7] = resname
            parts[6] = '{}'.format(resnum)

            formatted_line = f"{parts[0]:>7} {parts[1]:<5} {parts[2]:>10} {parts[3]:>10} {parts[4]:>10} {parts[5]:<5} {parts[6]:>3} {parts[7]:<8} {parts[8]:>10}"
            new_lines.append(formatted_line)
        else:
            new_lines.append(line)
    return '\n'.join(new_lines)


class SwissParams:

    BASE_URL = 'https://www.swissparam.ch:8443'

    def __init__(self, structure, silent=False, approach='both'):
        """
        :param structure: molecular structure object
        :param silent: suppress progress output
        :param approach: parameterization approach — 'both' (default), 'mmff-based', or 'match'
        """
        self._structure = structure
        self._filename = 'test'
        self._silent = silent
        self._approach = approach

        self._tar_data = None
        self._session_number = None

        self._cache = SimpleCache()

    def get_mol2(self):
        obConversion = openbabel.OBConversion()
        obConversion.SetInAndOutFormats("xyz", "mol2")

        mol = openbabel.OBMol()
        obConversion.ReadString(mol, self._structure.get_xyz())

        if len(mol.Separate()) > 1:
            raise Exception('Structure has more than one molecule')
            # mol = mol.Separate()[0]

        return set_molecule_name(obConversion.WriteString(mol), resname='test', resnum=1)

    def get_hashable_connectivity(self):

        def sort_pairs(test):
            sorted_1 = np.sort(test, axis=1)
            sorted_2 = sorted(sorted_1, key=lambda x: x[1])
            sorted_3 = sorted(sorted_2, key=lambda x: x[0])
            return np.array(sorted_3)

        class Connectivity():
            def __init__(self, structure, use_types=False):
                obConversion = openbabel.OBConversion()
                obConversion.SetInAndOutFormats("xyz", "mol2")

                mol = openbabel.OBMol()
                obConversion.ReadString(mol, structure.get_xyz())

                atomic_data = []
                for i in range(mol.NumAtoms()):
                    if use_types:
                        atomic_data.append((mol.GetAtom(i+1).GetFormalCharge(),
                                            np.product([ord(c) for c in mol.GetAtom(i+1).GetType()]),
                                            ))
                    else:
                        atomic_data.append((mol.GetAtom(i + 1).GetFormalCharge(),
                                            mol.GetAtom(i + 1).GetAtomicNum()
                                            ))

                conn_index = []
                for i in range(mol.NumBonds()):
                    conn_index.append((mol.GetBond(i).GetBeginAtomIdx()-1, mol.GetBond(i).GetEndAtomIdx()-1))

                conn_index = sort_pairs(conn_index)

                self._connectivity = []
                for i, j in conn_index:
                    self._connectivity.append((atomic_data[i], atomic_data[j]))

            def __hash__(self):
                return hash(tuple(self._connectivity))

        return Connectivity(self._structure, use_types=False)

    def submit_file(self):
        if self._session_number is not None:
            return self._session_number

        url = f'{self.BASE_URL}/startparam?approach={self._approach}'

        files = {'myMol2': (self._filename + '.mol2',
                            io.BytesIO(self.get_mol2().encode('utf-8')),
                            'chemical/x-mol2')}

        r = req.post(url, files=files)

        if not self._silent or not r.ok:
            print(f'Server response ({r.status_code}): {r.text}')

        r.raise_for_status()

        for line in r.text.splitlines():
            if 'Session number' in line:
                self._session_number = line.split(':')[1].strip()
                break

        if self._session_number is None:
            raise Exception(f'Failed to get session number. Response:\n{r.text}')

        if not self._silent:
            print(f'Submitted to SwissParam. Session number: {self._session_number}')

        r.close()
        return self._session_number

    def _check_session(self, session_number):
        """Return the status text for a session."""
        url = f'{self.BASE_URL}/checksession?sessionNumber={session_number}'
        r = req.get(url)
        r.raise_for_status()
        text = r.text
        r.close()
        return text

    def get_tar_file(self, wait_time=10):
        """Poll until the job is done, then return the raw tar.gz bytes."""

        if self._tar_data is not None:
            return self._tar_data

        session_number = self.submit_file()

        if not self._silent:
            print('Waiting for SwissParam...')

        n = 0
        while True:
            status = self._check_session(session_number)

            if 'Calculation is finished' in status:
                break
            elif 'Calculation is in the queue' in status or 'Calculation currently running' in status:
                if not self._silent:
                    print('\b' * (np.mod(n - 1, 10) + 7), end="", flush=True)
                    print('waiting' + '.' * np.mod(n, 10), end="", flush=True)
                    n += 1
                time.sleep(wait_time)
            else:
                raise Exception(f'Unexpected status from SwissParam:\n{status}')

        # Retrieve results as tar.gz
        url = f'{self.BASE_URL}/retrievesession?sessionNumber={session_number}'
        r = req.get(url)
        r.raise_for_status()

        if not self._silent:
            print('.done')

        self._tar_data = r.content
        r.close()

        return self._tar_data

    def store_param_tar(self, filename='params.tar.gz'):
        with open(filename, 'wb') as f:
            f.write(self.get_tar_file())

    def get_data_contents(self):
        files_dict = self._cache.retrieve_calculation_data(self.get_hashable_connectivity(), 'tar_files')

        if files_dict is None:
            raw = self.get_tar_file()

            # Debug: inspect the first bytes to identify format
            if not self._silent:
                print(f'Response first bytes: {raw[:16]}')

            tar_bytes = io.BytesIO(raw)

            # Try auto-detection: handles .tar, .tar.gz, .tar.bz2
            try:
                with tarfile.open(fileobj=tar_bytes, mode='r:*') as tar:
                    files_dict = {}
                    for member in tar.getmembers():
                        f = tar.extractfile(member)
                        if f is not None:
                            name = member.name.split('/')[-1]
                            files_dict[name] = f.read()
            except tarfile.ReadError:
                # Fallback: maybe it's still a zip
                from zipfile import ZipFile
                tar_bytes.seek(0)
                with ZipFile(tar_bytes) as zf:
                    files_dict = {name.split('/')[-1]: zf.read(name) for name in zf.namelist()}

            self._cache.store_calculation_data(self.get_hashable_connectivity(), 'tar_files', files_dict)

        return files_dict

    def get_itp_data(self):
        contents = self.get_data_contents()
        # Find .itp file regardless of internal naming
        itp_files = [k for k in contents if k.endswith('.itp')]
        if not itp_files:
            raise Exception('No .itp file found in SwissParam results')
        return contents[itp_files[0]].decode()

    def get_pdb_data(self):
        contents = self.get_data_contents()
        pdb_files = [k for k in contents if k.endswith('.pdb')]
        if not pdb_files:
            raise Exception('No .pdb file found in SwissParam results')
        return contents[pdb_files[0]].decode()


if __name__ == '__main__':
    from pyqchem.structure import Structure

    structure = Structure(coordinates=[[ 0.6952, 0.0000, 0.0000],
                                       [-0.6695, 0.0000, 0.0000],
                                       [ 1.2321, 0.9289, 0.0000],
                                       [ 1.2321,-0.9289, 0.0000],
                                       [-1.2321, 0.9289, 0.0000],
                                       [-1.2321,-0.9289, 0.0000]],
                          symbols=['C', 'C', 'H', 'H', 'H', 'H'],
                          charge=0,
                          multiplicity=1)

    sp = SwissParams(structure)
