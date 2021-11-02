import numpy as np


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
    :return:
    """

    from pyqchem import Structure

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


    nm_to_angs = 1e1
    coordinates = trajectory.atom_slice(res_indices[residue])[frame].xyz[0] * nm_to_angs
    symbols = [_label_to_element(symbol) for symbol in names[residue]]

    if center:
        gc_coordinates = np.average(coordinates, axis=0)
        coordinates -= gc_coordinates

    molecule = Structure(coordinates=coordinates,
                         symbols=symbols)

    return molecule
