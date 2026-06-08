import pandas as pd
import numpy as np

class StatData:

    def __init__(self, fname, dirname='data', ustar=1):
        self.data = pd.read_csv(dirname+'/'+fname, sep='\s+', header=0)

        # self.ym = self.data['ym']
        # self.U = self.data['U']
        # self.upvp = self.data['UV'] - self.data['U']*self.data['V']

        self.ustar = ustar

        self._calc_reynolds_stresses()


    def _calc_reynolds_stresses(self):
        self.data['up_up'] = self.data['U^2'] - self.data['U']*self.data['U']
        self.data['vp_vp'] = self.data['V^2'] - self.data['V']*self.data['V']
        self.data['wp_wp'] = self.data['W^2'] - self.data['W']*self.data['W']
        self.data['up_vp'] = self.data['UV'] - self.data['U']*self.data['V']
        self.data['up_wp'] = self.data['UW'] - self.data['U']*self.data['W']
        self.data['vp_wp'] = self.data['VW'] - self.data['V']*self.data['W']



    def flux_ustar(self, y):
        if len(y) > 1:
            # data_at_y = self.data.where((self.data['ym'] >= y[0]) & (self.data['ym'] <= y[1]))

            idx1 = (self.data['y']-y[0]).abs().idxmin()
            idx2 = (self.data['y']-y[1]).abs().idxmin()
            data_at_y = self.data.loc[idx1:idx2]
            data_at_y = data_at_y.mean()
        else:
            # data_at_y = self.data.sel(ym=y, method='nearest')
            idx = (self.data['y']-y).abs().idxmin()
            data_at_y = self.data.loc[idx]

        flux = data_at_y['UV'] - data_at_y['U']*data_at_y['V']
        ustar = (-flux)**(0.5)
        return ustar
    

    def Uz(self, z):
        # * isolate 2 points closest to y
        # dy = (ym[2]-ym[1])

        # * get index of nearest y (vertical)
        idx1 = (self.data['y']-z).abs().idxmin()
        data1 = self.data.loc[idx1]
        # print(data1)
        y1 = data1['y']

        # * figure out what local dy is
        ym = self.data['y']
        dy = (ym[idx1]-ym[idx1-1])

        # * if this is the correct location, just return
        tol = 1e-2
        if y1 - z < tol:
            return data1['U']
        
        # * find y2 based on direction of interpolation
        y2 = y1 + np.sign(z-y1) * dy
        print(y1, y2)

        idx2 = (self.data['y']-y2).abs().idxmin()
        data2 = self.data.loc[idx2]

        # print(data1['U'])
        u1 = data1['U']#.to_numpy()
        u2 = data2['U']#.to_numpy()

        # * interpolate
        if y2 == y1:
            uz = u1
        else:
            uz = u1 + (z-y1)*(u2-u1)/(y2-y1)

        return uz

    def bulk_vel(self):

        # self.data['Uxy'] = self.data['U'] * self.data['y']
        weighted_vel =  self.data['U'] * self.data['y']
        Ubulk = np.sum(weighted_vel.to_numpy())/np.sum(self.data['y'].to_numpy())
        # Ubulk = self.data.sum

        return Ubulk