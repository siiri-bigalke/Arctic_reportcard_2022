import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd


'''
Script summary: WY 2021 sesaonal departure of precipitation from the 1991-2020 climatological means. Autumn 2021 (OND), winter 2022 (JFM), spring 2022 (AMJ), and summer 2022 (JAS).
Author: Siiri Bigalke
Last edited: October 13, 2022
'''


# ==========================
'''     Load ERA5 Data  '''
# ==========================

pwd = '/work2/Reanalysis/ERA5/ERA5_monthly/monolevel/'+ \
                'ERA5.mon.tp.1950-2022.nc'

ds = xr.open_dataset(pwd).sel(
        latitude=slice(90, 60),
        longitude=slice(0, 360))['tp']

ds = ds.mean('expver') # As of 10.13.2022 september data is still ERA5T

lon = ds.coords['longitude']
lat = ds.coords['latitude']
X, Y = np.meshgrid(lon, lat)


# Weight by cosine of latitude
weights = np.cos(np.deg2rad(ds.latitude))
weights.name = 'weights'
wds = ds.weighted(weights)
ds = wds.mean(('latitude', 'longitude'))

# Create new coordinate for water year
water_year = (ds.time.dt.month >= 10) + ds.time.dt.year
ds.coords['water_year'] = water_year

# =========================
#   Trend Analysis 
# =========================

def seasonal_trend(ds, months, name):

    s = ds[ds.time.dt.month.isin(months)]  # Select seasonal month range
    if name == 'WY':
        ds = s.groupby('water_year').mean(['time'])
        avg = ds.sel(water_year = slice('1991', '2020')).mean() 
        depart = (ds - avg) / avg # Find percent departure from 1991-2020 average
    else:   
        ds = s.groupby('time.year').mean(['time'])
        avg = ds.sel(year = slice('1991', '2020')).mean() 
        depart = (ds - avg) / avg # Find percent departure from 1991-2020 average
    
    #return(ds*120000) # Use for raw values of mm/decade
    return(depart * 100 + 100)   

ond = seasonal_trend(ds, [10,11,12], 'ond').sel(year = slice(1950,2021))
jfm = seasonal_trend(ds, [1, 2, 3], 'jfm').sel(year = slice(1951,2022))
amj = seasonal_trend(ds, [4, 5, 6], 'amj').sel(year = slice(1951,2022))
jas = seasonal_trend(ds, [7, 8, 9], 'jas').sel(year = slice(1951,2022))
wy = seasonal_trend(ds, [np.arange(1, 13)], 'WY').sel(water_year=slice(1951,2022))


# Check length
# ------------
seasons = [ond, jfm, amj, jas, wy]
labs = ['OND', 'JFM', 'AMJ', 'JAS', 'WY']

for sdx, sea in enumerate(seasons):
    print(labs[sdx])
    print(len(sea))


date = np.arange(1951, 2023)
df = pd.DataFrame({'year': date,
                   'OND': ond,
                   'JFM': jfm,
                   'AMJ': amj,
                   'JAS': jas,
                   'WY': wy})


df.to_csv('v4.ERA5.precipitation.%from1991-2020.csv') # v4 includes September 2022 data
exit()



# ===========================
#        Plot Data
# ===========================
# (figure not included in 2022 Arctic Report Card)

fig, ax = plt.subplots(figsize=(10, 6))

seasons = [ond, jfm, amj, jas]#, year]
labs = ['OND', 'JFM', 'AMJ', 'JAS']#, 'Annual']
colors = ['brown', 'blue', 'pink', 'orange']#, 'black']

x = np.arange(1951, 2023)

for i, season in enumerate(seasons):
      ax.plot(x, season, 
               label = labs[i],
               color = colors[i])

ax.plot(x, wy, 
               label = 'WY',
               color = 'black', 
               linewidth = 3)

ax.legend(loc='center', bbox_to_anchor =(1.05, 0.5))
ax.axhline(y = 100, color = 'black')


ax.spines.right.set_visible(False)
ax.spines.top.set_visible(False)

ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')

ax.set_ylabel('Percent of 1991-2020 average')
plt.grid(linestyle = '--')

#plt.savefig('weighted.arctic.precip.departure1991-2020.png', dpi=500)
plt.show()

exit()
