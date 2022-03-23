import geopandas as gpd
from bokeh.plotting import save, figure, show, curdoc
from bokeh.models import GeoJSONDataSource, HoverTool, LogTicker, ColumnDataSource, Label
from bokeh.models.tools import CustomJSHover
from bokeh.palettes import brewer, Viridis3, YlOrBr, YlOrRd
from bokeh.models import (CDSView, ColorBar, CustomJS,
                          CustomJSFilter, GeoJSONDataSource,
                          LinearColorMapper, Slider, LogColorMapper, Toggle)
from bokeh.layouts import column, row, widgetbox
import numpy as np
import json 
import os

def getPolyCoords(row, geom, coord_type):
    """Returns the coordinates ('x|y') of edges/vertices of a Polygon/others"""

    # Parse the geometries and grab the coordinate
    geometry = row[geom]
    #print(geometry.type)

    if geometry.type=='Polygon':
        if coord_type == 'x':
            # Get the x coordinates of the exterior
            # Interior is more complex: xxx.interiors[0].coords.xy[0]
            return list( geometry.exterior.coords.xy[0] )
        elif coord_type == 'y':
            # Get the y coordinates of the exterior
            return list( geometry.exterior.coords.xy[1] )

    if geometry.type in ['Point', 'LineString']:
        if coord_type == 'x':
            return list( geometry.xy[0] )
        elif coord_type == 'y':
            return list( geometry.xy[1] )

    if geometry.type=='MultiLineString':
        all_xy = []
        for ea in geometry:
            if coord_type == 'x':
                all_xy.append(list( ea.xy[0] ))
            elif coord_type == 'y':
                all_xy.append(list( ea.xy[1] ))
        return all_xy

    if geometry.type=='MultiPolygon':
        all_xy = []
        for ea in geometry:
            if coord_type == 'x':
                all_xy.append(list( ea.exterior.coords.xy[0] ))
            elif coord_type == 'y':
                all_xy.append(list( ea.exterior.coords.xy[1] ))
        return all_xy

    else:
        # Finally, return empty list for unknown geometries
        return []

us_map = 'us_map.json'
us_counties = 'us_counties_map.json'
us_states = 'us_states_map.json'
fire = 'wildland_fires_1800-2021.json'

with open(fire) as f:
    data = json.load(f)

# Read the data
us = gpd.read_file(us_map)
states = gpd.read_file(us_states)
if os.path.isfile('country_source.geojson'):
    print('file exist!')
    file = open('country_source.geojson')
    countries = gpd.read_file(file)
else:
    print('making countries file ...')
    countries = gpd.read_file(us_counties)
    state_list = states['STATE']
    s = []
    for i in countries['STATE']:
        t=states.loc[states['STATE'] == i] 
        s.append(t.iloc[0,2])
    countries = countries.assign(STATE_NAME = s)

    for year in range(1800,2022,1):
        s = [0] * countries.shape[0]
        year = str(year)
        if year in data.keys():
            d_year = data[year]
            for state in  d_year.keys():
                d_state = d_year[state]
                d_country = d_state['counties']
                for d in d_country.keys():
                    t = countries.index[(countries['COUNTY'] == d) & (countries['STATE'] == state)].tolist()
                    s[t[0]] = float(d_country[d])
            kwargs = {year : s}
            countries = countries.assign(**kwargs)
        else:
            kwargs = {year : s}
            countries = countries.assign(**kwargs)
    s = countries.loc[:,'1800']
    countries = countries.assign(SELECT_YEAR = s)

    countries.to_file("country_source.geojson", driver='GeoJSON')
    print('done')



# Reproject to the same projection
CRS = us.crs
countries['geometry'] = countries['geometry'].to_crs(crs=CRS)
states = states.to_crs(crs=CRS)

countries['xs'] = countries.apply(getPolyCoords, geom="geometry", coord_type="x", axis=1)
countries['ys'] = countries.apply(getPolyCoords, geom="geometry", coord_type="y", axis=1)


# Convert GeoDataFrames into GeoJSONDataSource objects (similar to ColumnDataSource)
us_source = GeoJSONDataSource(geojson=us.to_json())
country_source = ColumnDataSource(countries.drop(columns=['geometry']))
state_source = GeoJSONDataSource(geojson=states.to_json())

