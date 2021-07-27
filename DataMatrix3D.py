import DataMatrix
import DataMatrixSegment
from enum import Enum
import numpy as np
import trimesh
import math


class Segment(Enum):
    parallelepiped = 0
    cylinder = 1
    hexagon = 2
    hemisphere = 3


class DataMatrix3D(DataMatrix.DataMatrix):

    def __init__(self, text, size, position, segments_height, segments_type, size_3d):
        super().__init__(text, size)
        self.dmtrx = self.get_datamatrix()
        self.position = position
        self.segments_height = segments_height
        self.segments_type = segments_type
        self.size_3d = size_3d
        self.segment = DataMatrixSegment.Dmtrx3DSegment()

    def encode3D(self, poly_num=10):
        segments = self.__place_segments(poly_num)
        substrate = self.__place_substrate()

        dmtrx = trimesh.util.concatenate(segments, substrate)
        dmtrx.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-90), [0, 0, 1], [0, 0, 0]))

        return dmtrx

    def __place_substrate(self):
        substrate_position = [self.position[0] - 2.5,
                              self.position[1],
                              self.position[2] + (self.size_3d[1] - self.segments_height) / 2]
        vertices_substrate, faces_substrate = self.segment.parallelepiped_segment(self.__x_size() + 5,
                                                                                  self.__y_size(),
                                                                                  self.size_3d[1] - self.segments_height,
                                                                                  substrate_position)

        substrate = trimesh.Trimesh(vertices=vertices_substrate, faces=faces_substrate)

        return substrate

    def __use_parallelepiped(self):
        vertices_segments = np.zeros(shape=(self.dmtrx.shape[1] * self.dmtrx.shape[0] * 8, 3))
        faces_segments = np.zeros(shape=(self.dmtrx.shape[1] * self.dmtrx.shape[0] * 12, 3))

        return vertices_segments, faces_segments

    def __use_cylinder(self, poly_num):
        vertices_segments = np.zeros(shape=(self.dmtrx.shape[1] * self.dmtrx.shape[0] * poly_num * 2, 3))
        faces_segments = np.zeros(shape=(self.dmtrx.shape[1] * self.dmtrx.shape[0] * poly_num * 2, 3))

        return vertices_segments, faces_segments

    def __use_hexagon(self):
        vertices_segments = np.zeros(shape=(self.dmtrx.shape[1] * self.dmtrx.shape[0] * 12, 3))
        faces_segments = np.zeros(shape=(self.dmtrx.shape[1] * self.dmtrx.shape[0] * 12, 3))

        return vertices_segments, faces_segments

    def __use_hemisphere(self, poly_num):
        vertices_segments = np.zeros(shape=(self.dmtrx.shape[1] * self.dmtrx.shape[0] * poly_num ** 3, 3))
        faces_segments = np.zeros(shape=(self.dmtrx.shape[1] * self.dmtrx.shape[0] * poly_num ** 3, 3))

        return vertices_segments, faces_segments

    def __place_segments(self, poly_num):

        if self.segments_type == Segment.parallelepiped:
            vertices_segments, faces_segments = self.__use_parallelepiped()
        elif self.segments_type == Segment.cylinder:
            vertices_segments, faces_segments = self.__use_cylinder(poly_num)
        elif self.segments_type == Segment.hexagon:
            vertices_segments, faces_segments = self.__use_hexagon()
        elif self.segments_type == Segment.hemisphere:
            vertices_segments, faces_segments = self.__use_hemisphere(poly_num)
        else:
            return

        count_f = 0
        count_v = 0

        i = 0
        n = 0

        for x in np.arange((-self.__x_size() + self.__step_x()) / 2,
                           (self.__x_size() + self.__step_x()) / 2,
                           self.__step_x()):
            for y in np.arange((-self.__y_size() + self.__step_y()) / 2,
                               (self.__y_size() + self.__step_y()) / 2,
                               self.__step_y()):

                x += self.position[0]
                y += self.position[1]
                z = self.position[2] + self.segments_height / 2 + (self.size_3d[1] - self.segments_height)

                if self.segments_type == Segment.parallelepiped:
                    vertices, faces = self.segment.parallelepiped_segment(self.__step_x(),
                                                                          self.__step_y(),
                                                                          self.segments_height, [x, y, z])
                elif self.segments_type == Segment.cylinder:
                    vertices, faces = self.segment.cylinder_segment(poly_num,
                                                                    self.__step_x() / 2,
                                                                    self.segments_height,
                                                                    [x, y, z])
                elif self.segments_type == Segment.hexagon:
                    vertices, faces = self.segment.hexagon_segment(self.__step_x() / 2,
                                                                   self.segments_height,
                                                                   [x, y, z])

                elif self.segments_type == Segment.hemisphere:
                    vertices, faces = self.segment.hemisphere_segment(poly_num,
                                                                      self.size_3d[0] / 2,
                                                                      [x, y, z])

                if self.dmtrx[i][n] == 0:
                    for j in range(0, len(faces)):
                        for k in range(faces_segments.shape[1]):
                            faces_segments[j + count_f][k] = faces[j][k] + count_v

                    for j in range(0, len(vertices)):
                        for k in range(vertices_segments.shape[1]):
                            vertices_segments[j + count_v][k] = vertices[j][k]

                    count_f += len(faces)
                    count_v += len(vertices)
                n += 1
            i += 1
            n = 0

        segments = trimesh.Trimesh(vertices=vertices_segments, faces=faces_segments)

        return segments

    def __step_x(self):
        return self.__x_size() / self.dmtrx.shape[0]

    def __step_y(self):
        return self.__y_size() / self.dmtrx.shape[1]

    def __x_size(self):
        return self.dmtrx.shape[0] * self.size_3d[0]

    def __y_size(self):
        return self.dmtrx.shape[1] * self.size_3d[0]

