from pylibdmtx.pylibdmtx import encode
import numpy as np


class DataMatrix:

    def __init__(self, text, size):
        self.text = text.encode('utf-8')
        self.size = size
        self.encode_data = self.__encode()
        self.datamatrix = None

    def get_datamatrix(self):
        return self.__delete_elements()

    def __encode(self):
        return encode(self.text, size=self.size)

    def __get_pixels(self):
        return self.encode_data.pixels

    def __convert_to_int(self):
        pixels = self.__get_pixels()
        return [int(bool.from_bytes(pixels[i:i + 1], 'little')) for i in range(0, len(pixels))]

    def __get_array(self):
        return np.reshape(self.__convert_to_int(), (self.encode_data.height, self.encode_data.width * 3))

    def __delete_elements(self):
        to_delete_x = []
        to_delete_y = []

        data = self.__get_array()

        for i in range(0, self.encode_data.width * 3):
            if i % (self.encode_data.width * 3 / self.__x_num()) != 0:
                to_delete_x.append(i)

        for i in range(0, self.encode_data.height):
            if i % (self.encode_data.height / self.__y_num()) != 0:
                to_delete_y.append(i)

        data = np.delete(data, to_delete_x, axis=1)
        data = np.delete(data, to_delete_y, axis=0)

        return data

    def __y_num(self):
        return int(self.size.split("x")[0]) + 4

    def __x_num(self):
        return int(self.size.split("x")[1]) + 4
