import geopandas as gpd
from bokeh.plotting import save, figure, show
from bokeh.models import GeoJSONDataSource, HoverTool, LogTicker, Label
from bokeh.models.tools import CustomJSHover
from bokeh.palettes import brewer, Viridis3, YlOrBr, YlOrRd
from bokeh.models import (CDSView, ColorBar, CustomJS,
                          CustomJSFilter, GeoJSONDataSource,
                          LinearColorMapper, Slider, LogColorMapper)
from bokeh.layouts import column, row, widgetbox
import numpy as np
import json 
import os


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


# Convert GeoDataFrames into GeoJSONDataSource objects (similar to ColumnDataSource)
us_source = GeoJSONDataSource(geojson=us.to_json())
country_source = GeoJSONDataSource(geojson=countries.to_json())
state_source = GeoJSONDataSource(geojson=states.to_json())

# Initialize our plot figure
p = figure(plot_width=1000, plot_height=600, x_range=(-130, -65), y_range=(25, 50), title="Wildland Fire Footprint in the United State", toolbar_location='above')

# Define color palettes
palette = ['#ffffff', '#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026', '#800026']
color_mapper = LogColorMapper(palette = palette, low = 1, high = 1e10)

# Create color bar.
color_bar = ColorBar(color_mapper=color_mapper,location = (0,10),
                     border_line_color=None, orientation = 'vertical',ticker=LogTicker())


year_slider = Slider(start=1800, end=2021, value=1800, step=1, title="year", callback_policy = 'mouseup')
n_slider = Slider(start=1, end=50, value=1, step=1, title="N", callback_policy = 'mouseup')
mytext = Label(x=820, y=510, x_units='screen', y_units='screen',
                 text=str(year_slider.value), render_mode='css',
                 border_line_color='black', border_line_alpha=1.0,
                 background_fill_color='white', background_fill_alpha=1.0)
callback = CustomJS(args=dict(source=country_source, year_slider=year_slider, n_slider=n_slider, mytext=mytext), code="""
    data = source.data;
    for (var i = 0; i < source.get_length(); i++){
        var v=0;
        for (var j = year_slider.value-n_slider.value+1; j <= year_slider.value; j++){
            v =  v + data[String(j)][i];
        }
        data['SELECT_YEAR'][i] = v;
    }
    mytext.text = String(year_slider.value)
    source.change.emit();
""")
year_slider.js_on_change('value_throttled', callback)
n_slider.js_on_change('value_throttled', callback)



country = p.patches('xs','ys', source = country_source,
                   fill_color = {'field' :'SELECT_YEAR', 'transform' : color_mapper},
                   line_color = 'gray', line_width = 0.5, fill_alpha = 1)
state = p.patches('xs','ys', source = state_source, fill_color = None,
                   line_color = 'blue', line_width = 1.25, fill_alpha = 1)
p.multi_line('xs', 'ys', source=us_source, color='black', line_width=1)


p.add_tools(HoverTool(renderers = [country],
                      tooltips = [('State','@STATE_NAME'),('Country','@NAME'),('Burned Area','@SELECT_YEAR')]))

p.add_layout(color_bar, 'right')
p.add_layout(mytext)
layout = column(p, year_slider, n_slider)
show(layout)



















