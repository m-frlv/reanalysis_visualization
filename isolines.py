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

    def get_geojsons(self):
        data_grids = self.__datagrid.get_data_grids()
        result = []
        for data_grid in data_grids:
            X = data_grid['X']
            Y = data_grid['Y']
            Z = data_grid['Z']

            if self.__method == 'Изолинии':
                contour = pylab.contour(
                    X, Y, Z, cmap=self.__create_colourmap())
                result.append({
                    'geojson': geojsoncontour.contour_to_geojson(contour, stroke_width=0.5),
                    'leadTime': data_grid['leadTime']
                })
            if self.__method == 'Контур с подписями':
                contourf = pylab.contourf(
                    X, Y, Z, cmap=self.__create_colourmap())
                result.append({
                    'geojson': geojsoncontour.contourf_to_geojson(contourf, stroke_width=0.5),
                    'leadTime': data_grid['leadTime']
                })
        return result
