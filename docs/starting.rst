.. highlight:: rst

Get started
===========


Defining molecule
-----------------

The definition of the molecule is done creating an instance of PyQchem Structure class.
See PyQchem manual for more details. Charge and multiplicity are ignored.

Example of ethylene:

.. code-block:: python

    from pyqchem.structure import Structure

    structure = Structure(coordinates=[[ 0.6695, 0.0000, 0.0000],
                                       [-0.6695, 0.0000, 0.0000],
                                       [ 1.2321, 0.9289, 0.0000],
                                       [ 1.2321,-0.9289, 0.0000],
                                       [-1.2321, 0.9289, 0.0000],
                                       [-1.2321,-0.9289, 0.0000]],
                          symbols=['C', 'C', 'H', 'H', 'H', 'H'])


Defining GROMACS input parameters
---------------------------------

GROMACS input parameters are defined in a dictionary. For example:

.. code-block:: python

    gmx_params = {
                 'integrator': 'md-vv',     # Verlet integrator
                 'nsteps': 10000,           # 0.001 * 10000 = 100 ps
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


The defined parameters override/add to the default values set by gromorg.
This way for most purposes it is not necessary to define most parameters.
These default values are:

.. code-block:: python

    'integrator': 'md-vv',     # Verlet integrator
    'nsteps': 5000,            # 0.001 * 5000 = 50 ps
    'dt': 0.001,               # ps
    # Output control
    'nstxout': 1,              # save coordinates every 0.001 ps
    'nstvout': 1,              # save velocities every 0.001 ps
    'nstenergy': 1,            # save energies every 0.001 ps
    'nstlog': 100,             # update log file every 0.1 ps
    # Bond parameters
    'continuation': 'no',       # first dynamics run
    'cutoff-scheme': 'Verlet',  # Buffered neighbor searching
    'verlet-buffer-tolerance': 3.3e-03,
    # 'ns_type': 'grid',          # search neighboring grid cells
    'nstlist': 10,              # 20 fs, largely irrelevant with Verlet
    'rcoulomb': 1.0,            # short-range electrostatic cutoff (in nm)
    'rvdw': 1.0,                # short-range van der Waals cutoff (in nm)
    'DispCorr': 'EnerPres',     # account for cut-off vdW scheme
    # Electrostatics
    'coulombtype': 'PME',       # Particle Mesh Ewald for long-range electrostatics
    'pme_order': 4,             # cubic interpolation
    'fourierspacing': 0.16,     # grid spacing for FFT
    # Temperature coupling is on
    'tcoupl': 'nose-hoover',    # Nose-Hoover thermostat
    'tc-grps': 'system',        # one coupling group
    'tau_t': 0.3,               # time constant, in ps
    'ref_t': 100,               # reference temperature, one for each group, in K
    # Pressure coupling is off
    'pcoupl': 'no',             # no pressure coupling in NVT
    # Periodic boundary conditions
    'pbc': 'xyz',               # 3-D PBC
    # Velocity generation
    'gen_vel': 'yes',           # assign velocities from Maxwell distributio
    'gen_temp': 10,             # temperature for Maxwell distribution
    'gen_seed': -1,             # generate a random seed


Setting up the calculation
--------------------------

Example of simple parallel(openMP) calculation using 4 threads:

.. code-block:: python

    calc = GromOrg(structure,
                   params=gmx_params,        # MDP parms
                   box=[10, 10, 10],         # unitcell a, b, c in angstrom
                   angles=[90, 90, 90],      # unitcell alpha, beta, gamma in degree
                   supercell=[3, 3, 3],      # size of supercell
                   delete_scratch=True,      # if true delete temp files when finished (default: True)
                   silent=False,             # if true print MD log info in screen (default: False)
                   omp_num_threads=False,    # number of parallel threads used (default: 1)
                   maxwarn=0,                # max number of GROMACS warnings (default: 0)
                   )

The defined structure correspond to the unit cell and it is replicated according to the ``supercell`` argument. This means
that while usually will contain a single molecule, it is possible to include several units particularly to define crystals.
The number of MPI processes is automatically set according to the cores available and the ``omp_num_threads`` parameter.
The calculation is run in a temporary folder in the current working directory. This directory is deleted by default
when the calculation is finished. ``delete_scratch`` keyword can be set to change this behavior.

``maxwarn`` keyword can be used to set the maximum number of warnings GROMACS can ignore before aborting the calculation.
It is recommended to keep this value to 0 (default) and only change it once you have revised all warnings and made sure
you can ignore them.


Run the calculation
-------------------
Once the calculation is set up, it can be run with the following command:

.. code-block:: python

    trajectory, energy = calc.run_md(whole=True)  # unwraps the trajectory


The return of this function is the trajectory as a MDtraj object and the energy as a dictionary.
MDtraj is a flexible format to store trajectory data. Check the documentation of MDtraj for
more information. (https://www.mdtraj.org/1.9.5/load_functions.html).
The only argument of this function is ``whole``, this optional arguments controls the unwrapping
of the trajectory. That is, if ``whole`` is True, the trajectory is unwrapped such that the molecules
are shown as whole for each step of the trajectory.

A simple way to visualize the trajectory is to store it in the disk as a common format. This
can be done using ``save`` method:

.. code-block:: python

    trajectory.save('trajectory.gro')


MDtraj supports different formats, such as GROMACS (gro), Protein Data Bank (pdb) and xyz.

Energy dictionary contains the total energy, the kinetic energy and the potential energy as lists.
This can be plotted, for example, as:

.. code-block:: python

    import matplotlib.pyplot as plt
    plt.plot(energy['potential'], label='potential')
    plt.plot(energy['kinetic'], label='kinetic')
    plt.plot(energy['total'], label='total')
    plt.legend()
    plt.show()



Extracting molecules from trajectory
------------------------------------

One of the main applications of Gromorg is use the geometries of the molecules within the
trajectory. For this purpose gromorg package provides some functions to do this.
``mdtraj_to_pyqchem`` function is used to extract a particular molecule from a trajectory.

.. code-block:: python

    from gromorg.tools import mdtraj_to_pyqchem

    molecule = mdtraj_to_pyqchem(trajectory, ifame, ires, center=True)

where ``trajectory`` is the trajectory as a MDtraj object, ``ifame`` is the index of the
frame and ``ires`` is the index of the residue. ``center`` is an optional argument that
centers the molecule in the origin. Each residue correspond to a unit cell (*structure*
in the first example), this means that in the case that the unit cell contains multiple
molecules, the separation of them will need to be done manually.

The return of this function is a PyQChem Structure containing the molecule. This object
can be used directly with PyQchem to perform quantum chemistry calculations. For example:

.. code-block:: python

    from gromorg.tools import mdtraj_to_pyqchem
    from pyqchem import QchemInput, get_output_from_qchem

    qc_input = QchemInput(molecule,
                          jobtype='sp',
                          exchange='hf',
                          basis='6-31G')

    output = get_output_from_qchem(qc_input)

    print(output)

