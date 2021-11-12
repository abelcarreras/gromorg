import numpy as np
import mdtraj
from pyqchem import Structure

NM_TO_ANGSTROM = 1e1


def _label_to_element(label):
    element = ''
    for char in label:
        if char.isnumeric():
            break
        element += char

    return element


def mdtraj_to_pyqchem(trajectory, frame, residue, center=True):
    """
    Extract molecule from MDTraj trajectory in pyqhcem Structure format

    :param trajectory: MDTraj trajectory
    :param frame: frame index
    :param residue: residue index
    :param center: if true center coordinates at geometric center
    :return: PyQChem structure
    """

    res_indices = []
    names = []
    for res in trajectory.topology.residues:
        res_indices.append([atom.index for atom in res.atoms])
        names.append([atom.name for atom in res.atoms])

    # check limits
    if np.abs(frame) >= trajectory.n_frames:
        raise Exception('Frame error. Trajectory length is {}'.format(trajectory.n_frames))

    if np.abs(residue) >= len(res_indices):
        raise Exception('Residue error. Number of residues is {}'.format(len(res_indices)))


    coordinates = trajectory.atom_slice(res_indices[residue])[frame].xyz[0] * NM_TO_ANGSTROM
    symbols = [_label_to_element(symbol) for symbol in names[residue]]

    if center:
        gc_coordinates = np.average(coordinates, axis=0)
        coordinates -= gc_coordinates

    molecule = Structure(coordinates=coordinates,
                         symbols=symbols)

    return molecule


def get_cluster(trajectory, frame, residue, cutoff=5.0, center=True):
    """
    Extract molecule cluster from a MDTraj trajectory

    :param trajectory: MDTraj trajectory
    :param frame: trajectory frame index
    :param residue: central residue index
    :param cutoff: cutoff distance in Angstroms
    :param center: If true, center molecule at geometric center
    :return: PyQChem structure
    """

    # res_indices = list(range(trajectory.topology.n_residues))

    res_indices = [(residue, i) for i in range(trajectory.topology.n_residues)]
    distances, pairs = mdtraj.compute_contacts(trajectory[frame], res_indices, scheme='closest', ignore_nonprotein=True)

    indices = np.argwhere(distances[0] < cutoff / NM_TO_ANGSTROM).T[0]

    res_indices = []
    names = []
    for res in trajectory.topology.residues:
        res_indices.append([atom.index for atom in res.atoms])
        names.append([atom.name for atom in res.atoms])

    coordinates = []
    symbols = []

    if len(indices) == 0:
        indices = [0]

    for i in indices:
        coordinates += list(trajectory.atom_slice(res_indices[i])[frame].xyz[0] * NM_TO_ANGSTROM)
        symbols += list([_label_to_element(symbol) for symbol in names[i]])

    if center:
        gc_coordinates = np.average(coordinates, axis=0)
        coordinates -= gc_coordinates

    molecule = Structure(coordinates=coordinates,
                         symbols=symbols)

    return molecule
