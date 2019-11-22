from configparser import ConfigParser
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import math
import sys

from Coordinate import Coordinate


class SierpinskiTetrahedron:
    def __init__(self):
        """
        Инициализация класса SierpinskiTetrahedron для отображения 3D - модели пирамиды Серпинского
        """
        # загружаем конфигурационный файл
        self.config = ConfigParser()
        self.config.read("config.ini")
        # список фигур - объектов класса GLMeshItem
        self.meshes = list()
        # степень рекурсии - при нуле строится обычная пирамида
        self.recursion_rate = self.config.getint("recurse", "recursion_rate") * 4 + 1
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
        # достаем из конфига координаты начала и толщину линии
        coordinate = Coordinate(self.config.getint("tetrahedron", "x"), self.config.getint("tetrahedron", "y"),
                                self.config.getint("tetrahedron", "z"))
        # запускаем рекурсию
        self.build_recursive(coordinate, self.config.getint("tetrahedron", "side"))
        # отрисовываем каждую фигуру на графике
        for mesh in self.meshes:
            self.widget.addItem(mesh)
        # отображаем виджет
        self.widget.show()

    def build_recursive(self, coordinate: Coordinate, side: int):
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
        colors = np.array([
            [1, 0, 0, 1.0],
            [0, 1, 0, 1.0],
            [0, 0, 1, 1.0],
            [1, 1, 0, 1.0]
        ])
        self.recursion_rate -= 1
        if self.recursion_rate // 4 > 0:
            mesh = gl.GLMeshItem(vertexes=vertex, faces=faces, faceColors=colors, smooth=False, drawEdges=True,
                                 drawFaces=False)
            self.meshes.append(mesh)
            side /= 2
            circle_1 = Coordinate(coordinate.x - side/2, coordinate.y - math.sqrt(3) / 6 * side, coordinate.z)
            circle_2 = Coordinate(coordinate.x + side/2, coordinate.y - math.sqrt(3) / 6 * side, coordinate.z)
            circle_3 = Coordinate(coordinate.x, coordinate.y + math.sqrt(3) / 6 * side*2, coordinate.z)
            circle_4 = Coordinate(coordinate.x, coordinate.y, coordinate.z + side * math.sqrt(2/3))
            self.build_recursive(circle_1, side)
            self.build_recursive(circle_2, side)
            self.build_recursive(circle_3, side)
            self.build_recursive(circle_4, side)
        else:
            mesh = gl.GLMeshItem(vertexes=vertex, faces=faces, faceColors=colors, smooth=False, drawEdges=True, drawFaces=True)
            self.meshes.append(mesh)

    @staticmethod
    def get_coordinates(coordinate: Coordinate, side: float) -> tuple:
        """
        Вычисляет координаты точек сторон для отрисоки пирамиды
        :param coordinate: Координаты вписанной в основание пирамиды окружности
        :param side: Длина стороны
        :return: Кортеж массивов точек для отрисовки
        """
        # вычисляем координаты вершин пирамиды
        A = Coordinate(coordinate.x - side / 2, coordinate.y - math.sqrt(3) / 6 * side, coordinate.z)
        B = Coordinate(coordinate.x, coordinate.y + math.sqrt(3) / 3 * side, coordinate.z)
        C = Coordinate(coordinate.x + side/2, coordinate.y - math.sqrt(3) / 6 * side, coordinate.z)
        D = Coordinate(coordinate.x, coordinate.y, coordinate.z + math.sqrt(2 / 3) * side)
        # получаем координаты точек для сторон пирамиды
        return A, B, C, D

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, points, color, width):
        self.traces[name].setData(pos=points, color=color, width=width)

    def update(self):
        self.set_plotdata(0, points=np.array([0, 10, 0]), color=pg.glColor(0, 83, 138), width=10.0)

    def animation(self):
        timer = QtCore.QTimer()
        # timer.timeout.connect(self.update)
        timer.start(20)
        self.start()


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    tetrahedron = SierpinskiTetrahedron()
    tetrahedron.animation()