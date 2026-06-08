import numpy as np
import pandas as pd

class EdsonData:

    def __init__(self):

        fpreamble = 'ext_data/edson_data/edson_'
        tags = ['high','med_high','med_low','low']
        self.data = {}

        for i in range(4):
            df = pd.read_csv(fpreamble+tags[i]+'.csv', header=0, names=['us', 'u10'])
            df = df.sort_values('us')

            self.data[tags[i]] = df
            # print(df)


    def fill_outer_region(self, ax, out_col='whitesmoke'):

        x1 = list(self.data['low'].us)
        y1 = list(self.data['low'].u10)
        x2 = list(self.data['high'].us)
        y2 = list(self.data['high'].u10)

        xfill = np.sort(np.concatenate([x1, x2]))
        y1fill = np.interp(xfill, x1, y1)
        y2fill = np.interp(xfill, x2, y2)
        
        ax.plot(x1, y1, color=out_col, zorder=0)
        ax.plot(x2, y2, color=out_col, zorder=0)
        ax.fill_between(xfill, y1fill, y2fill, color=out_col, zorder=0)



    def fill_med_region(self, ax, med_col='gainsboro'):

        x1 = list(self.data['med_low'].us)
        y1 = list(self.data['med_low'].u10)
        x2 = list(self.data['med_high'].us)
        y2 = list(self.data['med_high'].u10)

        xfill = np.sort(np.concatenate([x1, x2]))
        y1fill = np.interp(xfill, x1, y1)
        y2fill = np.interp(xfill, x2, y2)
        
        ax.plot(x1, y1, color=med_col, zorder=1)
        ax.plot(x2, y2, color=med_col, zorder=1)
        ax.fill_between(xfill, y1fill, y2fill, color=med_col, zorder=1)




