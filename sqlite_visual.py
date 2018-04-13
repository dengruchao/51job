# -*- coding: utf-8 -*-

import Tkinter
import ttk
import sqlite3
import os

class SQLiteVisual:

    def __init__(self, db_name):
        db = sqlite3.connect(db_name)
        self.cur = db.cursor()
        self.top = Tkinter.Tk()
        #self.top.geometry('1000x600+200+100')
        self.top.title('SQLiteVisual')
        self.init_ui()

    def init_ui(self):
        self.lb_table = Tkinter.Listbox(self.top, {'width': 30})
        self.lb_table.pack(side=Tkinter.LEFT, fill=Tkinter.Y)
        self.menu = Tkinter.Menu(self.top, tearoff=0)
        self.menu.add_command(label='Delete', command=self.delete)
        def popupmenu(event):
            self.menu.post(event.x_root, event.y_root)
        self.lb_table.bind("<Button-3>", popupmenu)

    def delete(self):
        tb_name = self.lb_table.get(Tkinter.ACTIVE)
        self.lb_table.delete(self.lb_table.curselection())
        self.cur.execute("drop table %s" % tb_name)

    def list_table(self):
        tables = self.cur.execute("select name from sqlite_master where type = 'table' order by name").fetchall()
        for table in tables:
            self.lb_table.insert(1, table)
        self.lb_table.bind('<Double-1>', self.list_data)

    def list_data(self, event):
        table = self.lb_table.get(self.lb_table.curselection()[0])
        try:
            self.tree.pack_forget()
            self.scrollbar_x.pack_forget()
            self.scrollbar_y.pack_forget()
        except:
            pass
        self.cur.execute("select * from %s" % table)
        cols = tuple([t[0] for t in self.cur.description])
        data = self.cur.fetchall()
        self.scrollbar_y = Tkinter.Scrollbar(self.top)
        self.scrollbar_y.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.scrollbar_x = Tkinter.Scrollbar(self.top, orient=Tkinter.HORIZONTAL)
        self.scrollbar_x.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
        self.tree =ttk.Treeview(self.top, yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set,
                                columns=cols, show='headings')
        for c in cols:
            self.tree.column(c, width=200, anchor='center')
            self.tree.heading(c, text=c)

        for i, d in enumerate(data):
            self.tree.insert('', i, values=d)
        self.tree.pack(side=Tkinter.LEFT, expand=Tkinter.YES, fill=Tkinter.BOTH)
        self.scrollbar_y.config(command=self.tree.yview)
        self.scrollbar_x.config(command=self.tree.xview)

    def start(self):
        self.top.mainloop()

if __name__ == '__main__':
    for f in os.listdir('.'):
        if f.split('.')[-1] == 'db':
            db_name = f
            break
    sql = SQLiteVisual(db_name)
    sql.list_table()
    sql.start()
