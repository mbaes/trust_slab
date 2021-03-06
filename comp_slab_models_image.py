#!/usr/bin/env python
#
# Code to make plots for comparing the images
# for the TRUST BM1 Slab benchmark
#
# Written by: Karl Gordon (kgordon@stsci.edu)
#
# 23 Jul 2015 - written
#
import os.path
import argparse

import numpy as np
import matplotlib.pyplot as pyplot
import matplotlib.gridspec as gridspec
from matplotlib.colors import LogNorm

from astropy.io import fits

def plot_imagegrid(modnames, moddisplaynames, wave, tau, angle, 
                   save_eps=False, save_png=False):

    # generate the filename
    ifilenames = [modname + '_t' + tau + '_i' + angle + 'a000_w' + wave + '.fits'
                 for modname in modnames]
    n_orig_files = len(ifilenames)

    # check all the files exisit, adjust if not
    filenames = []
    displaynames = []
    fileindxs = []
    for i, cfile in enumerate(ifilenames):
        if os.path.isfile(cfile):
            filenames.append(cfile)
            displaynames.append(moddisplaynames[i])
            fileindxs.append(i)
    n_files = len(filenames)

    if n_files == 0:
        print('no files present')
        print(ifilenames)
        exit(0)
    
    # plot information
    fig_label = r'Slab, $\tau (1 \mu m)$ = '+tau+r', $\theta$ = ' + angle + ', $\lambda$ = ' + wave
    symtype = ['b-','g-','r-','c-','m-','y-','k-']
    total_symtype = ['k-','b--','b:','r--','r:','b--']
    fontsize = 12

    # setup figure
    fig, ax = pyplot.subplots(figsize=(10,10))

    # use gridspec to allow for one plot to be larger than the others
    # may do this later
    gs = gridspec.GridSpec(3, 4, width_ratios=[1.,1.,1.0,0.15])
    ax = []
    for i in range(n_files):
        ax.append(pyplot.subplot(gs[divmod(fileindxs[i],3)]))

    # read in the results from each model
    for i, cfile in enumerate(filenames):

        # read in the image
        timage = np.squeeze(fits.getdata(cfile))

        if displaynames[i] in ['CRT','SOC']:
            timage = np.rot90(timage,3)

        if timage.shape[0] == 300:
            timage = timage[9:260,45:255]
        elif timage.shape[0] == 600:
            timage = timage[19:520,90:510]

        # save the image in a cube
        if i == 0:
            all_images = np.empty((timage.shape[0],timage.shape[1],n_files))
            minmax_vals = np.empty((n_files,2))
        all_images[:,:,i] = timage

        # save the min/max values for determing the overall min/max plotting values
        gindxs = np.where((timage[:] > 0.) & (timage[:] < np.max(timage[:])))
        if len(gindxs[0]) > 0:
            minmax_vals[i,0] = np.min(timage[gindxs])
            minmax_vals[i,1] = np.max(timage[gindxs])
        else:
            print(i,cfile,' has no positive values')

    # get the min/max to plot
    gindxs, = np.where(minmax_vals[:,0] > 0)
    plot_minmax = [np.median(minmax_vals[gindxs,0]),np.median(minmax_vals[gindxs,1])]

    for i in range(n_files):
        cur_cax = ax[i].imshow(all_images[:,:,i],norm=LogNorm(vmin=plot_minmax[0],vmax=plot_minmax[1]), origin='lower')#,
#                               cmap=pyplot.get_cmap('cubehelix'))
        ax[i].set_title(displaynames[i],fontsize=fontsize)
        ax[i].get_xaxis().set_visible(False)
        ax[i].get_yaxis().set_visible(False)

    # add the overall label
    fig.text (0.5, 0.99, fig_label, horizontalalignment='center',
              verticalalignment='top',fontsize=1.5*fontsize)

    # colorbar
    fig.colorbar(cur_cax, cax=(pyplot.subplot(gs[0:3,3])))
    
    # optimize the figure layout
    gs.tight_layout(fig, rect=[0, 0.03, 1, 0.96])

    # display the plot
    save_name =  'slab_t' + tau + '_i' + angle + '_w' + wave + '_image_comp'
    
    if save_png:
        fig.savefig(save_name+'.png')
        fig.savefig(save_name+'_small.png',dpi=13)
    elif save_eps:
        fig.savefig(save_name+'.eps')
    else:
        pyplot.show()

    pyplot.close(fig)

