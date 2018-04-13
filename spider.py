# -*- coding: utf-8 -*-

import requests
from lxml import etree
import chardet
from pipeline import Pipeline
from multipro import *
import re
import time

class Job51:
    def __init__(self):
        self.id = 1
        self.isFirst = True
        self.keyword = ''
        self.pl = Pipeline('job51')
        self.neglect = 0
        self.exactly = True

    def get_link(self, url):
        resp = requests.get(url)
        resp.encoding = 'GB2312'
        html = etree.HTML(resp.text)
        els = html.xpath('//div[@id="resultList"]/div[@class="el"]')
        for el in els:
            link = el.xpath('p/span/a/@href')[0].strip()
            title = el.xpath('p/span/a/text()')[0].strip()
            if self.exactly and title.lower().find(self.keyword) == -1:
                continue
            Request(link, self.get_details)
        # if it is first page, add page link to queue
        if self.isFirst:
            next_page_link = html.xpath('//div[@class="dw_page"]/div/div/div/ul/li/a/@href')[-1]
            total_page = html.xpath('//div[@class="dw_page"]/div/div/div/span[1]/text()')[0]
            total_page = re.search(u'共(.*?)页', total_page, re.S).group(1)
            for page in range(2, int(total_page)+1):
                page_link = re.sub(',(\d+)\.html?', ',%s.html' % page, next_page_link)
                Request(page_link, self.get_link)
            self.isFirst = False

    def get_details(self, link):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, likeGecko) Chrome/60.0.3112.113 Safari/537.36'
        }
        resp = requests.get(link, headers=headers)
        resp.encoding = 'GB2312'
        html = etree.HTML(resp.text)
        try:
            cn = html.xpath('//div[@class="cn"]')[0]

            title = cn.xpath('h1/text()')[0].strip()
            district = cn.xpath('span/text()')[0].strip()
            salary = cn.xpath('strong/text()')[0].strip()
            company = cn.xpath('p[1]/a/text()')[0].strip()
            company_details = cn.xpath('p[2]/text()')[0].strip()

            jtag = html.xpath('//div[@class="t1"]/span')
            tag_map = {'i1': 'years', 'i2': 'education', 'i3': 'people'}
            tag_dict = {'years': '', 'education': '', 'people': ''}
            for tag in jtag:
                span_class = tag.xpath('em/@class')[0].strip()
                if span_class not in tag_map.keys():continue
                tag_dict[tag_map[span_class]] = tag.xpath('text()')[0].strip()

            jd_list = html.xpath('//div[@class="bmsg job_msg inbox"]/text()')
        except IndexError as e:
            return
        tmp = company_details.split('|')
        company_type = ''
        company_people = ''
        company_field = ''
        tmp_len = len(tmp)
        if tmp_len == 3:
            company_type = tmp[0].strip()
            company_people = tmp[1].strip()
            company_field = tmp[2].strip()
        jd_list = [line.strip() for line in jd_list if line.strip() != '']
        jd = '\n'.join(jd_list)
        responsibility = ''
        specification = ''
        segment = 0
        for line in jd_list:
            if re.match(u'^[(（]?\d[）).、]', line):
                if segment == 0:
                    responsibility += line
                elif segment == 1:
                    specification += line
            elif responsibility != '':
                segment += 1
                if segment == 2: break
        segment = -1
        if responsibility == '' or specification == '':
            responsibility = ''
            specification = ''
            for line in jd_list:
                if re.search(u'[:：]$', line) or len(line) <= 5:
                    segment += 1
                    if segment == 2: break
                    continue
                if segment == 0:
                    responsibility += line
                elif segment == 1:
                    specification += line
        if responsibility == '' or specification == '':
            specification = responsibility
            responsibility = ''
            self.neglect += 1
        lock.acquire()
        #print self.id, title, district, salary, company, company_type, company_people, company_field
        #print years, education, people
        #print jd
        #print responsibility, '\n', specification
        try:
            self.pl.save(self.keyword if self.keyword != 'c++' else 'cpp', [self.id, title, district, salary, company, company_type, company_people, company_field,
                                        tag_dict['years'], tag_dict['education'], tag_dict['people'], responsibility, specification])
        except UnicodeEncodeError:
            pass
        self.id += 1
        if self.id % 100 == 0:
            print self.id
            time.sleep(0.5)
        lock.release()

    def start(self, jobarea, keyword, exactly=True):
        self.exactly = exactly
        self.pl.create_tb(keyword if keyword != 'c++' else 'cpp')
        # get area number
        with open('area_array.txt') as f:
            for line in f:
                number, area = line.split(':')
                encoding = chardet.detect(area)['encoding']
                area = area.decode(encoding).strip()
                if area == jobarea:
                    break
        print number, keyword
        self.keyword = keyword
        base_url = 'http://search.51job.com/jobsearch/search_result.php?fromJs=1&jobarea=%s&keyword=%s&keywordtype=2&lang=c&stype=2&postchannel=0000&fromType=1&confirmdate=9'
        url = base_url % (number, self.keyword if self.keyword != 'c++' else 'c%2B%2B')
        queue.put((url, self.get_link))
        for i in range(8):
            worker = DownloadWorker(queue)
            worker.daemon = True
            worker.start()
        queue.join()
        print '----------------------------------'
        print self.neglect

        self.pl.close_db()

if __name__ == '__main__':
    job51 = Job51()
    #job51.start(u'上海', 'python')
    #job51.start(u'上海', 'java')
    #job51.start(u'上海', 'c++')
    #job51.start(u'上海', u'人工智能')
    #job51.start(u'上海', u'大数据')
    job51.start(u'上海', u'web后端', exactly=False)
