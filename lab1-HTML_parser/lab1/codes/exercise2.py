# SJTU EE208

import re
import sys
import urllib.request

from bs4 import BeautifulSoup


def parseIMG(content):
    urlset = set()
    ########################
    # write your code here
    ########################

    soup = BeautifulSoup(content, 'html.parser')
    imgs = soup.findAll("img")
    for img in imgs:
        src = img['src']
        urlset.add(src)
    return urlset


def write_outputs(urls, filename):
    file = open(filename, 'w', encoding='utf-8')
    for i in urls:
        file.write(i)
        file.write('\n')
    file.close()


def main():
    url = "http://www.baidu.com"
    req = urllib.request.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0')
    content = urllib.request.urlopen(req).read()
    urlSet = parseIMG(content)
    write_outputs(urlSet, "result2.txt")


if __name__ == '__main__':
    main()
