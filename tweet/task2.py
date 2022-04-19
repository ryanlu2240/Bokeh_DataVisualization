from bokeh.plotting import figure, show, output_file
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show
from bokeh.palettes import Dark2_5 as palette
from bokeh.models import ColumnDataSource, HoverTool, Slider, CustomJS
from bokeh.layouts import column
from bokeh.models.widgets import Div
import itertools
import operator
from tqdm import tqdm
import os

from os import path
from wordcloud import WordCloud
from bokeh.io import curdoc

img = []

user_info = pd.read_csv('tweet_user_info.csv')
tweets = pd.read_csv('tweets_final.csv')
ts = ['' for i in range(2010,2022)] 


year = [i for i in range(2010,2022)]
for i in tqdm(range(tweets.shape[0])):
    twet = tweets.iloc[i,3]
    date = tweets.iloc[i,4]
    y = int(date[:4])
    ts[y-2010] = ts[y-2010] + twet


for y in year:
    wordcloud = WordCloud().generate(ts[y-2010])
    img.append(wordcloud)
    import matplotlib.pyplot as plt
    wordcloud.to_file(str(y)+'.png')

div_image = Div(text="""<img src="2010.png" alt="div_image">""", width=400, height=200)
year_slider = Slider(start=2010, end=2021, value=2010, step=1, title="year", callback_policy = 'mouseup')
callback = CustomJS(args=dict(d=div_image, slider=year_slider), code="""

    console.log(slider.value)
    d.text = '<img src=\"' + String(slider.value) + '.png\" alt=\"div_image\">';
    console.log(d.text)
""")
year_slider.js_on_change('value_throttled', callback)


show(column(div_image, year_slider))



