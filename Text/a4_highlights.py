import argparse
import numpy as np
import pandas as pd
from bokeh.io import output_file, show
from bokeh.models.widgets import Div
from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument('--d', type=str)
args = parser.parse_args()

df = pd.read_csv('tfidf.csv')
d = df[df['documents'] == args.d].iloc[:,2:]
d.reset_index(drop=True, inplace=True)
idf_min = min(d['TF.IDF'])
idf_max = max(d['TF.IDF'])
g = idf_max - idf_min
color = []
bold = []
#4 color light to dark is '#ffa366', '#ff6600', '#ff3333', '#990000'
#set color
for i in range(d.shape[0]):
    if((d.iloc[i,1]-idf_min)/g <= 0.2 and (d.iloc[i,1]-idf_min)/g > 0.05):
        color.append('#ffa366')
        bold.append(False)
    elif((d.iloc[i,1]-idf_min)/g <= 0.4):
        color.append('#ff6600')
        bold.append(False)
    elif((d.iloc[i,1]-idf_min)/g <= 0.7):
        color.append('#ff3333')
        bold.append(True)
    else:
        color.append('#990000')
        bold.append(True)
d['color'] = color
d['bold'] = bold
print(d)

f = open('science/'+args.d, 'r')
text = ''
for line in tqdm(f.readlines()):
    edited = line
    for i in range(d.shape[0]-1,0,-1):
        w = d.iloc[i,0]
        if w == 'color' or w=='span':
            continue
        if d.iloc[i,3]:
            edited = edited.replace(w, '<span style="color:' + d.iloc[i,2] + '"><b>' + w + '</b></span>')
        else:
            edited = edited.replace(w, '<span style="color:' + d.iloc[i,2] + '">' + w + '</span>')
    # print(edited)
    text = text + edited + '<br>'

# line = 'There are much more than black holes than meets the eye.'
# edited = line
# for i in range(d.shape[0]-1,0,-1):
#     print(i,':',edited)
#     w = d.iloc[i,0]
    
#         continue
#     if d.iloc[i,3]:
#         edited = edited.replace(w, '<span style="color:' + d.iloc[i,2] + '"><b>' + w + '</b></span>')
#     else:
#         edited = edited.replace(w, '<span style="color:' + d.iloc[i,2] + '">' + w + '</span>')



div = Div(text=text,
width=1000)

show(div)