if __name__ == "__main__":

    good_angles = ['000','030','060','090','120','150','180','all']
    good_taus = ['1e-2','1e-1','1e0','1e1','all']
    good_waves = ['000.15','000.53','035.11','151.99','all']

    # commandline parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--wave", choices=good_waves, default='000.53',
                        help="wavelength to display")
    parser.add_argument("-t", "--tau", choices=good_taus, default='1e0', 
                        help="Optical depth of model run")
    parser.add_argument("-a", "--angle", choices=good_angles, default='090',
                        help="Viewing angle of model run")
    parser.add_argument("--econs", action="store_true",
                        help="energy conservation convergence (special DIRTY runs) [default=False]")
    parser.add_argument("--mscat", action="store_true",
                        help="max scat convergence (special DIRTY runs) [default=False]")
    parser.add_argument("--nphot", action="store_true",
                        help="nphot convergence (special DIRTY runs) [default=False]")
    parser.add_argument("--stau", action="store_true",
                        help="subdivision tau for clumps (special DIRTY runs) [default=False]")
    parser.add_argument("--nz", action="store_true",
                        help="number of grid cells in the z direction (special SKIRT runs) [default=False]")
    parser.add_argument("--wr", action="store_true",
                        help="minimum weight reduction (special SKIRT runs) [default=False]")
    parser.add_argument("--minfs", action="store_true",
                        help="minimum number of forced scattering events (special SKIRT runs) [default=False]")
    parser.add_argument("-e", "--eps", help="Save the plot as an encapsulated file",
                        action="store_true")
    parser.add_argument("-p", "--png", help="Save the plot as a portable network graphics file",
                        action="store_true")
    args = parser.parse_args()

    # check if 'all' then set to full set
    angles = [args.angle]
    if 'all' in angles:
        angles = good_angles[0:len(good_angles)-1]

    taus = [args.tau]
    if 'all' in taus:
        taus = good_taus[0:len(good_taus)-1]

    waves = [args.wave]
    if 'all' in waves:
        waves = good_waves[0:len(good_waves)-1]

    # models to display
    if args.stau:
        moddisplaynames = ['DIRTY (Nz=400)','DIRTY (Nz=200)','DIRTY (Nz=100)','DIRTY (Nz=50)',
                           'DIRTY (Nz=10)','DIRTY (Nz=6)','DIRTY (Nz=3)']
        #moddisplaynames = ['DIRTY (stau=0.0025)','DIRTY (stau=0.005)','DIRTY (stau=0.01)','DIRTY (stau=0.05)',
        #                   'DIRTY (stau=0.1)','DIRTY (stau=0.25)','DIRTY (stau=1.0)']
        modnames = ['dirty_stau_0.00250','dirty_stau_0.00500','dirty_stau_0.01000','dirty_stau_0.05000',
                    'dirty_stau_0.10000','dirty_stau_0.25000','dirty_stau_1.00000']
        imodnames = ['dirty_stau/' + modname + '_slab_eff' for modname in modnames]
        scomp = 0
    elif args.nphot:
        moddisplaynames = ['DIRTY (N=3.2e7)','DIRTY (N=1e7)','DIRTY (N=3.2e6)','DIRTY (N=1e6)','DIRTY (N=3.2e5)']
        modnames = ['dirty_nphot_3.2e7','dirty_nphot_1e7','dirty_nphot_3.2e6','dirty_nphot_1e6','dirty_nphot_3.2e5']
        imodnames = ['dirty_nphot/' + modname + '_slab_eff' for modname in modnames]
        scomp = 0
    elif args.mscat:
        moddisplaynames = ['DIRTY (mscat=5)','DIRTY (mscat=1)']
        modnames = ['dirty_mscat_5','dirty_mscat_1']
        imodnames = ['dirty_mscat/' + modname + '_slab_eff' for modname in modnames]
        scomp = 0
    elif args.econs:
        moddisplaynames = ['DIRTY (econs=0.001)','DIRTY (econs=0.0032)','DIRTY (econs=0.01)','DIRTY (econs=0.032)',
                           'DIRTY (econs=0.1)','DIRTY (econs=0.32)','DIRTY (econs=1.0)']
        modnames = ['dirty_econs_0.001','dirty_econs_0.0032','dirty_econs_0.01','dirty_econs_0.032',
                    'dirty_econs_0.1','dirty_econs_0.32','dirty_econs_1.0']
        imodnames = ['dirty_econs/' + modname + '_slab_eff' for modname in modnames]
        scomp = 0
    elif args.nz:
        moddisplaynames = ['SKIRT (Nz=400)','SKIRT (Nz=200)','SKIRT (Nz=100)','SKIRT (Nz=30)','SKIRT (Nz=10)','SKIRT (Nz=5)']
        modnames = ['skirtnz400','skirtnz200','skirtnz100','skirtnz030','skirtnz010','skirtnz005']
        imodnames = ['skirtnz/' + modname + '_slab_eff' for modname in modnames]
        scomp = 0
    elif args.wr:
        moddisplaynames = ['SKIRT (wr=1e8)','SKIRT (wr=1e7)','SKIRT (wr=1e6)','SKIRT (wr=1e5)','SKIRT (wr=1e4)','SKIRT (wr=1e3)']
        modnames = ['skirtwr1e8','skirtwr1e7','skirtwr1e6','skirtwr1e5','skirtwr1e4','skirtwr1e3']
        imodnames = ['skirtwr/' + modname + '_slab_eff' for modname in modnames]
        scomp = 0
    elif args.minfs:
        moddisplaynames = ['SKIRT (minfs=1)','SKIRT (minfs=3)','SKIRT (minfs=10)','SKIRT (minfs=30)',
                           'SKIRT (minfs=100)','SKIRT (minfs=200)','SKIRT (minfs=400)']
        modnames = ['skirtminfs001wr1e7','skirtminfs003wr1e7','skirtminfs010wr1e7','skirtminfs030wr1e7',
                    'skirtminfs100wr1e7','skirtminfs200wr1e7','skirtminfs400wr1e7']
        imodnames = ['skirtminfs/' + modname + '_slab_eff' for modname in modnames]
        scomp = 0
    else:
        moddisplaynames = ['CRT','DART-ray','DIRTY','Hyperion','SKIRT','SOC','TRADING']
        #modnames = ['crt','dirty_stau_0.00250','hyper','skirt','SOC','tradi']
        modnames = ['crt','dartr','dirty','hyper','skirt','SOC','tradi']
        scomp = -1

        imodnames = [modname + '/' + modname + '_slab_eff'
                     for modname in modnames]

    for angle in angles:
        for tau in taus:
            for wave in waves:
                plot_imagegrid(imodnames, moddisplaynames, wave, tau, angle,
                               save_eps=args.eps, save_png=args.png)
