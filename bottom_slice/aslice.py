import pandas as pd
import numpy as np
import re


class AlphaSlice:

    def __init__(self, fname):

        self.data = self._load_slice(fname)
        
        # * parse dx
        name_bits = fname.split('_')
        dx_bits = [nbit for nbit in name_bits if 'dx' in nbit]
        if len(dx_bits) > 0:
            dx = re.findall(r'\d+', dx_bits[0])
            self.dx = int(dx[0])
        else:
            self.dx = 8


    def _load_slice(self, filename):
        # df = pd.read_csv(filename, header=0, names=['x','y','z','u','v','w','alpha'])

        if 'ns' in filename:
            df = pd.read_csv(filename, header=0, 
                         names=['alpha','x','y','z','u','v','w','FD','eta','eta_2d','d_eta'])
        else:
            df = pd.read_csv(filename, header=0, 
                            names=['alpha','x','y','z','u','v','w','FD','F2D','eta','eta_2d','d_eta'])
        # df = df.set_index(['x','z'])

        return df
    

    def isolate_valid_entries(self):
        # * want only entries where U > c_2D
        c2d = np.sqrt(9.81/(np.pi/self.dx))
        
        self.data = self.data[self.data['u'] - c2d > 0]

    

    def calc_stats(self):
        self.frac_0 = (self.data['alpha'] < 1e-6).sum() / len(self.data['alpha'])
        self.frac_nan = (self.data['alpha'] == 1e-7).sum() / len(self.data['alpha'])
        self.frac_nobin = (self.data['alpha'] == 1.5e-7).sum() / len(self.data['alpha'])