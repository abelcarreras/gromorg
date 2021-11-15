from gromorg import GromOrg
import matplotlib.pyplot as plt
from pyqchem.structure import Structure


# Define naphthalene unit cell (2 molecules)
naphthalene = Structure(coordinates=[[-0.879056,  0.105037,  2.364700],
                                     [-0.125716,  0.962042,  1.597606],
                                     [ 0.218241,  0.620970,  0.265160],
                                     [ 0.990084,  1.486032, -0.551051],
                                     [ 1.315660,  1.125565, -1.836908],
                                     [-1.135021,  0.384936,  3.383302],
                                     [ 0.218405,  1.915131,  1.992132],
                                     [ 1.330150,  2.433750, -0.138684],
                                     [ 1.921565,  1.786819, -2.443576],
                                     [ 0.879056, -0.105037, -2.364700],
                                     [ 0.125716, -0.962042, -1.597606],
                                     [-0.218241, -0.620970, -0.265160],
                                     [-0.990084, -1.486032,  0.551051],
                                     [-1.315660, -1.125565,  1.836908],
                                     [ 1.135021, -0.384936, -3.383302],
                                     [-0.218405, -1.915131, -1.992132],
                                     [-1.330150, -2.433750,  0.138684],
                                     [-1.921565, -1.786819,  2.443576],
                                     [ 4.976056,  3.089037, -2.364700],
                                     [ 4.222716,  3.946042, -1.597606],
                                     [ 3.878759,  3.604970, -0.265160],
                                     [ 3.106916,  4.470032,  0.551051],
                                     [ 2.781340,  4.109565,  1.836908],
                                     [ 5.232021,  3.368936, -3.383302],
                                     [ 3.878595,  4.899131, -1.992132],
                                     [ 2.766850,  5.417750,  0.138684],
                                     [ 2.175435,  4.770819,  2.443576],
                                     [ 3.217944,  2.878963,  2.364700],
                                     [ 3.971284,  2.021958,  1.597606],
                                     [ 4.315241,  2.363030,  0.265160],
                                     [ 5.087084,  1.497968, -0.551051],
                                     [ 5.412660,  1.858435, -1.836908],
                                     [ 2.961979,  2.599064,  3.383302],
                                     [ 4.315405,  1.068869,  1.992132],
                                     [ 5.427150,  0.550250, -0.138684],
                                     [ 6.018565,  1.197181, -2.443576]],
                        symbols=['C', 'C', 'C', 'C', 'C', 'H', 'H', 'H', 'H', 'C', 'C', 'C', 'C', 'C',
                                 'H', 'H', 'H', 'H', 'C', 'C', 'C', 'C', 'C', 'H', 'H', 'H', 'H', 'C',
                                 'C', 'C', 'C', 'C', 'H', 'H', 'H', 'H'],
                        charge=0,
                        multiplicity=1)

# Gromacs parameters
params = {  # Run parameters
            'integrator': 'md-vv',    # Verlet integrator
            'nsteps': 2000,           # 0.001 * 2000 = 20 ps
            'nstxout': 10,            # save coordinates every 0.01 ps
            'nstvout': 10,            # save velocities every 0.01 ps
            'nstfout': 10,            # save forces every 0.01 ps
            'nstenergy': 10,          # save energies every 0.01 ps
            'dt': 0.001,              # ps
            # Temperature coupling is on
            'tcoupl': 'nose-hoover',  # Nose-Hoover thermostat
            'tau_t': 0.3,             # time constant, in ps
            'ref_t': 300,             # reference temperature, one for each group, in K
            # Bond parameters
            'gen_vel': 'yes',         # assign velocities from Maxwell distributio
            'gen_temp': 300,          # temperature for Maxwell distribution
            'gen_seed': -1,           # generate a random seed
        }

# setup MD simulation
calc = GromOrg(naphthalene, params=params, box=[8.194, 5.968, 8.669], angles=[90.0, 123.57, 90.0], supercell=[4, 4, 4],
               silent=False, omp_num_threads=4)

# Run the simulation
trajectory, energy = calc.run_md(whole=True)

# Save the trajectory
trajectory.save('trajectory.gro')

# Plot the energy
plt.plot(energy['potential'], label='potential')
plt.plot(energy['kinetic'], label='kinetic')
plt.plot(energy['total'], label='total')
plt.xlabel('Steps')
plt.ylabel('Energy (eV)')
plt.legend()
plt.show()
