# SJTU EE208

INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, threading, time
from datetime import datetime

# from java.io import File
from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import (
    Document,
    Field,
    FieldType,
    StringField,
    TextField,
)
from org.apache.lucene.index import (
    FieldInfo,
    IndexWriter,
    IndexWriterConfig,
    IndexOptions,
)
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from bs4 import BeautifulSoup
import jieba
import re

"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""


class Ticker(object):
    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(1.0)


class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, root, storeDir, indexfile):
        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        # store = SimpleFSDirectory(File(storeDir).toPath())
        store = SimpleFSDirectory(Paths.get(storeDir))
        analyzer = WhitespaceAnalyzer()
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.indexDocs(root, writer, indexfile)
        ticker = Ticker()
        print("commit index")
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print("done")

    def indexDocs(self, root, writer, indexfile):
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.NONE)

        t2 = FieldType()
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        filenames = []
        urls = []
        with open(indexfile, "r") as f:
            for line in f.readlines():
                line = line.split()
                filenames.append(line[1])
                urls.append(line[0])

        for i in range(len(filenames)):
            print(i)
            try:
                filename = filenames[i]
                path = os.path.join(root, filename)
                file = open(path, encoding="utf-8")
                contents = file.read()
                file.close()

                soup = BeautifulSoup(contents, "html.parser")
                site_title = soup.find("head").find("title").string

                encoding = [
                    i.get("charset")
                    for i in soup.find("head").findAll("meta")
                    if i.get("charset") != None
                ]
                if not len(encoding):
                    encoding = "utf-8"
                else:
                    encoding = encoding[0]
                if encoding.upper() != "UTF-8":
                    contents = contents.encode("GBK")

                spans = soup.findAll("span", {"class": "bg"})
                body = soup.find("div", {"class": "post_body"})
                if body != None:
                    imgs = soup.findAll("img")
                    for img in imgs:
                        src = img.get("src")
                        title = img.get("alt")

                        if title == None:
                            try:
                                title = img.parent.find("a").get("title")
                            except:
                                continue

                        title = " ".join(jieba.cut(title, cut_all=True))

                        doc = Document()
                        doc.add(Field("contents", title, t2))
                        doc.add(Field("imgurl", src, t1))
                        doc.add(Field("url", urls[i], t1))
                        doc.add(Field("title", site_title, t1))
                        writer.addDocument(doc)

                        print(src, title, urls[i])
                        print("------------------------------")
                else:
                    for span in spans:
                        try:
                            hyper = span.parent
                            img = hyper.find("img")
                            if img.get("alt") != None:
                                title = img.get("alt")
                            else:
                                if hyper.find("h3") != None:
                                    if hyper.find("h3").find("a") == None:
                                        title = hyper.find("h3").string
                                    else:
                                        title = hyper.find("h3").find("a").string
                                elif hyper.find("h2") != None:
                                    if hyper.find("h2").find("a") == None:
                                        title = hyper.find("h2").string
                                    else:
                                        title = hyper.find("h2").find("a").string

                            src = img.get("src")
                            if src == None:
                                src = img.get("data-original")
                            if src == None:
                                src = img.get("lazy-src")

                            title = " ".join(jieba.cut(title, cut_all=True))
                            doc = Document()
                            doc.add(Field("contents", title, t2))
                            doc.add(Field("imgurl", src, t1))
                            doc.add(Field("url", urls[i], t1))
                            doc.add(Field("title", site_title, t1))
                            writer.addDocument(doc)
                            print(src, title, urls[i])
                            print("------------------------------")
                        except:
                            continue

            except Exception as e:
                continue


if __name__ == "__main__":
    lucene.initVM()  # vmargs=['-Djava.awt.headless=true'])
    print("lucene", lucene.VERSION)
    # import ipdb; ipdb.set_trace()
    start = datetime.now()
    try:
        IndexFiles("html", "pic_index", "index.txt")
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e
