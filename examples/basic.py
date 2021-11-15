from gromorg import GromOrg
import matplotlib.pyplot as plt
from pyqchem.structure import Structure
from pyqchem.tools import get_geometry_from_pubchem


# Define molecule (ethylene) as pyqchem Structure
structure = Structure(coordinates=[[ 0.6695, 0.0000, 0.0000],
                                   [-0.6695, 0.0000, 0.0000],
                                   [ 1.2321, 0.9289, 0.0000],
                                   [ 1.2321,-0.9289, 0.0000],
                                   [-1.2321, 0.9289, 0.0000],
                                   [-1.2321,-0.9289, 0.0000]],
                      symbols=['C', 'C', 'H', 'H', 'H', 'H'],
                      charge=0,
                      multiplicity=1)

params = {# Run paramters
          'integrator': 'md-vv',     # Verlet integrator
          'nsteps': 5000,            # 0.001 * 5000 = 50 ps
          'dt': 0.001,               # ps
          # Temperature coupling is on
          'tcoupl': 'nose-hoover',    # Nose-Hoover thermostat
          'tau_t': 0.3,               # time constant, in ps
          'ref_t': 100,               # reference temperature, one for each group, in K
          # Bond parameters
          'gen_vel': 'yes',           # assign velocities from Maxwell distributio
          'gen_temp': 100,            # temperature for Maxwell distribution
          'gen_seed': -1,             # generate a random seed
          }

# Set up simulation
calc = GromOrg(structure, params=params, box=[10, 10, 10], angles=[90, 123.570, 90], supercell=[3, 3, 3], silent=True)

# print full GROMACS input
print(calc.get_mdp())

# perform the MD simulation
trajectory, energy = calc.run_md(whole=True)

# save trajectory in GRO format
trajectory.save('traj_test.gro')

# plot energy
plt.plot(energy['potential'], label='potential')
plt.plot(energy['kinetic'], label='kinetic')
plt.plot(energy['total'], label='total')
plt.legend()
plt.show()
