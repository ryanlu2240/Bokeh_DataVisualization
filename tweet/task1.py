import pandas as pd
import numpy as np
from bokeh.plotting import figure, show
from bokeh.palettes import Dark2_5 as palette
from bokeh.models import ColumnDataSource, HoverTool
import itertools
import operator
from tqdm import tqdm


user_info = pd.read_csv('tweet_user_info.csv')
tweets = pd.read_csv('tweets_final.csv')
year = range(2010,2022)
count = [0]*len(year)
account = []

total_group = []
group_list = [x for x in user_info.description_group.unique() if x is not np.nan]

for i in year:
	group_dict = {}
	acc_dict = {}

	for i in group_list:
		if i is not np.nan:
			group_dict[i] = 0
	total_group.append(group_dict)
	account.append(acc_dict)


for i in tqdm(range(tweets.shape[0])):
	auid = tweets.iloc[i,1]
	date = tweets.iloc[i,4]
	y = date[:4]

	if auid in account[int(y)-2010]:
		account[int(y)-2010][auid] = account[int(y)-2010][auid] + 1
	else:
		account[int(y)-2010][auid] = 1
	gt = user_info[user_info['author_id'] == auid]
	if not gt.empty:
		g = gt.iloc[0,8]
	if g is not np.nan:
		total_group[int(y)-2010][g] = total_group[int(y)-2010][g] + 1

final_acc = []
for y in year:
	a = max(account[y-2010].items(), key=operator.itemgetter(1))[0]
	gt = user_info[user_info['author_id'] == a]
	final_acc.append(gt.iloc[0,1])



data = []
for i in group_list:
	t = []
	for y in year:
		t.append(total_group[y-2010][i])
	data.append(t)


colors = itertools.cycle(palette) 

p = figure(plot_width=1200, plot_height=800, title="Line chart", x_axis_label="year", y_axis_label="tweets count")

for idx, g in enumerate(group_list):
	ddata = {}
	ddata['x'] = [i for i in year]
	ddata['y'] = data[idx]
	ddata['a'] = final_acc
	source = ColumnDataSource(data=ddata)
	p.line(x='x', y='y', legend_label=g, line_width=2, color=next(colors), source=source)

p.add_tools(HoverTool(
    tooltips=[
        ( 'year','@x',),
        ( 'Most Active Account','@a'),
    ],

))
p.legend.location = "top_left"
p.xaxis.ticker = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
show(p)










