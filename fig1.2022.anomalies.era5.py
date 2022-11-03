import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from scipy import stats
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point



# ==========================
#      Load ERA5 Data  
# ==========================

pwd = '/work2/Reanalysis/ERA5/ERA5_monthly/monolevel/'+ \
                'ERA5.mon.tp.1950-2022.nc'

d = xr.open_dataset(pwd).sel(
        latitude=slice(90, 55),
        longitude=slice(0, 360))['tp'] #* 100 # convert m to mm

ds1 = d.mean('expver') # Sepetember 2022 data is ERA5T as of 10.13.2022

'''
ds1 = xr.open_dataset(pwd).sel(
        latitude=slice(90, 55),
        longitude=slice(0, 360),
        expver = 1)['tp'] * 100 # convert m to mm


ds5 = xr.open_dataset(pwd).sel(
        latitude=slice(90, 55),
        longitude=slice(0, 360),
        expver = 5)['tp'] * 100 # convert m to mm
'''



# ============================
#      Composite Analysis 
# ============================

# 1991 - 2020 Climatology

climo = ds1.sel(time = slice('1991', '2020'))
ondC = climo[climo.time.dt.month.isin([10,11,12])].mean('time') * 100 * 92
jfmC = climo[climo.time.dt.month.isin([1,2,3])].mean('time') * 100 * 90
amjC = climo[climo.time.dt.month.isin([4,5,6])].mean('time')  * 100 * 91
jasC = climo[climo.time.dt.month.isin(7)].mean('time') * 100 * 92


# 2021-2022 Composites
ond = ds1.sel(time = slice('2021-10','2021-12')).mean('time') * 100 * 92
jfm = ds1.sel(time = slice('2022-01','2022-03')).mean('time') * 100 * 90
amj = ds1.sel(time = slice('2022-04','2022-06')).mean('time') * 100 * 91
jas = ds1.sel(time = slice('2022-07','2022-09')).mean('time') * 100 * 92

autumn = ond - ondC 
winter = jfm - jfmC  
spring = amj - amjC 
summer = jas - jasC 

seasons = [autumn, winter, spring, summer]
titles = ['Autumn 2021', 'Winter 2022', 'Spring 2022', 'Summer 2022']


# Before plotting, add cyclic point
lon = ds1.coords['longitude']
lat = ds1.coords['latitude']

c_seasons = []
for sdx, season in enumerate(seasons):
    data, lon_c = add_cyclic_point(season.values, coord = lon)
    c_seasons.append(data)

X, Y = np.meshgrid(lon_c, lat)

# ==========================
#        Plotting   
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
    ax.set_extent([-180,180,55,90], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE.with_scale('110m'), linewidth=1.0)
    ax.add_feature(cfeature.BORDERS)
    return(ax)


tcrs = ccrs.PlateCarree()
pcrs = ccrs.NorthPolarStereo()
fig, ax = plt.subplots(2, 2,
                      subplot_kw = {'projection':pcrs},
                      #constrained_layout = True,
                      figsize=(9,9))

n = -1
for col in range(2):
    for row in range(2):
        n += 1
        plot_background(ax[col,row])
        ax[col,row].set_title(titles[n])
        cf = ax[col,row].contourf(X,Y, c_seasons[n],
                          cmap = 'RdBu',#'BrBG',
                          levels = np.arange(-55, 56, 1),
                          extend = 'both',
                          transform=tcrs)



fig.subplots_adjust(top = 0.95,
                    bottom = 0.1,
                    left = 0.07,
                    right = 0.85,
                    hspace = 0.02,
                    wspace = 0.04)

cbar_ax = fig.add_axes([0.87,
                        0.25,
                        0.03,
                        0.5])#0.27, 0.07, 0.5, 0.02])

cbar = fig.colorbar(cf,
                    orientation='vertical',
                    cax=cbar_ax)


cbar.ax.set_ylabel('Seasonal total precipitation (cm)\n     anomalies from 1991-2020')
plt.savefig('figs/v3.RdBlu.arctic.2021-2022.precip.anomalies.era5.png', dpi = 500)

plt.show(), exit()
