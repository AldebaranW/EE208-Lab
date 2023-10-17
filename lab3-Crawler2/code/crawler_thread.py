# SJTU EE208

import os
import re
import string
import sys
import urllib.error
import urllib.parse
import urllib.request
import queue
import threading
import time

from bs4 import BeautifulSoup
lock = threading.Lock()

def valid_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s


def get_page(page):
    content = ''

    header = ("User-Agent", "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110Safari/537.36")
    request = urllib.request.Request(page)
    request.add_header(*header)
    try:
        content = urllib.request.urlopen(request, timeout=5).read().decode('utf-8')
    except:
        pass
    return content


def get_all_links(content, page):
    links = []

    soup = BeautifulSoup(content, 'html.parser')
    hypers = soup.findAll('a', {'href' : re.compile('^http|^/')})
    for hyper in hypers:
        href = hyper["href"]
        if href[:4] == 'http':
            links.append(href)
        else:
            links.append(urllib.parse.urljoin(page, href))

    return links

def add_page_to_folder(page, content):  # 将网页存到文件夹里，将网址和对应的文件名写入index.txt中
    index_filename = 'index.txt'  # index.txt中每行是'网址 对应的文件名'
    folder = 'html'  # 存放网页的文件夹
    filename = valid_filename(page)  # 将网址变成合法的文件名
    index = open(index_filename, 'a')
    index.write(str(page.encode('ascii', 'ignore'))[1:] + '\t' + filename + '\n')
    # Notice here: 由于依赖库更新，如果在这里写入txt时存在数据类型不符的bug，
    # 尝试将page.encode()的byte类型数据转换成string后写入txt文件。
    
    index.close()
    if not os.path.exists(folder):  # 如果文件夹不存在则新建
        os.mkdir(folder)
    f = open(os.path.join(folder, filename), 'w')
    f.write(str(content))  # 将网页存入文件
    f.close()


def crawl(seed, max_page):
    tocrawl = queue.Queue()
    tocrawl.put(seed)
    crawled = []
    graph = {}
    # count = 0
    NUM = 4
    for _ in range(NUM):
        time.sleep(0.5)
        t = threading.Thread(target=crawl_per_thread, args=(tocrawl, crawled, graph, max_page))
        t.setDaemon(True)
        t.start()
    
    t.join()
    return graph, crawled
    
def crawl_per_thread(tocrawl, crawled, graph, maxpage):
    if not tocrawl:
        time.sleep(0.5)
    while len(crawled) <= maxpage:
        try:
            page = tocrawl.get()
            if page not in crawled:
                print(page)
                content = get_page(page)
                add_page_to_folder(page, content)
                outlinks = get_all_links(content, page)
                for outlink in outlinks:
                    tocrawl.put(outlink)
                lock.acquire()
                crawled.append(page)
                graph[page] = outlinks
                lock.release()
        except:
            pass
    
    return
       

if __name__ == '__main__':

    try:
        seed = sys.argv[1]
        max_page = sys.argv[2]
    except:
        seed = "http://www.baidu.com"
        max_page = 1000
    graph, crawled = crawl(seed, max_page)

