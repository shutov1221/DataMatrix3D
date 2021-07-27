import numpy as np
import math

class Dmtrx3DSegment:

    def parallelepiped_segment(self, width, length, height, position):
        vertices = np.array([
            [-width / 2 + position[0], -length / 2 + position[1], -height / 2 + position[2]],  # 0
            [+width / 2 + position[0], -length / 2 + position[1], -height / 2 + position[2]],  # 1
            [+width / 2 + position[0], +length / 2 + position[1], -height / 2 + position[2]],  # 2
            [-width / 2 + position[0], +length / 2 + position[1], -height / 2 + position[2]],  # 3
            [-width / 2 + position[0], -length / 2 + position[1], +height / 2 + position[2]],  # 4
            [+width / 2 + position[0], -length / 2 + position[1], +height / 2 + position[2]],  # 5
            [+width / 2 + position[0], +length / 2 + position[1], +height / 2 + position[2]],  # 6
            [-width / 2 + position[0], +length / 2 + position[1], +height / 2 + position[2]]  # 7
        ])

        faces = np.array([
            [0, 3, 1],
            [1, 3, 2],
            [2, 3, 7],
            [6, 2, 7],
            [4, 7, 3],
            [3, 0, 4],
            [5, 4, 0],
            [0, 1, 5],
            [5, 1, 2],
            [5, 2, 6],
            [4, 5, 7],
            [7, 5, 6]])

        return vertices, faces

    def cylinder_segment(self, poly_num, radius, height, position):
        vertices = np.zeros(shape=(poly_num * 4, 3))
        faces = np.zeros(shape=(poly_num * 4, 3))

        for i in range(0, poly_num):
            vertices[i][0] = radius * math.cos(2 * math.pi / poly_num * i) + position[0]
            vertices[i][1] = radius * math.sin(2 * math.pi / poly_num * i) + position[1]
            vertices[i][2] = height / 2 + position[2]

            vertices[i + poly_num][0] = radius * math.cos(2 * math.pi / poly_num * i) + position[0]
            vertices[i + poly_num][1] = radius * math.sin(2 * math.pi / poly_num * i) + position[1]
            vertices[i + poly_num][2] = -height / 2 + position[2]

        for i in range(0, poly_num):
            faces[i][0] = int(i)
            faces[i][1] = int(i + poly_num)
            if i == poly_num - 1:
                faces[i][2] = int(poly_num)
            else:
                faces[i][2] = int(i + poly_num + 1)

            faces[i + poly_num][0] = int(i)
            if i == poly_num - 1:
                faces[i + poly_num][1] = int(poly_num)
                faces[i + poly_num][2] = int(0)
            else:
                faces[i + poly_num][1] = int(i + poly_num + 1)
                faces[i + poly_num][2] = int(i + 1)

        for i in range(poly_num * 2, poly_num * 3 - 2):
            faces[i][0] = 0
            faces[i][1] = i + 1 - poly_num * 2
            faces[i][2] = i + 2 - poly_num * 2

        return vertices, faces

    def hexagon_segment(self, radius, height, position):
        return self.cylinder_segment(6, radius, height, position)

    def hemisphere_segment(self, poly_num, radius, position):
        vertices = np.zeros(shape=(poly_num ** 3, 3))
        faces = np.zeros(shape=(poly_num ** 3, 3))

        y = -1

        for i in range(0, poly_num + 1):
            for j in range(0, poly_num + 1):
                vertices[i * poly_num + j][0] = radius * math.cos(2 * math.pi / poly_num * j) * math.sin(math.pi / 2 / poly_num * i) + position[0]
                vertices[i * poly_num + j][1] = radius * math.sin(2 * math.pi / poly_num * j) * math.sin(math.pi / 2 / poly_num * i) + position[1]
                vertices[i * poly_num + j][2] = radius * math.cos(math.pi / 2 / poly_num * i) + position[2]

                faces[y][0] = y + poly_num
                faces[y][1] = y + 1
                faces[y][2] = y
                faces[y + poly_num * poly_num][0] = y + 1
                faces[y + poly_num * poly_num][1] = y + poly_num
                faces[y + poly_num * poly_num][2] = y + poly_num + 1

                y += 1
            y -= 2

        return vertices, faces


