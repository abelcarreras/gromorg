.. highlight:: rst

Parameters
==========

The parameters are obtained automatically using SwissParam service (https://www.swissparam.ch).
This is done in a seamlessly without user intervention. The molecular structure is transformed
to *.mol2* format and the connectivity is generated using OpenBabel library. Then the molecule is
updated to SwissParam servers and the parameters are downloaded. This process requires internet
connection and is usually very fast for small molecules.

Once the parameters are obtained, they are stored in a cache file (.parameters.pkl) in the working
directory. This file can contain the parameters for multiple molecules and it is used for all
calculations performed in the same directory. This file can be used to run calculations offline.

Custom parameters
-----------------

In some cases, the parameters obtained from SwissParam servers are not suitable for the calculation.
In this case, the user can provide custom parameters computed elsewhere. The custom parameters should
be written in an gromacs *.itp* formatted file. Also it is necessary to include a *.pdb* formatted file
of the structure with the same atom labels than the *.itp* file. Then the following function can be used
to generate a *.parameters.pkl* file containing the parameters:

.. code-block:: python

    from gromorg.setparam import SetParams
    from pyqchem.structure import Structure

    # Initialize the SetParams with database file (append data if file exists)
    data = SetParams(filename='.parameters.pkl')

    # Add parameters to database
    data.add_data('ethylene.itp', 'ethylene.pdb')  # ethylene


An example is provided in the *examples* directory (https://github.com/abelcarreras/gromorg/blob/master/examples/set_params.py).

Example data
------------

ethylene.itp
~~~~~~~~~~~~

.. code-block::

    : ----
    ; Built itp for test.mol2
    ;    by user vzoete     Wed Jul 14 16:04:50 UTC 2021
    ; ----
    ;

    [ atomtypes ]
    ; name at.num  mass   charge  ptype    sigma            epsilon
    C=C     6   12.0110  0.0  A         0.372396    0.284512
    HCMM    1    1.0079  0.0  A         0.235197    0.092048


    [ pairtypes ]
    ;  i     j    func     sigma1-4       epsilon1-4 ; THESE ARE 1-4 INTERACTIONS

    [ moleculetype ]
    ; Name nrexcl
    test 3

    [ atoms ]
    ; nr type resnr resid atom cgnr charge mass
       1 C=C  1  LIG C       1 -0.3000  12.0110
       2 C=C  1  LIG C1      2 -0.3000  12.0110
       3 HCMM 1  LIG H       3  0.1500   1.0079
       4 HCMM 1  LIG H1      4  0.1500   1.0079
       5 HCMM 1  LIG H2      5  0.1500   1.0079
       6 HCMM 1  LIG H3      6  0.1500   1.0079

    [ bonds ]
    ; ai aj fu b0 kb, b0 kb
      1   2 1 0.13330  572403.8  0.13330  572403.8
      1   3 1 0.10830  311344.8  0.10830  311344.8
      1   4 1 0.10830  311344.8  0.10830  311344.8
      2   5 1 0.10830  311344.8  0.10830  311344.8
      2   6 1 0.10830  311344.8  0.10830  311344.8

    [ pairs ]
    ; ai aj fu
      3   5 1
      3   6 1
      4   5 1
      4   6 1

    [ angles ]
    ; ai aj ak fu th0 kth ub0 kub th0 kth ub0 kub
      2   1   3 1  121.0040  322.18    121.0040  322.18
      2   1   4 1  121.0040  322.18    121.0040  322.18
      3   1   4 1  119.5230  219.80    119.5230  219.80
      1   2   5 1  121.0040  322.18    121.0040  322.18
      1   2   6 1  121.0040  322.18    121.0040  322.18
      5   2   6 1  119.5230  219.80    119.5230  219.80

    [ dihedrals ]
    ; ai aj ak al fu phi0 kphi mult phi0 kphi mult
      3   1   2   5 9 180.00  25.1040 2   180.00  25.1040 2
      3   1   2   6 9 180.00  25.1040 2   180.00  25.1040 2
      4   1   2   5 9 180.00  25.1040 2   180.00  25.1040 2
      4   1   2   6 9 180.00  25.1040 2   180.00  25.1040 2

    [ dihedrals ]
    ; ai aj ak al fu xi0 kxi xi0 kxi
      1   3   2   4 2   0.00   3.6150     0.00   3.6150
      2   5   1   6 2   0.00   3.6150     0.00   3.6150


    #ifdef POSRES_LIGAND
    [ position_restraints ]
    ; atom  type      fx      fy      fz
       1 1 1000 1000 1000
       2 1 1000 1000 1000
    #endif

.. note::
    Notice that ``moleculetype`` name must be **test**.

ethylene.pdb
~~~~~~~~~~~~

.. code-block::

    REMARK  FOR INFORMATIONS, PLEASE CONTACT:
    REMARK  ZOETE VINCENT
    REMARK  VINCENT.ZOETE_AT_ISB-SIB.CH
    REMARK  SWISS INSTITUTE OF BIOINFORMATICS
    REMARK  MOLECULAR MODELING GROUP
    REMARK  QUARTIER SORGE - BATIMENT GENOPODE
    REMARK  CH-1015 LAUSANNE
    REMARK  SWITZERLAND
    REMARK  T: +41 21 692 4082
    REMARK ****************************************************************
    REMARK   DATE:     7/14/21     16: 4:50      CREATED BY USER: root
    ATOM      1  C   LIG     1       0.669   0.000   0.000  1.00  0.00      LIG
    ATOM      2  C1  LIG     1      -0.669   0.000   0.000  1.00  0.00      LIG
    ATOM      3  H   LIG     1       1.232   0.929   0.000  1.00  0.00      LIG
    ATOM      4  H1  LIG     1       1.232  -0.929   0.000  1.00  0.00      LIG
    ATOM      5  H2  LIG     1      -1.232   0.929   0.000  1.00  0.00      LIG
    ATOM      6  H3  LIG     1      -1.232  -0.929   0.000  1.00  0.00      LIG
    TER       7      LIG      1
    END