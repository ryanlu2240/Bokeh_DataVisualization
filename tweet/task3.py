from bokeh.plotting import figure, show, output_file
import pandas as pd
import numpy as np
from bokeh.palettes import Category20 as palette
from bokeh.models import ColumnDataSource, HoverTool, Slider, CustomJS
from bokeh.layouts import column
from bokeh.models.widgets import Div
import itertools
import operator
from tqdm import tqdm
import os
from random import randint
from scipy.interpolate import interp1d
from bokeh.models import Label
from bokeh.models import  ColumnDataSource,Range1d, LabelSet, Label

from pandas.core.frame import DataFrame



user_info = pd.read_csv('tweet_user_info.csv')
tweets = pd.read_csv('tweets_final.csv')
group_list = [x for x in user_info.description_group.unique() if x is not np.nan]
cmap = palette[20]
#node
auid = []
acc = []
x = []
y = []
size = []
r = []
g = []
node_c = []
#edge
xs = []
ys = []
c = []
#node
for i in tqdm(range(user_info.shape[0])):
    if user_info.iloc[i,3]>1000 and user_info.iloc[i,8] is not np.nan:
        auid.append(user_info.iloc[i,0])
        acc.append(user_info.iloc[i,1])
        x.append(randint(0,1500))
        y.append(randint(0,1000))
        if user_info.iloc[i,3]<9999: 
        	size.append('8px')
        	r.append(1)
        elif user_info.iloc[i,3]<49999: 
        	size.append('12px')
        	r.append(5)
        elif user_info.iloc[i,3]<99999: 
        	size.append('20px')
        	r.append(15)
        elif user_info.iloc[i,3]<499999:
        	size.append('35px')
        	r.append(25)
        elif user_info.iloc[i,3]<999999: 
        	size.append('60px')
        	r.append(40)
        else: 
        	size.append('100px')
        	r.append(60)
        g.append(user_info.iloc[i,8])
        node_c.append(cmap[group_list.index(user_info.iloc[i,8])])

node_source = ColumnDataSource(data=dict(x=x, y=y, size=r, c=node_c))

# print(df)
# edge
for i in tqdm(range(tweets.shape[0])):
    tid = tweets.iloc[i,0]
    aid = tweets.iloc[i,1]
    if aid in auid:
        auidx = auid.index(aid)
        df = tweets[tweets['referenced_tweet'] == str(tid)]
        for j in range(df.shape[0]):
            retaid = df.iloc[j,1]
            if retaid in auid :
                retidx = auid.index(retaid)
                if g[auidx] in group_list:
                    gidx = group_list.index(g[auidx])
                    tx = []
                    ty = []
                    tx.append(x[auidx])
                    ty.append(y[auidx])
                    tx.append(x[retidx])
                    ty.append(y[retidx])
                    xs.append(tx)
                    ys.append(ty)
                    c.append(cmap[gidx])

edge_source = ColumnDataSource(data=dict(xs=xs, ys=ys, c=c))


p = figure(plot_width=1500, plot_height=1000, x_range=(0, 1500), y_range=(0, 1000))
p.scatter(x='x', y='y', source=node_source, color='c', size='size')
p.multi_line(xs='xs', ys='ys', color='c', line_width=0.5, source=edge_source) 
for i in tqdm(range(len(auid))):
    mytext = Label(x=x[i], y=y[i], text=acc[i], text_font_size=size[i], text_baseline='middle', text_align='center')
    p.add_layout(mytext)

show(p)









