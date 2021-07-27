import DataMatrix3D as dm3d
from DataMatrix3D import Segment
import trimesh


def ConnectDmtrxToJaw(jaw, dmtrx):
    return trimesh.util.concatenate(jaw, dmtrx)


def CreateDmtrx(name):
    dataMatrix = dm3d.DataMatrix3D(name, '14x14', [0, 0, 0], 1, Segment.cylinder, [0.8, 1.5])
    dmtrx = dataMatrix.encode3D()
    dmtrx.apply_transform(trimesh.transformations.translation_matrix([0, -17, 0]))
    return dmtrx.subdivide()


def LoadJaw(path):
    return trimesh.load_mesh(path)


def GetJawWithDmtrx(jaw, id):
    return ConnectDmtrxToJaw(jaw, CreateDmtrx(id))
