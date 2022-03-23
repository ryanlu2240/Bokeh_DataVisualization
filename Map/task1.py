import geopandas as gpd
from bokeh.plotting import save, figure, show
from bokeh.models import GeoJSONDataSource, HoverTool
from bokeh.models.tools import CustomJSHover
import numpy as np


us_map = 'us_map.json'
us_counties = 'us_counties_map.json'
us_states = 'us_states_map.json'

# Read the data
us = gpd.read_file(us_map)
countries = gpd.read_file(us_counties)
states = gpd.read_file(us_states)
state_list = states['STATE']
s = []
for i in countries['STATE']:
	t=states.loc[states['STATE'] == i] 
	s.append(t.iloc[0,2])
countries = countries.assign(STATE_NAME =  s)

# Reproject to the same projection
CRS = us.crs
countries = countries.to_crs(crs=CRS)
states = states.to_crs(crs=CRS)


# Convert GeoDataFrames into GeoJSONDataSource objects (similar to ColumnDataSource)
us_source = GeoJSONDataSource(geojson=us.to_json())
country_source = GeoJSONDataSource(geojson=countries.to_json())
state_source = GeoJSONDataSource(geojson=states.to_json())

# Initialize our plot figure
p = figure(plot_width=1000, plot_height=600, x_range=(-130, -65), y_range=(25, 50), title="USA map")

state = p.patches('xs','ys', source = state_source, fill_color = None,
                   line_color = 'blue', line_width = 1.25, fill_alpha = 1)
country = p.patches('xs','ys', source = country_source, fill_color = None,
                   line_color = 'gray', line_width = 0.5, fill_alpha = 1)
p.multi_line('xs', 'ys', source=us_source, color='black', line_width=1)

p.add_tools(HoverTool(renderers = [country],
                      tooltips = [('State','@STATE_NAME'),('Country','@NAME')]))

show(p)