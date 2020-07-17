import requests
import json
import pandas as pd
from scipy.ndimage.filters import gaussian_filter
import numpy as np


class DataGrid:
    def __init__(self, params, variables):
        self.params = params
        self.variables = variables
        self.__prepare_data(self.__query())

    def get_data_grid(self):
        return self.X, self.Y, self.Z

    def __query(self):
        url = 'http://92.50.219.104:8503/api/NWP/region'
        response = requests.post(
            url, params=self.params, json=self.variables)
        response.raise_for_status()

        return response.json()

    def __prepare_data(self, response):
        data = {
            'lat': [],
            'lon': [],
            'val': []
        }

        for row in response:
            if not np.isnan(float(row['values'][0][0])):
                data['lat'].append(row['latGrd'])
                data['lon'].append(row['lonGrd'])
                data['val'].append(row['values'][0][0])

        data = pd.DataFrame(data)
        self.Z = data.pivot_table(
            index='lon', columns='lat', values='val').T.values

        sigma = 1
        self.Z = gaussian_filter(self.Z, sigma)
        X = np.sort(data.lon.unique())
        Y = np.sort(data.lat.unique())

        self.X, self.Y = np.meshgrid(X, Y)
