# SJTU EE208

INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, threading, time
from datetime import datetime

# from java.io import File
from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, StringField, TextField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
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
            sys.stdout.write('.')
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
        print('commit index')
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print('done')

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
        with open(indexfile, 'r') as f:
            for line in f.readlines(): 
                line = line.split()
                filenames.append(line[1])
                urls.append(line[0])

        for i in range(len(filenames)):
            try:
                filename = filenames[i]
                path = os.path.join(root, filename)
                file = open(path, encoding='utf-8')
                contents = file.read()
                file.close()
                if contents == None:
                    continue

                soup = BeautifulSoup(contents, 'html.parser')
                title = soup.find("head").find("title").string
                encoding = [i.get('charset') for i in soup.find("head").findAll('meta') if i.get('charset') != None]
                if not len(encoding):
                    encoding = 'utf-8'
                else:
                    encoding = encoding[0]
                if encoding.upper() != "UTF-8":
                    contents = contents.encode('GBK')

                contents = re.sub("[^\u4e00-\u9fa5]", "", contents)
                site = urls[i].split('/')[2]
                site = ' '.join(site.split('.'))
                
                doc = Document()
                doc.add(Field("name", filename, t1))
                doc.add(Field("path", path, t1))
                doc.add(Field("title", title, t1))
                doc.add(Field("url", urls[i], t1))
                doc.add(Field("site", site, t2))
                if len(contents) > 0:
                    contents = jieba.cut(contents, cut_all=False)
                    contents = ' '.join(contents)
                    doc.add(Field("contents", contents, t2))
                else:
                    print("warning: no content in %s" % filename)
                
                writer.addDocument(doc)
            except Exception as e:
                continue

if __name__ == '__main__':
    lucene.initVM()#vmargs=['-Djava.awt.headless=true'])
    print('lucene', lucene.VERSION)
    # import ipdb; ipdb.set_trace()
    start = datetime.now()
    try:
        IndexFiles('html', "index", 'index.txt')
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e
