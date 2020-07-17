import pylab
import matplotlib.colors as colours
import geojsoncontour


class Isolines(object):
    base_colours = ['#3339e8', '#f54b42']

    def __init__(self, datagrid, method):
        self.__datagrid = datagrid
        self.__method = method

    def __create_colourmap(self):
        return colours.LinearSegmentedColormap.from_list('custom colourmap', self.base_colours, N=256)

    def __calculate_isolines(self):
        X, Y, Z = self.__datagrid.get_data_grid()
        contour = pylab.contour(
            X, Y, Z, cmap=self.__create_colourmap())
        return contour

    def __calculate_filled_contour(self):
        X, Y, Z = self.__datagrid.get_data_grid()
        contourf = pylab.contourf(
            X, Y, Z, cmap=self.__create_colourmap())
        return contourf

    def get_geojson(self):
        if self.__method == 'Изолинии':
            return geojsoncontour.contour_to_geojson(self.__calculate_isolines(), stroke_width=0.5)
        if self.__method == 'Контур с подписями':
            return geojsoncontour.contourf_to_geojson(self.__calculate_filled_contour(), stroke_width=0.5)
