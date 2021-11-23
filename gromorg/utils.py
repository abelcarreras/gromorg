import warnings

import numpy as np
import gmxapi as gmx
import os
from packaging import version


def commandline_operation_v1(program, arguments, stdin=None, input_files=None, output_files=None):

    from subprocess import Popen, PIPE

    if isinstance(arguments, list):
        arguments = ' '.join(arguments)

    command = '{} {}'.format(program, arguments)

    for key, value in input_files.items():

        if isinstance(value, list):
            value = ' '.join(value)

        command += ' {} {}'.format(key, value)

    for key, value in output_files.items():
        if isinstance(value, list):
            value = ' '.join(value)

        command += ' {} {}'.format(key, value)

    qchem_process = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
    (output, err) = qchem_process.communicate(input=None if stdin is None else stdin.encode('utf-8'))
    qchem_process.wait()
    output = output.decode()
    err = err.decode()

    # mock class to return same output
    # mock_class = type("mock_classi", (object,), {"run": lambda: None, "output":
    #              type("mock_class", (object,), {"erroroutput": type("mock_class", (object,), {"result": lambda: output + err}),
    #                                             "returncode": type("mock_class", (object,), {"result": lambda: 0})
    #                                             })})
    # return mock_class


def commandline_operation(program, arguments, stdin=None, input_files=None, output_files=None):

    if version.parse(gmx.__version__) < version.parse('0.2.0'):
        warnings.warn('Using mock function for commandline_operation for back compatibility. '
                      'Update to gmxapi >0.2 to get full functionally')
        return commandline_operation_v1(program, arguments, stdin, input_files, output_files)

    grompp = gmx.commandline_operation(program, arguments,
                                       stdin=stdin,
                                       input_files=input_files,
                                       output_files=output_files)

    grompp.run()

    if grompp.output.returncode.result() != 0:
        print(grompp.output.erroroutput.result())


def extract_energy(edr_file, output='property.xvg', initial=0, option=None):
    """
      1  Bond             2  Angle            3  Proper-Dih.      4  Improper-Dih.
      5  LJ-14            6  Coulomb-14       7  LJ-(SR)          8  Disper.-corr.
      9  Coulomb-(SR)    10  Coul.-recip.    11  Potential       12  Kinetic-En.
     13  Total-Energy    14  Conserved-En.   15  Temperature     16  Pres.-DC
     17  Pressure        18  Vir-XX          19  Vir-XY          20  Vir-XZ
     21  Vir-YX          22  Vir-YY          23  Vir-YZ          24  Vir-ZX
     25  Vir-ZY          26  Vir-ZZ          27  Pres-XX         28  Pres-XY
     29  Pres-XZ         30  Pres-YX         31  Pres-YY         32  Pres-YZ
     33  Pres-ZX         34  Pres-ZY         35  Pres-ZZ         36  #Surf*SurfTen
     37  T-LIG

    :param edr_file: EDR filename
    :param output: output filename
    :param option: option number from above
    :return:
    """

    if option is None:
        option = '11, 12, 13'

    commandline_operation('gmx', 'energy',
                                       stdin=option,
                                       input_files={'-f': edr_file},
                                       output_files={'-o': 'property.xvg'})

    data = np.loadtxt('property.xvg', comments=['#', '@'])[initial:].T
    os.remove('property.xvg')

    data[1:, :] *= 0.010364272  # KJ/mol -> eV

    if option == '11, 12, 13':
        return {'time': list(data[0]),
                'potential': list(data[1]),
                'kinetic': list(data[2]),
                'total': list(data[3])}
    else:
        return data


def extract_forces(trajectory_file, tpr_file, step=500):

    commandline_operation('gmx', ['traj', '-of'],
                                       stdin='0',
                                       input_files={'-f': trajectory_file,
                                                    '-s': tpr_file,
                                                    '-b': '{}'.format(step),
                                                    '-e': '{}'.format(step),
                                                    },
                                       )


    forces = np.loadtxt('force.xvg', comments=['#', '@'])[1:].reshape(-1, 3)
    os.remove('force.xvg')

    return forces * 0.00103642723  # KJ/(mol nm) to eV/ang


def pdb_to_xyz(pdb_xyz):
    """
    Convert a pdb file to xyz format
    :param pdb_xyz:
    :return:
    """

    def _label_to_element(label):
        element = ''
        for char in label:
            if char.isnumeric():
                break
            element += char.strip()

        list_changes = {'CA': 'C', 'HA': 'H'}
        if element in list_changes:
            element = list_changes[element]
        return element

    def iter_coordinates():
        for line in pdb_xyz.split('\n'):
            if line.startswith('ATOM'):
                yield np.array(line[30:55].split(), dtype=float)

    def iter_symbols():
        for line in pdb_xyz.split('\n'):
            if line.startswith('ATOM'):
                yield _label_to_element(line[13:16])

    xyz_txt = '{}\n'.format(len(list(iter_symbols())))
    for s, c in zip(iter_symbols(), iter_coordinates()):
        xyz_txt += '\n' + s + ' {:10.5f} {:10.5f} {:10.5f}'.format(*c)

    return xyz_txt

