import argparse
import numpy as np
import pandas as pd
from bokeh.io import output_file, show
from bokeh.models.widgets import Div
from tqdm import tqdm
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from nltk.tokenize import sent_tokenize
import cus_wordtree


parser = argparse.ArgumentParser()
parser.add_argument('--d', type=str)
parser.add_argument('--k', type=str)
parser.add_argument('--n', type=int)
args = parser.parse_args()
# keywords = input('key word:')


text = ''
f = open('science/'+args.d, 'r')
for line in f.readlines():
    line = re.sub(r"\s+", " ", line)
    text = text + line

l_sen = sent_tokenize(text)


g = cus_wordtree.search_and_draw(corpus = l_sen, keyword = args.k.split(), max_n = args.n)
g.render() # creates a file world.dv.png
