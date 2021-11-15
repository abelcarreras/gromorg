from gromorg import GromOrg
from pyqchem.tools import get_geometry_from_pubchem
from gromorg.tools import get_cluster


# get structures from PubChem database (main and solvent)
structure = get_geometry_from_pubchem('(S)-N-(3-(4-(2-hydroxy-1-phenylethylamino)-6-phenylfuro[2,3-d]pyrimidin-5-yl)phenyl)acrylamide')
solvent = get_geometry_from_pubchem('water')

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


# define simulation box with one molecule with solvent
calc = GromOrg(structure, params=params, box=[30, 30, 30], supercell=[1, 1, 1], silent=False,
               solvent=solvent, solvent_scale=0.5,
               )

trajectory, energy = calc.run_md(whole=True)

# get molecule (residue 0) at frame 5000 with close distance solvent molecules (<3.0 angstrom)
molecule = get_cluster(trajectory, frame=5000, residue=0, cutoff=3.0, center=False)
print(molecule)

