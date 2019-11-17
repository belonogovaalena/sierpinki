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
        # получаем массивы точек для отрисовки
        items = self.draw_tetrahedron(coordinate, self.config.getint("tetrahedron", "side"))
        # и отображаем каждую линию
        for i in range(len(items)):
            self.traces[i] = gl.GLLinePlotItem(pos=items[i], color=pg.glColor(0, 83, 138, 255), width=10.0, antialias=True)
            self.widget.addItem(self.traces[i])
        # отображаем виджет
        self.widget.show()

    def draw_tetrahedron(self, coordinate: Coordinate, side: float) -> tuple:
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
        AB = self._get_points_by_tops(A, B)
        BC = self._get_points_by_tops(B, C)
        CA = self._get_points_by_tops(C, A)
        AD = self._get_points_by_tops(A, D)
        BD = self._get_points_by_tops(B, D)
        CD = self._get_points_by_tops(C, D)
        return AB, BC, CA, AD, BD, CD

    def _get_points_by_tops(self, lower_point: Coordinate, upper_point: Coordinate):
        """
        Вычисляет координаты точек стороны по двум вершинам треугольника
        :param lower_point: Вершина треугольника
        :param upper_point: Вершина треугольника
        :return: Массив точек для отрисовки
        """
        x_line = np.linspace(lower_point.x, upper_point.x, 2)
        y_line = np.linspace(lower_point.y, upper_point.y, 2)
        z_line = np.linspace(lower_point.z, upper_point.z, 2)
        line = np.vstack([x_line, y_line, z_line]).transpose()
        return line

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