import numpy as np
import os

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

    from subprocess import Popen, PIPE

    command = 'gmx energy -f {} -o property.xvg'.format(edr_file, output).split()
    qchem_process = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=False)
    (output, err) = qchem_process.communicate(input='{}\n'.format(option).encode())
    qchem_process.wait()
    output = output.decode()
    err = err.decode()

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

