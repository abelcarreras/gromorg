GROMORG
=======

A simple tool to run simulations of small organic molecules with gromacs

Features
--------
- Use pyqchem to link first principles & molecular mechanics calculations
- Get parameters from SwissParam automatically
- Clean run without intermediate files


Requirements
------------

- PyQchem (https://github.com/abelcarreras/PyQchem)
- Gromacs (gmxapi)
- Openbabel (python API)
- mdtraj 

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


calc = GromOrg(structure, box=[10, 10, 10], angles=[90, 123.570, 90], supercell=[3, 3, 3])

trajectory, energy = calc.run_md(delete_scratch=True, whole=True)

plt.plot(energy['potential'], label='potential')
plt.plot(energy['kinetic'], label='kinetic')
plt.plot(energy['total'], label='total')
plt.legend()

trajectory.save('trajectory.gro')

plt.show()
```

