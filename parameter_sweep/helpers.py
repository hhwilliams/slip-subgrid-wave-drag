from matplotlib import pyplot as plt
from matplotlib import pylab as pl
import matplotlib as mpl
import cmcrameri.cm as cmc
from matplotlib import rcParams
import numpy as np
import pandas as pd
from scipy.io import loadmat

import sys
sys.path.insert(0, "../sliptools")
from statData import StatData

nu = 1.8e-5


def make_statlist(caseids, ids, case_info):
    time_window = [0,10]
    dirname = ''

    statlist = {}
    for id, case in zip(ids, caseids):
            casename = case.split('/')[0]
            cinf = case_info.loc[casename]
            stat_params = cinf.to_dict()
            fname = dirname+casename+'.txt'
            statlist[id] = StatData(fname, ustar=stat_params['ustar_mean'])
            # statlist[id] = StatData.PVstat(id, case, params=stat_params, dirname=dirname, 
            #                             time_index=1, time_window=time_window,
            #                             save_mean=False, read_save=True)
    
    return statlist


def plot_velocity(stats, ids, colors, linestyle='-', axs=[], labels=True):
    if len(axs) == 0:
        fig, axs = plt.subplots(1,2,facecolor='w', dpi=180.0, tight_layout=True, figsize=(8,4))

    for i in range(len(ids)):
        id = ids[i]
        u = stats[id].data['U']
        y = stats[id].data['ym']

        if labels:
            axs[0].plot(u, y, lw=2, color=colors[i], ls=linestyle, label=id)
        else:
            axs[0].plot(u, y, lw=2, color=colors[i], ls=linestyle)
        
        # * viscous scaling
        ustar = stats[id].ustar
        H = 1000

        axs[1].plot(y[1:]/H, u[1:]/ustar, marker='.', ls=linestyle,
                    color=colors[i], label=id)
        
        # * some checks
        print(ids[i])
        # print('U_bulk: {:.1f}'.format(stats[id].bulk_vel()))
        # print('U(1000): {:.1f}\n'.format(stats[id].Uz(1000)))
        print('U(20): {:.1f}\n'.format(stats[id].Uz(20)))


    axs[0].set_ylim((0,1000))
    axs[0].set_xlabel('U (m/s)')
    axs[0].set_ylabel('y (m)')

    if labels:
        axs[0].legend()

    axs[1].set_ylabel(r'$\langle \overline{u}\rangle/u_\ast$')
    axs[1].set_xlabel(r'$y/H$')
    axs[1].set_xscale('log')
    axs[1].set_xlim((1e-3, 1))

    # return fig, axs



def plot_reynolds(stats, ids, colors, linestyle='-', fig=None, axs=None, labels=True):
    if not fig:
        fig, axs = plt.subplots(2, 3, facecolor='w', dpi=180, constrained_layout=True,
                                figsize=(10,6), sharey=True)

    plot_ids = ['up_up','vp_vp','wp_wp','up_vp','up_wp','vp_wp']
    plot_labels = [r"$\langle u'u'\rangle$", r"$\langle v'v'\rangle$",
                r"$\langle w'w'\rangle$", r"$\langle u'v'\rangle$",
                r"$\langle u'w'\rangle$", r"$\langle v'w'\rangle$"]
    
    for j in range(len(plot_ids)):
        axi = int(j/3)
        axj = j%3

        for i in range(len(ids)):
            id = ids[i]

            if labels:
                axs[axi,axj].plot(stats[id].data[plot_ids[j]],stats[id].data['ym'],
                        lw=1.2, color=colors[i], ls=linestyle, label=id)
            else:
                axs[axi,axj].plot(stats[id].data[plot_ids[j]],stats[id].data['ym'],
                    lw=1.2, color=colors[i], ls=linestyle)
            
        if axj == 0:   
            axs[axi,axj].set_ylabel(r'$y$')
        axs[axi,axj].set_title(plot_labels[j])

        axs[axi,axj].set_ylim((0,1000))

    axs[0,0].legend()


def plot_upvp(stats, ids, colors, ax=False, labels=True):
    if not ax:
        fig, ax = plt.subplots(1,1, facecolor='w', dpi=180, figsize=(5.2,4.6))

    for i in range(len(ids)):
        id = ids[i]
        ax.plot(stats[id].data['up_vp'], stats[id].data['y'],
                lw=2, color=colors[i], label=id)
    
    ax.set_xlabel(r"$\langle u'v' \rangle$ (m$^2$/s$^2$)")
    ax.set_ylabel(r'$y$ (m)')
    
    ax.set_ylim((0,1000))

    if labels:
        ax.legend()


def coare_plot_starter(figsize, Romero_colorby='none', Romero_cmap='none'):

    # * COARE 3.5 formula
    ncoare = 500
    u10_coare = np.linspace(1,20,ncoare)
    ustar_coare = np.empty(ncoare)

    for i in range(ncoare):
        if u10_coare[i] < 4:
            ustar_coare[i] = 0.03 * u10_coare[i]
        elif u10_coare[i] < 9.6:
            ustar_coare[i] = 0.035 * u10_coare[i] - 0.005*4
        else:
            # ustar_coare[i] = 0.058 * u10_coare[i] - 0.24 # Andreas et al. (2012)
            ustar_coare[i] = 0.062 * u10_coare[i] - 0.28

    fig, ax = plt.subplots(1,1,facecolor='w', dpi=180.0,tight_layout=True, figsize=figsize)

    # * Edson
    ed = loadmat('ext_data/TauDataEdson.mat')
    plt.scatter(ed['U10Nalex'], np.sqrt(ed['TAUalex']/1.2), s=10, marker='x', lw=1,
                color='gainsboro', label='Edson et al. 2013', zorder=1)
    plt.plot(u10_coare,ustar_coare,'k',lw=2.5,label='COARE 3.5 (Edson et al. 2013)', zorder=2)

    # * Romero
    rom = pd.read_csv('ext_data/romero.csv', header=0, sep=' ',index_col=False)
    rom['hs'] = 4*np.sqrt(rom['eta_sq'])
    rom['kphs'] = rom['hs']*rom['kp']

    if Romero_colorby == 'none':
        ax.scatter(rom['U10'],rom['ustar'],c='black',
                   s=5,label='Romero and Melville 2010',zorder=2)
    elif Romero_colorby == 'hs':
        rsc = ax.scatter(rom['U10'],rom['ustar'],c=rom['hs'],
                            cmap=Romero_cmap, vmin=0, vmax=4,
                            s=5,label='Romero and Melville 2010',zorder=2)
        plt.colorbar(rsc, label=r'$H_s$ (m)')
    elif Romero_colorby == 'kphs':
        rsc = ax.scatter(rom['U10'],rom['ustar'],c=rom['kphs'],
                            cmap=Romero_cmap, vmin=0, vmax=0.3,
                            s=5,label='Romero and Melville 2010',zorder=2)
        plt.colorbar(rsc, label=r'$k_pH_s$')

    ax.set_xlabel(r'$U_{10}$ (m/s)')
    ax.set_ylabel(r'$u_*$ (m/s)')

    ax.legend()

    ax.set_xlim((0,21.0))
    ax.set_ylim((0,1.2))

    return fig, ax

    
def z0(U10, ustar):
    kappa = 0.4
    z0 = 10 / np.exp(U10*kappa/ustar)
    return z0