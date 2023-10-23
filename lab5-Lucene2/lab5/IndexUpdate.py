# SJTU EE208

import sys, os, lucene, time, re
from java.io import File
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, StringField, TextField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexReader ,IndexWriterConfig, Term, DirectoryReader, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher, TermQuery
from org.apache.lucene.util import Version
from bs4 import BeautifulSoup
import jieba

class IndexUpdate(object):
    def __init__(self, storeDir):
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        print('lucene', lucene.VERSION)
        self.dir = SimpleFSDirectory(File(storeDir).toPath())

        
    def testDelete(self, fieldName, searchString):
        config = IndexWriterConfig(self.getAnalyzer())
        config.setOpenMode(IndexWriterConfig.OpenMode.APPEND)
        writer = IndexWriter(self.dir, config)
        writer.deleteDocuments(Term(fieldName, searchString))
        writer.close()

        
    def testAdd(self, filepath, url):
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        
        t2 = FieldType()
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS) 

        config = IndexWriterConfig(self.getAnalyzer())
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
        writer = IndexWriter(self.dir, config)
        
        file = open(filepath, encoding='utf-8')
        contents = file.read()
        file.close()

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
        site = url.split('/')[2]
        site = ' '.join(site.split('.'))
        filename = filepath.split('/')[-1]
        print(filename)
        
        doc = Document()
        doc.add(Field("name", filename, t1))
        doc.add(Field("title", title, t1))
        doc.add(Field("url", url, t1))
        doc.add(Field("site", site, t2))
        if len(contents) > 0:
            contents = jieba.cut(contents, cut_all=False)
            contents = ' '.join(contents)
            doc.add(Field("contents", contents, t2))
        else:
            print("warning: no content in %s" % filename)
        writer.addDocument(doc)
        writer.close()

    def getHitCount(self, fieldName, searchString):
        reader = DirectoryReader.open(self.dir) #readOnly = True
        print('%s total docs in index' % reader.numDocs())
        
        searcher = IndexSearcher(reader) #readOnly = True
        t = Term(fieldName, searchString)
        query = TermQuery(t)
        hitCount = len(searcher.search(query, 50).scoreDocs)

        reader.close()
        print("%s total matching documents for %s\n---------------" \
              % (hitCount, searchString))
        return hitCount


    def getAnalyzer(self):
        return WhitespaceAnalyzer()

if __name__ == '__main__':
    try:
        fn = 'httpwww.baidu.com'
        index = IndexUpdate('index')
        print(index.getHitCount ('name', fn))

        # print('delete %s' % fn)
        # index.testDelete('name', fn)
        # index.getHitCount('name', fn)

        print('add %s' % fn)
        index.testAdd('html/%s' % fn, 'http://www.baidu.com')
        index.getHitCount('name', fn)
    except Exception as e:
        print("Failed: ", e)

