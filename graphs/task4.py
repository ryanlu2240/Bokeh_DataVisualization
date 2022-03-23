import geopandas as gpd
import pandas as pd
from bokeh.plotting import save, figure, show
from bokeh.models import GeoJSONDataSource, HoverTool, LogTicker, Label, ColumnDataSource, Legend, Circle, LegendItem, BooleanFilter
from bokeh.models.tools import CustomJSHover
from bokeh.palettes import brewer, Viridis3, YlOrBr, YlOrRd
from bokeh.models import (CDSView, ColorBar, CustomJS,
                          CustomJSFilter, GeoJSONDataSource,
                          LinearColorMapper, Slider, LogColorMapper)
from bokeh.layouts import column, row, widgetbox
from math import floor
import numpy as np
import json
import os
from scipy.interpolate import interp1d
from bokeh.transform import linear_cmap


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
origin_str = []
destination_str = []
for index, row in flights.iterrows():
    src = airports.iloc[row['origin'],:]
    des = airports.iloc[row['destination'],:]
    xs.append([src['longitude'], des['longitude']])
    ys.append([src['latitude'], des['latitude']])
    origin_str.append(src['full_name'])
    destination_str.append(des['full_name'])
flights['xs'] = xs
flights['ys'] = ys
flights['origin_str'] = origin_str
flights['destination_str'] = destination_str

#cal total flights
total_flights =  [0] * airports.shape[0]
degree = [0] * airports.shape[0]
airports['total_flights'] = total_flights
airports['degree'] = degree
dur_str = []
delay_str = []

for index, row in flights.iterrows():
    airports.iloc[row['origin'],5] = airports.iloc[row['origin'],5] + row['number_of_flights']
    airports.iloc[row['destination'],5] = airports.iloc[row['destination'],5] + row['number_of_flights']
    airports.iloc[row['origin'],6] = airports.iloc[row['origin'],6] + 1
    airports.iloc[row['destination'],6] = airports.iloc[row['destination'],6] + 1
    dur_str.append(str(floor(row['air_time'])) + '\'')
    delay_str.append(str(floor(row['delay'])) + '\'')
flights['dur_str'] = dur_str
flights['delay_str'] = delay_str
#cal number of airline
airlines = [[] for i in range(airports.shape[0])]
for index, row in flights.iterrows():
    airlines[row['origin']] = list(set(airlines[row['origin']]) | set(row['carriers']))
    airlines[row['destination']] = list(set(airlines[row['destination']]) | set(row['carriers']))

airports['airlines'] =  airlines
number_of_airline = []

for index, row in airports.iterrows():
    number_of_airline.append(len(row['airlines']))
airports['number_of_airline'] = number_of_airline


#map radius
radius_mapper = interp1d([1,max(airports['total_flights'])],[0.05,1.2])
airports['radius'] = radius_mapper(airports['total_flights'])

dummy_radius = [2] * airports.shape[0]
dummy_radius[1] = 100
dummy_radius[2] = 1000
dummy_radius[3] = 34000
airports['dummy_radius'] = dummy_radius

#map number of airlines
airline_cmap = linear_cmap(field_name = 'number_of_airline', palette=Viridis3, low=min(airports['number_of_airline']), high=max(airports['number_of_airline']))

#map flights line width
width_mapper = interp1d([1,max(flights['number_of_flights'])],[0,3])
alpha_mapper = interp1d([1,max(flights['number_of_flights'])],[0,2])
flights['width'] = width_mapper(flights['number_of_flights'])
flights['alpha'] = alpha_mapper(flights['number_of_flights'])


sort_with_flight = flights.sort_values(by=['number_of_flights'], ascending=False, ignore_index=True)
top_200 = sort_with_flight[0:200]

# Convert GeoDataFrames into GeoJSONDataSource objects (similar to ColumnDataSource)
state_source = GeoJSONDataSource(geojson=states.to_json())
airport_source = ColumnDataSource(airports)
flight_source = ColumnDataSource(flights)
# flight_source = ColumnDataSource(top_200)

node_slider = Slider(start=1, end=34436, value=1, step=1, title="Node value", callback_policy = 'mouseup', width=1000)
edge_slider = Slider(start=1, end=1305, value=1, step=1, title="Edge value", callback_policy = 'mouseup', width=1000)

node_slider.js_on_change('value_throttled', CustomJS(args=dict(airport_source=airport_source, flight_source=flight_source), code="""
   airport_source.change.emit()
   flight_source.change.emit()

"""))

