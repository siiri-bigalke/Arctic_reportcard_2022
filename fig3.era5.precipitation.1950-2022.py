import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from scipy import stats
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point


# !!!! activate climate2.2 environment !!!!


# ---- Get coordinates from original datafile ----
pwd = '/work2/Reanalysis/ERA5/ERA5_monthly/monolevel/'+ \
                'ERA5.mon.tp.1950-2021.nc'

ds = xr.open_dataset(pwd).sel(
        latitude=slice(90, 55),
        longitude=slice(0, 360))['tp']


# ==========================
'''     Load ERA5 Data  '''
# ==========================
lon = ds.coords['longitude']
lat = ds.coords['latitude']

names = ['ond', 'jfm', 'amj', 'jas']
ndays = [92, 90, 91, 92]
seasons = []
sig = []

for i, snx in enumerate(names):
    slope = np.load('binary_files/saverage.'+snx+'theilslopes.arctic.slope.npy')
    s = slope.reshape(141, 1440) * ndays[i] * 1000 # converting to seasonal cm/decade
    seasons.append(s)

    pvalue = np.load('binary_files/saverage.'+snx+'theilslopes.arctic.pvalue.npy')
    p = pvalue.reshape(141, 1440)
    sig.append(p)


# Before plotting, add cyclic point
c_seasons = []
c_sig = []

for sdx, season in enumerate(seasons):
    print('adding cyclic point to season ', sdx)
    data, lon_c = add_cyclic_point(seasons[sdx], coord = lon)
    sigdata, lon_c = add_cyclic_point(sig[sdx], coord = lon)

    c_seasons.append(data)
    c_sig.append(sigdata)

X, Y = np.meshgrid(lon_c, lat)

print('now plotting')


# ==========================
'''     Plotting   '''
# ==========================
plt.rcParams.update({'hatch.color': 'gray'})
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.path as mpath

def plot_background(ax):
    theta = np.linspace(0, 2*np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)

    ax.set_boundary(circle, transform=ax.transAxes)
    ax.set_extent([-180, 180, 55, 90], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('110m'), linewidth=1.0)
    ax.add_feature(cfeature.BORDERS)
    return(ax)


tcrs = ccrs.PlateCarree()
pcrs = ccrs.NorthPolarStereo()
fig, ax = plt.subplots(2, 2, 
                      subplot_kw = {'projection':pcrs},
                      #constrained_layout = True,
                      figsize=(9,9))

titles = ['Autumn', 'Winter', 'Spring', 'Summer']
n = -1
for col in range(2):
    for row in range(2):
        n += 1
        plot_background(ax[col,row])
        ax[col,row].set_title(titles[n])
        cf = ax[col,row].contourf(X,Y, c_seasons[n], 
                          cmap = 'BrBG', 
                          #levels = np.arange(-1, 1.01, 0.01),
                          levels = np.arange(-4, 4.1, 0.1),
                          extend = 'both', 
                          transform=tcrs)

        cf2 = ax[col,row].contourf(X, Y, c_sig[n],
                          colors = 'none',
                          levels = [0.00,0.05], 
                          hatches = ['....'],
                          transform = tcrs)


fig.subplots_adjust(top = 0.95, 
                    bottom = 0.1,
                    left = 0.07,
                    right = 0.85,
                    hspace = 0.02,
                    wspace = 0.04)


cbar_ax = fig.add_axes([0.87, 
                        0.25, 
                        0.03, 
                        0.5])

cbar = fig.colorbar(cf, 
                    orientation='vertical',
                    cax=cbar_ax,
                    ticks = [-4, -2, 0, 2, 4])

cbar.ax.set_ylabel('Seasonal total precipitation (cm) \n trend per decade (1950-2022)')


plt.savefig('figs/saverage.arctic.preciptrend.1950-2022.era5.png', dpi=500)
plt.show()
exit()

