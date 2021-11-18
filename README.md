[![Documentation Status](https://readthedocs.org/projects/gromorg/badge/?version=latest)](https://gromorg.readthedocs.io/en/latest/?badge=latest)

GroMorG
=======

A python tool to automate the calculation of MD simulations of small organic molecules using gromacs.

Features
--------
- Link first principles & molecular mechanics calculations using PyQchem
- Get parameters from SwissParam (https://www.swissparam.ch) automatically from molecular structure
- Clean run without intermediate files
- Add solvent molecules to the system
- Extract structures from the trajectory (including surrounding solvent molecules)

Requirements
------------
- PyQchem (https://github.com/abelcarreras/PyQchem)
- Gromacs (gmxapi) (http://www.gromacs.org)
- Openbabel (python API) (http://openbabel.org)
- MDtraj (https://www.mdtraj.org)

Basic example
-------------
```python
from gromorg import GromOrg
import matplotlib.pyplot as plt
from pyqchem.structure import Structure

# Define moleule as PyQchem Structure
structure = Structure(coordinates=[[ 0.6695, 0.0000, 0.0000],
                                   [-0.6695, 0.0000, 0.0000],
                                   [ 1.2321, 0.9289, 0.0000],
                                   [ 1.2321,-0.9289, 0.0000],
                                   [-1.2321, 0.9289, 0.0000],
                                   [-1.2321,-0.9289, 0.0000]],
                      symbols=['C', 'C', 'H', 'H', 'H', 'H'])

# Define Gromacs parameters
gmx_params = {
             'integrator': 'md-vv',     # Verlet integrator
             'nsteps': 5000,            # 0.001 * 5000 = 50 ps
             'dt': 0.001,               # time step, in ps
             # Temperature coupling is on
             'tcoupl': 'nose-hoover',    # Nose-Hoover thermostat
             'tau_t': 0.3,               # time constant, in ps
             'ref_t': 300,               # reference temperature, one for each group, in K
             # Bond parameters
             'gen_vel': 'yes',           # assign velocities from Maxwell distributio
             'gen_temp': 300,            # temperature for Maxwell distribution
             'gen_seed': -1,             # generate a random seed
             }

# Define simulation
calc = GromOrg(structure, 
               params=gmx_params,        # MDP parms 
               box=[10, 10, 10],         # a, b, c in angstrom
               angles=[90, 90, 90],      # alpha, beta, gamma in degree
               supercell=[3, 3, 3],
               delete_scratch=True,      # delete temp files when finished
               silent=False)             # print MD log info in screen

# Run simulation and get trajectory (MDTraj) and energy
trajectory, energy = calc.run_md(whole=True) 

# plot energies
plt.plot(energy['potential'], label='potential')
plt.plot(energy['kinetic'], label='kinetic')
plt.plot(energy['total'], label='total')
plt.legend()
plt.show()

# Store trajectory
trajectory.save('trajectory.gro')
```

Contact info
------------
Abel Carreras  
abelcarreras83@gmail.com

Donostia International Physics Center (DIPC)  
Donostia-San Sebastian, Euskadi (Spain)
