from configparser import ConfigParser
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np
import math
import sys

from Coordinate import Coordinate


class SierpinskiTetrahedron:
    def __init__(self):
        """
        Инициализация класса SierpinskiTetrahedron для отображения 3D - модели пирамиды Серпинского
        """
        # загружаем конфигурационный файл и читаем его
        self.config = ConfigParser()
        self.config.read("config.ini")
        # список пирамид - объектов класса GLMeshItem
        self.meshes = list()
        # глубина рекурсии - при нуле строится обычная пирамида
        self.recursion_rate = self.config.getint("recurse", "recursion_rate")
        # инициализируем базовый класс QApplication библиотеки PyQt5, передавая аргументом путь к файлу .py
        self.application = QtGui.QApplication(sys.argv)
        # создаем базовый виджет библиотеки PyOpenGL для отображения 3D - модели
        self.widget = gl.GLViewWidget()
        # устанавливаем значения расстояниия от камеры до центра
        self.widget.opts['distance'] = self.config.getint("widget", "distance")
        # устанавливаем заголовок окна
        self.widget.setWindowTitle('Пирамида Серпинского')
        # устанавливаем положение окна и размеры окна
        self.widget.setGeometry(self.config.getint("widget", "xposition"), self.config.getint("widget", "yposition"),
                                self.config.getint("widget", "width"), self.config.getint("widget", "height"))

        # создаем координатные плоскости
        # плоскость Z0Y
        z0y = gl.GLGridItem()
        # поворачиваем плоскость на 90 градусов вдоль оси Y
        z0y.rotate(90, 0, 1, 0)
        # перемещаем плоскость вдоль оси X
        z0y.translate(-10, 0, 0)
        # добавляем плоскость к виджету
        self.widget.addItem(z0y)

        # плоскость Z0X
        z0x = gl.GLGridItem()
        # поворачиваем плоскость на 90 градусов вдоль оси X
        z0x.rotate(90, 1, 0, 0)
        # перемещаем плоскость вдоль оси Y
        z0x.translate(0, -10, 0)
        # добавляем плоскость к виджету
        self.widget.addItem(z0x)

        # плоскость X0Y
        x0y = gl.GLGridItem()
        # перемещаем плоскость вдоль оси Z
        x0y.translate(0, 0, -10)
        # добавляем плоскость к виджету
        self.widget.addItem(x0y)
        self.traces = dict()
        # достаем из конфига координаты центра пирамиды - он же центр вписанной в основание окружности
        coordinate = Coordinate(self.config.getint("tetrahedron", "x"), self.config.getint("tetrahedron", "y"),
                                self.config.getint("tetrahedron", "z"))
        # запускаем рекурсию для построения пирамиды Серпинского
        self.build_recursive(coordinate, self.config.getint("tetrahedron", "side"))
        # отрисовываем каждую фигуру на графике
        for mesh in self.meshes:
            self.widget.addItem(mesh)
        # отображаем виджет
        self.widget.show()

    def build_recursive(self, coordinate: Coordinate, side: int):
        """
        Рекурсивная функция для построения пирамиды Серпинского
        :param coordinate: кордината центра вписанной окружности в основание пирамиды
        :param side: длина стороны пирамиды
        """
        # получаем массивы точек для отрисовки
        points = self.get_coordinates(coordinate, side)
        # точки A, B, C, D
        vertex = np.array([
            [points[0].x, points[0].y, points[0].z],
            [points[1].x, points[1].y, points[1].z],
            [points[2].x, points[2].y, points[2].z],
            [points[3].x, points[3].y, points[3].z],
        ])
        # создаем грани ABC, ABD, ACD, BCD
        faces = np.array([
            [0, 1, 2],
            [0, 1, 3],
            [0, 2, 3],
            [1, 2, 3]
        ])
        # раскрашиваем их в цвета
        colors = np.array([
            [1, 0, 0, 1.0],
            [0, 1, 0, 1.0],
            [0, 0, 1, 1.0],
            [1, 1, 0, 1.0]
        ])
        # если пирамиды достаточной глубины рекурсии не построены - строим их незакрашенными
        if self.recursion_rate > 0:
            self.recursion_rate -= 1
            mesh = gl.GLMeshItem(vertexes=vertex, faces=faces, faceColors=colors, smooth=False, drawEdges=True,
                                 drawFaces=False)
            # добавляем незакрашенную верхнеуровневую пирамиду-каркас к списку пирамиид
            self.meshes.append(mesh)
            # строим четыре пирамиды внутри каркаса
            side /= 2
            # находим координаты окружностей, вписанных в непоспостроенные пока еще пирамиды внутри каркаса
            circle_1 = Coordinate(coordinate.x - side/2, coordinate.y - math.sqrt(3) / 6 * side, coordinate.z)
            circle_2 = Coordinate(coordinate.x + side/2, coordinate.y - math.sqrt(3) / 6 * side, coordinate.z)
            circle_3 = Coordinate(coordinate.x, coordinate.y + math.sqrt(3) / 6 * side*2, coordinate.z)
            circle_4 = Coordinate(coordinate.x, coordinate.y, coordinate.z + side * math.sqrt(2/3))
            # для каждой пары - координаты окружности/деленная пополам длина ребра - вызываем рекурсивно функцию
            self.build_recursive(circle_1, side)
            self.build_recursive(circle_2, side)
            self.build_recursive(circle_3, side)
            self.build_recursive(circle_4, side)
            self.recursion_rate += 1
        # дошли до конца в рекурсии - красим пирамиду
        else:
            mesh = gl.GLMeshItem(vertexes=vertex, faces=faces, faceColors=colors, smooth=False, drawEdges=True, drawFaces=True)
            self.meshes.append(mesh)

    @staticmethod
    def get_coordinates(coordinate: Coordinate, side: float) -> tuple:
        """
        Вычисляет координаты вершины пирамиды
        :param coordinate: Координаты вписанной в основание пирамиды окружности
        :param side: Длина стороны
        :return: Кортеж массивов точек для отрисовки
        """
        # вычисляем координаты вершин пирамиды
        A = Coordinate(coordinate.x - side / 2, coordinate.y - math.sqrt(3) / 6 * side, coordinate.z)
        B = Coordinate(coordinate.x, coordinate.y + math.sqrt(3) / 3 * side, coordinate.z)
        C = Coordinate(coordinate.x + side/2, coordinate.y - math.sqrt(3) / 6 * side, coordinate.z)
        D = Coordinate(coordinate.x, coordinate.y, coordinate.z + math.sqrt(2 / 3) * side)
        return A, B, C, D

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()


if __name__ == '__main__':
    tetrahedron = SierpinskiTetrahedron()
    tetrahedron.start()