node_filter = CustomJSFilter(args=dict(airport_source=airport_source, flight_source=flight_source, node_slider=node_slider, edge_slider=edge_slider), code='''
    const indices = [];

    // iterate through rows of data source and see if each satisfies some constraint
    for (let i = 0; i < airport_source.get_length(); i++){
        var a=false;
        for(let j = 0;j < flight_source.get_length(); j++){
            if(flight_source.data['number_of_flights'][j] >= edge_slider.value && (flight_source.data['origin'][j] == i || flight_source.data['destination'][j] == i)){
                a=true;
                break;
            }
        }
        if (airport_source.data['total_flights'][i] >= node_slider.value && a){
            indices.push(true);
        } else {
            indices.push(false);
        }
    }
    return indices;
''')


edge_slider.js_on_change('value_throttled', CustomJS(args=dict(airport_source=airport_source, flight_source=flight_source), code="""
   airport_source.change.emit()
   flight_source.change.emit()
"""))

edge_filter = CustomJSFilter(args=dict(airport_source=airport_source, flight_source=flight_source, node_slider=node_slider, edge_slider=edge_slider), code='''
    const indices = [];

    // iterate through rows of data source and see if each satisfies some constraint
    for (let i = 0; i < flight_source.get_length(); i++){
        if (flight_source.data['number_of_flights'][i] >= edge_slider.value && airport_source.data['total_flights'][flight_source.data['origin'][i]] >= node_slider.value && airport_source.data['total_flights'][flight_source.data['destination'][i]] >= node_slider.value){
            indices.push(true);
        } else {
            indices.push(false);
        }
    }
    return indices;
''')


# Initialize our plot figure
p = figure(plot_width=1400, plot_height=600, x_range=(-130, -65), y_range=(25, 50), toolbar_location='above')

state = p.patches('xs','ys', source = state_source, fill_color = None,
                   line_color = 'blue', line_width = 1.25, fill_alpha = 1)

airport = p.circle('longitude', 'latitude', source=airport_source, radius='radius', color = airline_cmap, view=CDSView(source=airport_source, filters=[node_filter]))
airport_line = p.scatter('longitude', 'latitude', source=airport_source, radius='radius', fill_color = None, line_color = 'black', legend_field='dummy_radius', view=CDSView(source=airport_source, filters=[node_filter]))
# airport = p.scatter('longitude', 'latitude', source=airport_source)
flight = p.multi_line(xs='xs', ys='ys', source=flight_source, line_width = 'width', alpha = 'alpha', view=CDSView( source=flight_source, filters=[edge_filter]))
p.legend[0].title='Airport significance'
p.legend[0].location=(10, 400)
p.add_layout(p.legend[0], 'right')

#add legend
#airport significance
event_scatter_dummy = p.scatter(
    x=[1,2,3,4],
    y=[1,5,10,18],
    radius=0,
    fill_color={'field': 'y', 'transform': LinearColorMapper(palette=Viridis3, low=1, high=18)},
    # fill_color=['red','blue','green','yellow'],
    fill_alpha=1.0,
    name='event_scatter_dummy'
)
color_legend = Legend(items=[
    LegendItem(label='1', renderers=[event_scatter_dummy], index=0),
    LegendItem(label='5', renderers=[event_scatter_dummy], index=1),
    LegendItem(label='10', renderers=[event_scatter_dummy], index=2),
    LegendItem(label='18', renderers=[event_scatter_dummy], index=3),
])
color_legend.title = 'Number of airlines'
color_legend.location=(-140,200)
p.add_layout(color_legend, 'right')

#Number of flights
event_line_dummy = p.multi_line(
    xs=[[1,1],[2,2],[3,3],[4,4]],
    ys=[[1,1],[2,2],[3,3],[4,4]],
    line_width = [width_mapper(400), width_mapper(700), width_mapper(1000), width_mapper(1300)],
    alpha = [alpha_mapper(400), alpha_mapper(700), alpha_mapper(1000), alpha_mapper(1300)],
    # fill_color={'field': 'y', 'transform': LinearColorMapper(palette=Viridis3, low=1, high=18)},
    # fill_color=['red','blue','green','yellow'],
    name='event_line_dummy'
)
line_legend = Legend(items=[
    LegendItem(label='400', renderers=[event_line_dummy], index=0),
    LegendItem(label='700', renderers=[event_line_dummy], index=1),
    LegendItem(label='1000', renderers=[event_line_dummy], index=2),
    LegendItem(label='1300', renderers=[event_line_dummy], index=3)
])
line_legend.title = 'Number of flights'
line_legend.location=(-285,0)
p.add_layout(line_legend, 'right')
p.add_tools(HoverTool(renderers = [airport],
                      tooltips = [('City: ','@city'),('State: ','@state'),('Degree: ','@degree'),('Importance:: ','@total_flights')]))

p.add_tools(HoverTool(renderers = [flight],
                      tooltips = [('Airport1: ','@origin_str'),('Airport2: ','@destination_str'),('Flights: ','@number_of_flights'),('Airlines: ','@carriers'),('Duration: ','@dur_str'),('Delay: ','@delay_str')]))


layout = column(p, node_slider, edge_slider)
show(layout)
