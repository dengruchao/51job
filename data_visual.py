# -*- coding: utf-8 -*-

import sqlite3
import os
import jieba
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pandas as pd
import numpy

class DataVisual:
    def __init__(self, db_name):
        self.db = sqlite3.connect(db_name)
        self.cur = self.db.cursor()

    def spec_wc(self, tb_name):
        self.cur.execute('select 任职要求 from %s' % tb_name)
        #self.cur.execute('select 岗位职责 from %s' % tb_name)
        data = self.cur.fetchall()
        text = ''
        for d in data:
            spec = d[0]
            if spec.strip() == '':
                continue
            text += spec
        seg_list = jieba.lcut(text)
        words_df = pd.DataFrame({'seg_list': seg_list})
        #print words_df.head()
        stopwords = pd.read_csv("stopwords.txt",index_col=False,quoting=3,sep="\t",names=['stopword'], encoding='utf-8')
        words_df = words_df[~words_df.seg_list.isin(stopwords.stopword)]
        #print words_df.head()
        words_stat = words_df.groupby(by=['seg_list'])['seg_list'].agg({"计数":numpy.size})
        words_stat = words_stat.reset_index().sort_values(by=["计数"],ascending=False)
        print words_stat.head()

        wordcloud=WordCloud(font_path="SIMYOU.TTF",background_color="white",max_font_size=300, width=1000, height=600)
        word_frequence = {x[0]:x[1] for x in words_stat.head(100).values}
        wordcloud=wordcloud.generate_from_frequencies(word_frequence)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()

if __name__ == '__main__':
    for f in os.listdir('.'):
        if f.split('.')[-1] == 'db':
            db_name = f
            break
    dv = DataVisual(db_name)
    dv.spec_wc('python')
    #dv.spec_wc('cpp')
    #dv.spec_wc('人工智能')
    #dv.spec_wc('大数据')
    #dv.spec_wc('web后端')
