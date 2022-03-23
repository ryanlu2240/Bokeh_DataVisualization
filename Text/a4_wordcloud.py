import argparse
import numpy as np
import pandas as pd
from bokeh.io import output_file, show
from bokeh.models.widgets import Div
from tqdm import tqdm
from wordcloud import WordCloud
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()
parser.add_argument('--d', type=str)
parser.add_argument('--n', type=int)
args = parser.parse_args()

df = pd.read_csv('tfidf.csv')
d = df[df['documents'] == args.d].iloc[:,2:]
d.reset_index(drop=True, inplace=True)
print(d)

d_word = {}

for i in range(d.shape[0]):
    d_word[d.iloc[i,0]] = d.iloc[i,1]

wordcloud = WordCloud(width=900,height=500, max_words=args.n,relative_scaling=1,normalize_plurals=False).generate_from_frequencies(d_word)

plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()

