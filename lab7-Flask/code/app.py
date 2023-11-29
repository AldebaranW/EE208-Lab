# SJTU EE208
INDEX_DIR = "IndexFiles.index"

import re

import sys, os, lucene,jieba
from java.io import File
from java.nio.file import Path
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.core import SimpleAnalyzer ,WhitespaceAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import BooleanClause
from org.apache.lucene.search.highlight import Highlighter, QueryScorer, SimpleFragmenter, SimpleHTMLFormatter
from typing import KeysView
from flask import Flask, redirect, render_template, request, url_for
import urllib.error
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

title = ''
url = ''
titles = []
urls = []
con = []

def parseCommand(command):
    command_dict = {'contents': ''}   
    command_dict['contents'] = ' '.join(jieba.cut(command))
    return command_dict

def runs(searcher, analyzer,command):
    global title, url
    global titles, urls, con
    titles = []
    urls = []
    con = []
    while True:
        if command == '':
            return
        print ("Searching for:", command)
        command_dict = parseCommand(command)
        querys = BooleanQuery.Builder()
        for k, v in command_dict.items():
            query = QueryParser(k, analyzer).parse(v)
            querys.add(query, BooleanClause.Occur.MUST)
        scoreDocs = searcher.search(querys.build(), 50).scoreDocs
        print("%s total matching documents." % len(scoreDocs))
        query = QueryParser('contents', analyzer).parse(command)

        titlst = []
        urlst = []
        contentlist = []
        for scoreDoc in scoreDocs:
            doc = searcher.doc(scoreDoc.doc)
            title = doc.get('title')
            url = doc.get('url')
            contents = urllib.request.urlopen(url)
            soup =  BeautifulSoup(contents,features="html.parser")
            contents = ''.join(soup.findAll(text=True))
            contents = ' '.join(jieba.cut(contents))
            titlst.append(title)
            urlst.append(url)
            contentlist.append(contents)

        # for scoreDoc in scoreDocs:
        for i in range(len(urlst)):
            title = titlst[i]
            url = urlst[i]
            contents = contentlist[i]

            formatter = SimpleHTMLFormatter('"','"')           
            highlighter =  Highlighter(formatter, QueryScorer(query))   
            highlighter.setTextFragmenter(SimpleFragmenter(25))
            tmp = analyzer.tokenStream("contents",contents) 
            substring = highlighter.getBestFragment(tmp, contents)

            if substring !=None:
                con.append(substring)   
            else:
                continue
            titles.append(title)
            urls.append(url)
        break

app = Flask(__name__)
@app.route('/', methods=['POST', 'GET'])
def bio_data_form():
    if request.method == "POST":
        keyword = request.form['keyword']
        return redirect(url_for('result', keyword=keyword))
    return render_template("bio_form.html")


@app.route('/result', methods=['GET'])
def result():
    global titles, urls, con, last_search
    STORE_DIR = "index"
    vm.attachCurrentThread() 

    directory = SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher = IndexSearcher(DirectoryReader.open(directory))
    analyzer = SimpleAnalyzer()

    keyword = request.args.get('keyword')
    if keyword == '':
        keyword = last_search
    elif keyword != '':
        last_search = keyword
    keyword = ' '.join(jieba.cut(keyword))

    runs(searcher, analyzer, keyword)
    length = min(len(titles),len(urls))
    length = min(length,len(con))
    del searcher
    return render_template("result.html", keyword=keyword, length=length, urls=urls, title=titles, con=con)



if __name__ == '__main__':
    last_search = ''

    vm = lucene.initVM()

    app.run(debug=True,port = 8080)