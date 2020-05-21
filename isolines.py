import pandas as pd
import numpy as np
import pylab


class Isolines(object):
    def __init__(self, csv_path):
        X, Y, Z = self.__prepare_data(csv_path)
        contour = pylab.contour(X, Y, Z)
        pylab.clabel(contour, fmt='x=%.2f')

        pylab.show()


    def __prepare_data(sels, csv_path):
        contour_data = pd.read_csv(csv_path, sep=';')
        contour_data.head()

        Z = contour_data.pivot_table(index='lon', columns='lat', values='val').T.values

        X_unique = np.sort(contour_data.lon.unique())
        Y_unique = np.sort(contour_data.lat.unique())
        X, Y = np.meshgrid(X_unique, Y_unique)
        print(Z)
        return X, Y, Z

    def draw_isolines(self):
        pass