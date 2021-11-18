.. highlight:: rst

Introduction
============

Gromorg in a python interface for Gromacs, a popular software to simulate
molecular dynamics using molecular mechanics originally developed within the
Biophysical Chemistry department at University of Groningen.

Gromorg aims to provide a simple interface to automate the process of
simulating molecular dynamics of small organic molecules from simple structural
information. This includes the determination of the molecular connectivity,
the obtainment the force field parameters, the build of the unitcell/supercell,
the solvation of the system and the parsing of the outputs.

The philosophy of Gromorg is to provide a simple interface to link MD simulations
performed with Gromacs with other tools using python. An example is its close connection
with PyQchem (https://github.com/abelcarreras/PyQchem), a python interface for Q-Chem.

Main features
-------------

- Link first principles & molecular mechanics calculations using PyQchem.
- Get parameters from SwissParam (https://www.swissparam.ch) automatically from molecular structure
- Clean run without intermediate files
- Add solvent molecules to the system
- Extract structures from the trajectory (including surrounding solvent molecules)

