# This scripts creates a database file (.parameter.pkl) with the parameters
# from an itp and a PDB files. This can be used to run gromorg offline.

from gromorg.setparam import SetParams
from pyqchem.structure import Structure

# Initialize the SetParams with database file (append data if file exists)
data = SetParams(filename='.parameter.pkl')

# Add parameters to database
data.add_data('data/ethylene.itp', 'data/ethylene.pdb')  # ethylene


# Test access to parameters for ethylene
structure = Structure(coordinates=[[ 0.6952,  0.0000,  0.0000],
                                   [-0.6695,  0.0000,  0.0000],
                                   [ 1.2321,  0.9289,  0.0000],
                                   [ 1.2321, -0.9289,  0.0000],
                                   [-1.2321,  0.9289,  0.0000],
                                   [-1.2321, -0.9289,  0.0000]],
                      symbols=['C', 'C', 'H', 'H', 'H', 'H'],
                      charge=0,
                      multiplicity=1)

files_dict = data.get_data(structure)
print(files_dict['test.pdb'].decode())
print(files_dict['test.itp'].decode())
