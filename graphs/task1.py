import geopandas as gpd
import pandas as pd
from bokeh.plotting import save, figure, show
from bokeh.models import GeoJSONDataSource, HoverTool, LogTicker, Label, ColumnDataSource
from bokeh.models.tools import CustomJSHover
from bokeh.palettes import brewer, Viridis3, YlOrBr, YlOrRd
from bokeh.models import (CDSView, ColorBar, CustomJS,
                          CustomJSFilter, GeoJSONDataSource,
                          LinearColorMapper, Slider, LogColorMapper)
from bokeh.layouts import column, row, widgetbox
import numpy as np
import json
import os


us_states = 'us_states.json'
us_airports = 'all_airports_info.json'
us_flights = 'all_edges.json'

# Read the data
states = gpd.read_file(us_states)
airports = pd.read_json(us_airports)
flights = pd.read_json(us_flights)
airports = airports.transpose()
#set flight's src des coordinates
xs = []
ys = []
for index, row in flights.iterrows():
    src = airports.iloc[row['origin'],:]
    des = airports.iloc[row['destination'],:]
    xs.append([src['longitude'], des['longitude']])
    ys.append([src['latitude'], des['latitude']])
flights['xs'] = xs
flights['ys'] = ys

sort_with_flight = flights.sort_values(by=['number_of_flights'], ascending=False, ignore_index=True)
top_200 = sort_with_flight[0:200]


# Convert GeoDataFrames into GeoJSONDataSource objects (similar to ColumnDataSource)
state_source = GeoJSONDataSource(geojson=states.to_json())
airport_source = ColumnDataSource(airports)
flight_source = ColumnDataSource(top_200)
# flight_source = GeoJSONDataSource(geojson=flights.to_json())

# Initialize our plot figure
p = figure(plot_width=1000, plot_height=600, x_range=(-130, -65), y_range=(25, 50), toolbar_location='above')

state = p.patches('xs','ys', source = state_source, fill_color = None,
                   line_color = 'blue', line_width = 1.25, fill_alpha = 1)
airport = p.scatter('longitude', 'latitude', source=airport_source)
flight = p.multi_line(xs='xs', ys='ys', source=flight_source)

layout = column(p)
show(layout)
