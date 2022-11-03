import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from scipy import stats
import cartopy.crs as ccrs
import cartopy.feature as cfeature



# ==========================
'''     Load ERA5 Data  '''
# ==========================

pwd = '/work2/Reanalysis/ERA5/ERA5_monthly/monolevel/'+ \
		'ERA5.mon.tp.1950-2022.nc'

ds = xr.open_dataset(pwd).sel(
        latitude=slice(90, 55),
        longitude=slice(0, 360))['tp']

ds = ds.mean('expver') # September 2022 data is ERA5T as of 10.13.2022

lon = ds.coords['longitude']
lat = ds.coords['latitude']
X, Y = np.meshgrid(lon, lat)



# =========================
#   Trend Analysis 
# =========================

def seasonal_trend(ds, months, name):

    s = ds[ds.time.dt.month.isin(months)]  # select seasonal month range
    ds = s.groupby('time.year').sum('time')    # season sum
    t = s.time
    t = np.arange(0, len(ds.year))

    slope = np.array([])
    pvalue = np.array([])

    for i, latx in enumerate(lat):
        print('lat = ', latx)
        for n, lonx in enumerate(lon):
            grid = ds.sel(latitude = latx, longitude = lonx)
            result = stats.theilslopes(t, grid, alpha=0.95)
            result = stats.linregress(t, grid)
            slope = np.append(slope, result[0])
            pvalue = np.append(pvalue, result[3])
   
    np.save('binary_files/v2.'+ name + 'theilslopes.arctic.slope.npy', slope)
    np.save('binary_files/v2.'+ name + 'theilsloeps.arctic.pvalue.npy', pvalue)
    print('FINISHED', name)
 
    return(slope, pvalue)


slope_ond, p_ond = seasonal_trend(ds, [10,11,12], 'ond')
slope_jfm, p_jfm = seasonal_trend(ds, [1, 2, 3], 'jfm')
slope_amj, p_amj = seasonal_trend(ds, [4, 5, 6], 'amj')
slope_jas, P_jas = seasonal_trend(ds, [7, 8, 9], 'jas')
#slope_annual, P_annual = seasonal_trend(ds, 
#                                        [1,2,3,4,5,6,7,8,9,10,11,12],
#                                        'annual')
                                        

print('done')
exit()

