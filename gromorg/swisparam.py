import requests as req
from lxml import html
import time
import io
from zipfile import ZipFile
import openbabel
from gromorg.cache import SimpleCache
import numpy as np


class SwissParams:

    def __init__(self, structure, silent=False):
        self._structure = structure
        self._filename = 'test'
        self._silent = silent

        self._zip_data = None
        self._url_data = None

        self._cache = SimpleCache()

    def get_mol2(self):
        obConversion = openbabel.OBConversion()
        obConversion.SetInAndOutFormats("xyz", "mol2")

        mol = openbabel.OBMol()
        obConversion.ReadString(mol, self._structure.get_xyz())

        return obConversion.WriteString(mol)

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

                # mol.AddHydrogens()

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

                return

            def __hash__(self):
                return hash(tuple(self._connectivity))

        return Connectivity(self._structure, use_types=False)

    def get_zip_file(self, wait_time=10):

        if self._zip_data is not None:
            return self._zip_data

        url_data = self.submit_file()

        url_zip = url_data.replace('index.html', self._filename + '.zip')

        r_data = req.get(url_data, allow_redirects=True)

        if not self._silent:
            print('connecting to SwissParam...')
            print('url: {}'.format(url_data))

        n = 0
        while 'Your job is currently being performed' in r_data.text:
            r_data = req.get(url_data, allow_redirects=True)
            if not self._silent:
                print('\b' * (np.mod(n - 1, 10) + 7), end="", flush=True)
                print('waiting' + '.' * np.mod(n, 10), end="", flush=True)
                n += 1

            time.sleep(wait_time)

        r = req.get(url_zip, allow_redirects=True)

        if r.status_code == 404:
            print(r_data.text)
            raise Exception('Failed retrieving parameters from SwissParam')

        if not self._silent:
            print('.done')

        self._zip_data = r.content

        r.close()
        r_data.close()

        return self._zip_data

    def store_param_zip(self, filename='params.zip'):
        with open(filename, 'wb') as f:
            f.write(self.get_zip_file())

    def submit_file(self):

        if self._url_data is not None:
            return self._url_data

        url = 'https://www.swissparam.ch/submit.php'

        files = {'MAX_FILE_SIZE': '30000000',
                 'mol2Files': (self._filename + '.mol2',
                               io.StringIO(self.get_mol2()),
                               'multipart/form-data')}

        r = req.post(url, files=files)

        tree = html.fromstring(r.content)

        self._url_data = tree.xpath('//a[@class="sib_link"]/text()')[0]

        r.close()

        return self._url_data

    def get_data_contents(self):

        files_dict = self._cache.retrieve_calculation_data(self.get_hashable_connectivity(), 'zip_files')

        if files_dict is None:
            input_zip = ZipFile(io.BytesIO(self.get_zip_file()))
            files_dict = {name: input_zip.read(name) for name in input_zip.namelist()}
            self._cache.store_calculation_data(self.get_hashable_connectivity(), 'zip_files', files_dict)

        return files_dict

    def get_itp_data(self):
        return self.get_data_contents()[self._filename + '.itp'].decode()

    def get_pdb_data(self):
        return self.get_data_contents()[self._filename + '.pdb'].decode()


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
    sp.get_hashable_connectivity()