# Initialize our plot figure
p = figure(plot_width=1000, plot_height=600, x_range=(-130, -65), y_range=(25, 50), title="Wildland Fire Footprint in the United State", toolbar_location='above')

# Define color palettes
palette = ['#ffffff', '#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026', '#800026']
color_mapper = LogColorMapper(palette = palette, low = 1, high = 1e10)

# Create color bar.
color_bar = ColorBar(color_mapper=color_mapper,location = (0,10),
                     border_line_color=None, orientation = 'vertical',ticker=LogTicker())


current_year = 1800
start_year = 1800

n_slider = Slider(start=1, end=50, value=1, step=1, title="N", callback_policy = 'mouseup')
mytext = Label(x=820, y=510, x_units='screen', y_units='screen',
                 text=str(current_year), render_mode='css',
                 border_line_color='black', border_line_alpha=1.0,
                 background_fill_color='white', background_fill_alpha=1.0)

toggle = Toggle(label="Play", button_type="success")

rewind = Toggle(label="rewind", button_type="danger")


country = p.patches('xs','ys', source = country_source,
                   fill_color = {'field' :'SELECT_YEAR', 'transform' : color_mapper},
                   line_color = 'gray', line_width = 0.5, fill_alpha = 1)
state = p.patches('xs','ys', source = state_source, fill_color = None,
                   line_color = 'blue', line_width = 1.25, fill_alpha = 1)
p.multi_line('xs', 'ys', source=us_source, color='black', line_width=1)

def callback():
    global current_year, s, country_source, start_year, mytext
    if toggle.active and current_year<2021 and not rewind.active:
        if current_year-n_slider.value+1 < 1800:
            start_year = 1800
        else:
            start_year = current_year-n_slider.value+1
        current_year = current_year + 1
        
        if current_year - start_year + 1 > n_slider.value:
            for i in range(countries.shape[0]):
                country_source.data['SELECT_YEAR'][i] = country_source.data['SELECT_YEAR'][i] -  country_source.data[str(start_year)][i]     
            start_year = start_year + 1
        for i in range(countries.shape[0]):
            country_source.data['SELECT_YEAR'][i] = country_source.data['SELECT_YEAR'][i] +  country_source.data[str(current_year)][i]     
        country_source.trigger('data', country_source.data, country_source.data)
        mytext.text = str(current_year)
    elif not toggle.active and current_year>1800 and rewind.active:
        for i in range(countries.shape[0]):
            country_source.data['SELECT_YEAR'][i] = country_source.data['SELECT_YEAR'][i] -  country_source.data[str(current_year)][i] 
        if current_year-n_slider.value+1 < 1800:
            start_year = 1800
        else:
            start_year = current_year-n_slider.value+1
        current_year = current_year - 1
        if start_year > 1800:
            start_year = start_year - 1
            for i in range(countries.shape[0]):
                country_source.data['SELECT_YEAR'][i] = country_source.data['SELECT_YEAR'][i] +  country_source.data[str(start_year)][i]     

        country_source.trigger('data', country_source.data, country_source.data)
        mytext.text = str(current_year)

def n_callback(attr, old, new):
    global country_source, current_year, t, s, countries
    if current_year-n_slider.value+1  >= 1800:
        t = current_year-n_slider.value+1
    else:
        t = 1800
    for i in range(countries.shape[0]):
        s = 0
        for j in range(t,current_year+1,1):
            s = s+country_source.data[str(j)][i]
        country_source.data['SELECT_YEAR'][i] = s
    country_source.trigger('data', country_source.data, country_source.data)

n_slider.on_change('value_throttled', n_callback)

p.add_tools(HoverTool(renderers = [country],
                      tooltips = [('State','@STATE_NAME'),('Country','@NAME'),('Burned Area','@SELECT_YEAR')]))

p.add_layout(color_bar, 'right')
p.add_layout(mytext)
curdoc().add_root(column(p, n_slider, toggle, rewind))
curdoc().add_periodic_callback(callback, 1000)




