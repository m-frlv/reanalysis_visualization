import pandas as pd
import numpy as np
import pylab
import matplotlib.colors as colours
import geojsoncontour


class Isolines(object):
    base_colours = ['#3339e8', '#f54b42']

    def __init__(self, csv_path):
        self.__csv_path = csv_path

    def __prepare_data(self):
        contour_data = pd.read_csv(self.__csv_path, sep=';')
        contour_data.head()

        Z = contour_data.pivot_table(
            index='lon', columns='lat', values='val').T.values

        X_unique = np.sort(contour_data.lon.unique())
        Y_unique = np.sort(contour_data.lat.unique())
        X, Y = np.meshgrid(X_unique, Y_unique)
        return X, Y, Z

    def __create_colourmap(self):
        return colours.LinearSegmentedColormap.from_list('custom colourmap', self.base_colours, N=256)

    def __calculate_isolines(self):
        X, Y, Z = self.__prepare_data()
        contour = pylab.contour(
            X, Y, Z, cmap=self.__create_colourmap())
        return contour

    def get_geojson(self):
        return geojsoncontour.contour_to_geojson(self.__calculate_isolines(), stroke_width=0.5)
