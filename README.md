GroMorG
=======

A simple python tool to run MD simulations of small organic molecules with gromacs

Features
--------
- Use PyQchem to link first principles & molecular mechanics calculations
- Get parameters from SwissParam automatically
- Clean run without intermediate files


Requirements
------------

- PyQchem (https://github.com/abelcarreras/PyQchem)
- Gromacs (gmxapi)
- Openbabel (python API)
- MDtraj 

Example
-------

```python
from gromorg import GromOrg
import matplotlib.pyplot as plt
from pyqchem.structure import Structure


structure = Structure(coordinates=[[ 0.6695, 0.0000, 0.0000],
                                   [-0.6695, 0.0000, 0.0000],
                                   [ 1.2321, 0.9289, 0.0000],
                                   [ 1.2321,-0.9289, 0.0000],
                                   [-1.2321, 0.9289, 0.0000],
                                   [-1.2321,-0.9289, 0.0000]],
                      symbols=['C', 'C', 'H', 'H', 'H', 'H'])


gmx_params = {# Run paramters
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

calc = GromOrg(structure, 
               params=gmx_params,        # MDP parms 
               box=[10, 10, 10],         # a, b, c in angstrom
               angles=[90, 123.570, 90], # alpha, beta, gamma in degree
               supercell=[3, 3, 3])

trajectory, energy = calc.run_md(delete_scratch=True, # delete temp files when finished 
                                 whole=True,          # show whole molecules in trajectory
                                 silent=False)        # print MD log info in screen

plt.plot(energy['potential'], label='potential')
plt.plot(energy['kinetic'], label='kinetic')
plt.plot(energy['total'], label='total')
plt.legend()

trajectory.save('trajectory.gro')

plt.show()
```

Contact info
------------
Abel Carreras  
abelcarreras83@gmail.com

Donostia International Physics Center (DIPC)  
Donostia-San Sebastian, Euskadi (Spain)
