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

    def get_data_grids(self):
        return self.data_grids

    def __query(self):
        url = 'http://92.50.219.104:8503/api/NWP/region'
        response = requests.post(
            url, params=self.params, json=self.variables)
        response.raise_for_status()

        return response.json()

    def __prepare_data(self, response):
        data_grids = []

        i = 0

        for lead_time in self.params['leadTimes']:
            data = {
                'lat': [],
                'lon': [],
                'val': []
            }

            for row in response:
                if not np.isnan(float(row['values'][0][0])):
                    data['lat'].append(row['latGrd'])
                    data['lon'].append(row['lonGrd'])
                    data['val'].append(row['values'][i][0])

            i += 1

            data = pd.DataFrame(data)
            Z = data.pivot_table(
                index='lon', columns='lat', values='val').T.values

            sigma = 1
            Z = gaussian_filter(Z, sigma)
            X = np.sort(data.lon.unique())
            Y = np.sort(data.lat.unique())

            data_grids.append({
                'X': X,
                'Y': Y,
                'Z': Z,
                'leadTime': lead_time
            })

        self.data_grids = data_grids
