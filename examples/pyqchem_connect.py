from gromorg import GromOrg
import matplotlib.pyplot as plt
from gromorg.tools import mdtraj_to_pyqchem
from pyqchem import get_output_from_qchem, QchemInput, Structure
from pyqchem.parsers.parser_cis import basic_cis
import numpy as np


# define molecule (ethylene)
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

# calculate MD simulation
calc = GromOrg(structure, params=params, box=[20, 20, 20], supercell=[3, 3, 3], silent=False, delete_scratch=True)
trajectory, energy = calc.run_md(whole=True)

# store trajectory
trajectory.save('trajectory.gro')

# connection with Q-Chem
excitation_energies = []
for iframe in np.linspace(2000, 5000, 500):

    # get random molecule sample from 500 frames between 2000 and 5000
    ires = np.random.randint(3*3*3)
    molecule = mdtraj_to_pyqchem(trajectory, frame=int(iframe), residue=ires)  # extract molecule from trajectory

    # Qchem TD-DFT calculation
    qc_input = QchemInput(molecule,
                          jobtype='sp',
                          exchange='b3lyp',
                          cis_n_roots=1,
                          basis='sto-3g',
                          unrestricted=True)

    # parse qchem output
    data = get_output_from_qchem(qc_input,
                                 processors=6,
                                 force_recalculation=True,
                                 parser=basic_cis,
                                 )

    print('scf energy', data['scf_energy'], 'H')
    # get fist excited state excitation energy
    excitation_energies.append(data['excited_states'][0]['excitation_energy'])


# plot histogram of excitation energies
plt.hist(excitation_energies, density=True)
plt.xlabel('Excitation energy [eV]')
plt.show()
