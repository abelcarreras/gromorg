from gromorg import GromOrg
from pyqchem import Structure
from pyqchem.tools import get_geometry_from_pubchem


# Main molecule
structure = Structure(coordinates=[[ 0.6695, 0.0000, 0.0000],
                                   [-0.6695, 0.0000, 0.0000],
                                   [ 1.2321, 0.9289, 0.0000],
                                   [ 1.2321,-0.9289, 0.0000],
                                   [-1.2321, 0.9289, 0.0000],
                                   [-1.2321,-0.9289, 0.0000]],
                      symbols=['C', 'C', 'H', 'H', 'H', 'H'],
                      charge=0,
                      multiplicity=1)


# Solvent molecule
solvent = Structure(coordinates=[[0.000000,  0.000000,  0.000000],
                                 [0.758602,  0.000000,  0.504284],
                                 [0.758602,  0.000000,  -0.504284]
                                 ],
                      symbols=['O', 'H', 'H'])


# Alternative: get molecules from PubChem
# structure = get_geometry_from_pubchem('ethylene')
# solvent = get_geometry_from_pubchem('water')

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


calc = GromOrg(structure,
               params=params,
               box=[60, 60, 60],
               supercell=[1, 1, 1],
               solvent=solvent,
               solvent_scale=0.57,
               )

trajectory, energy = calc.run_md(whole=True)

trajectory.save('traj_etylene_sol.gro')
