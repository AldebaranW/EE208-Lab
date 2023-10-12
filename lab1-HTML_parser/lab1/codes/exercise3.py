# SJTU EE208

import re
import sys
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup


def parseZhihuDaily(content, url):
    zhihulist = list()
    ########################
    # write your code here
    ########################
    soup = BeautifulSoup(content, 'html.parser')

    sources = soup.findAll('div', {'class':'wrap'})
    for source in sources:
        box = source.contents[0].contents[0]
        hyper = box['href']
        hyper = urllib.parse.urljoin(url, hyper)

        img = box.contents[0]
        src = img['src']

        title = box.contents[1].string

        zhihu = [src, title, hyper]
        zhihulist.append(zhihu)
        # print(title)
        # print(hyper)
        # print(src)

    return zhihulist


def write_outputs(zhihus, filename):
    file = open(filename, "w", encoding='utf-8')
    for zhihu in zhihus:
        for element in zhihu:
            file.write(element)
            file.write('\t')
        file.write('\n')
    file.close()


def main():
    url = "http://daily.zhihu.com/"
    req = urllib.request.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0')
    content = urllib.request.urlopen(req).read()
    zhihus = parseZhihuDaily(content, url)
    write_outputs(zhihus, "result3.txt")


if __name__ == '__main__':
    main()
