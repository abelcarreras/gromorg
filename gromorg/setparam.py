import openbabel
from gromorg.cache import SimpleCache
from gromorg.utils import pdb_to_xyz
import numpy as np


class SetParams:

    def __init__(self, filename='.parameters.pkl'):
        self._basename = 'test'

        self._cache = SimpleCache(filename=filename)

    def get_hashable_connectivity(self, xyz_txt):

        def sort_pairs(test):
            sorted_1 = np.sort(test, axis=1)

            sorted_2 = sorted(sorted_1, key=lambda x: x[1])
            sorted_3 = sorted(sorted_2, key=lambda x: x[0])

            return np.array(sorted_3)

        class Connectivity():
            def __init__(self, xyz_txt, use_types=False):

                obConversion = openbabel.OBConversion()
                obConversion.SetInAndOutFormats("xyz", "mol2")

                mol = openbabel.OBMol()
                obConversion.ReadString(mol, xyz_txt)

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

        return Connectivity(xyz_txt, use_types=False)

    def add_data(self, itp_file, pdb_file):

        with open(itp_file, 'r') as f:
            itp_txt = f.read()

        with open(pdb_file, 'r') as f:
            pdb_txt = f.read()

        files_dict = {self._basename + '.itp': itp_txt.encode(), self._basename + '.pdb': pdb_txt.encode()}
        xyz_txt = pdb_to_xyz(pdb_txt)

        self._cache.store_calculation_data(self.get_hashable_connectivity(xyz_txt), 'zip_files', files_dict)

    def get_data(self, structure):

        xyz_txt = structure.get_xyz()
        files_dict = self._cache.retrieve_calculation_data(self.get_hashable_connectivity(xyz_txt), 'zip_files')

        return files_dict


if __name__ == '__main__':
    from pyqchem.structure import Structure

    data = SetParams(filename='.parameter.pkl')

    data.add_data('test_param.itp', 'test_param.pdb')

    structure = Structure(coordinates=[[ 0.6952,  0.0000,  0.0000],
                                       [-0.6695,  0.0000,  0.0000],
                                       [ 1.2321,  0.9289,  0.0000],
                                       [ 1.2321, -0.9289,  0.0000],
                                       [-1.2321,  0.9289,  0.0000],
                                       [-1.2321, -0.9289,  0.0000]],
                          symbols=['C', 'C', 'H', 'H', 'H', 'H'],
                          charge=0,
                          multiplicity=1)

    a = data.get_data(structure)
    print(a['test.itp'])
    print(a['test.pdb'])
