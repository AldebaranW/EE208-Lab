# SJTU EE208

import os
import re
import string
import sys
import urllib.error
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup


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
        content = urllib.request.urlopen(request, timeout=5).read()
    except:
        pass
#
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


def union_dfs(a, b):
    for e in b:
        if e not in a:
            a.append(e)


def union_bfs(a, b):
    for e in b:
        if e not in a:
            a.insert(0, e)


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


def crawl(seed, method, max_page):
    tocrawl = [seed]
    crawled = []
    graph = {}
    # count = 0

    while tocrawl:
        page = tocrawl.pop()
        if page not in crawled:
            print(page)
            content = get_page(page)
            add_page_to_folder(page, content)
            outlinks = get_all_links(content, page)
            globals()['union_%s' % method](tocrawl, outlinks)
            crawled.append(page)
            graph[page] = outlinks

            if len(crawled) >= max_page:
                break

    return graph, crawled


if __name__ == '__main__':

    seed = "http://www.sjtu.edu.cn"
    # seed = sys.argv[1]
    method = "dfs"
    # method = sys.argv[2]
    max_page = 10
    # max_page = sys.argv[3]

    graph, crawled = crawl(seed, method, max_page)

