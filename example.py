from gromorg import GromOrg
import matplotlib.pyplot as plt
from pyqchem.structure import Structure
from pyqchem.tools import get_geometry_from_pubchem


structure = Structure(coordinates=[[ 0.6695, 0.0000, 0.0000],
                                   [-0.6695, 0.0000, 0.0000],
                                   [ 1.2321, 0.9289, 0.0000],
                                   [ 1.2321,-0.9289, 0.0000],
                                   [-1.2321, 0.9289, 0.0000],
                                   [-1.2321,-0.9289, 0.0000]],
                      symbols=['C', 'C', 'H', 'H', 'H', 'H'],
                      charge=0,
                      multiplicity=1)



# benzene = get_geometry_from_pubchem('benzene')

calc = GromOrg(structure, box=[10, 10, 10], angles=[90, 123.570, 90], supercell=[3, 3, 3])

#calc.get_trajectory()

#exit()
trajectory, energy = calc.run_md(delete_scratch=True, whole=True)

#from gromorg import whole_trajectory

#trajectory = whole_trajectory('')



plt.plot(energy['potential'], label='potential')
plt.plot(energy['kinetic'], label='kinetic')
plt.plot(energy['total'], label='total')
plt.legend()

#trajectory.make_molecules_whole()
trajectory.save('traj_test.gro')



plt.show()
