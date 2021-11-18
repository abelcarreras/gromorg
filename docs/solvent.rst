.. highlight:: rst

Solvent
=======

Solvent molecules can be easily added in analogous way to the main molecule.
First the solvent molecule is defined as a PyQchem Structure object.

Example of water:

.. code-block:: python

    solvent = Structure(coordinates=[[0.000000,  0.000000,  0.000000],
                                     [0.758602,  0.000000,  0.504284],
                                     [0.758602,  0.000000,  -0.504284]
                                     ],
                          symbols=['O', 'H', 'H'])

then the solvent molecule is added during the calculation setup:

.. code-block:: python

    calc = GromOrg(structure,
                   params=gmx_params,        # MDP parms
                   box=[30, 30, 30],         # unitcell a, b, c in angstrom
                   supercell=[1, 1, 1],      # size of supercell
                   solvent=solvent,          # solvent molecule
                   solvent_scale=0.57,       # solvent scale parameter
                   )

To adjust the density of the solvent molecule, the solvent_scale parameter can be used.
This correspond to the ``-scale`` option in the ``gmx solvate`` command.
(https://manual.gromacs.org/current/onlinehelp/gmx-solvate.html?highlight=solvate)

