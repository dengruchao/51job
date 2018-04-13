# -*- coding: utf-8 -*-

import csv
import codecs
import sqlite3

OUTPUT = 'SQLite'

class Pipeline:
    def __init__(self, name):
        if OUTPUT == 'CSV':
            csvfile = open(name+'.csv', 'wb')
            csvfile.write(codecs.BOM_UTF8)
            self.writer = csv.writer(csvfile)
        if OUTPUT == 'SQLite':
            self.db = sqlite3.connect(name+'.db', check_same_thread=False)
            self.cur = self.db.cursor()

    def create_tb(self, tb_name, clear=True):
        if clear:
            try:
                self.cur.execute("drop table %s" % tb_name)
            except:
                pass
        self.cur.execute(u"create table %s (\
                                        id integer primary key,\
                                        标题 varchar(100),\
                                        地区 varchar(20),\
                                        薪资 varchar(20),\
                                        公司 varchar(200),\
                                        公司类型 varchar(20),\
                                        公司人数 varchar(20),\
                                        公司领域 varchar(200),\
                                        工作年限 varchar(20),\
                                        学历 varchar(20),\
                                        招聘人数 varchar(20),\
                                        岗位职责 varchar(500),\
                                        任职要求 varchar(500)\
                         )" % tb_name)

    def save(self, tb_name, data_list):
        if OUTPUT == 'SQLite':
            #for idx, data in enumerate(data_list):
            #    if not isinstance(data, int):
            #        data = data.replace('+', 'p')
            #    data_list[idx] = data
            self.cur.execute("insert into %s values (?,?,?,?,?,?,?,?,?,?,?,?,?)" % tb_name, data_list)
            self.db.commit()
        if OUTPUT == 'CSV':
            self.writer.writerow([data.encode('utf-8') for data in data_list])

    def close_db(self):
        self.cur.close()
        self.db.close()
