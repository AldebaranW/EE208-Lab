# SJTU EE208

INDEX_DIR = "IndexFiles.index"

import sys, os, lucene, threading, time
from datetime import datetime
import math

# from java.io import File
from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, StringField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.pylucene.search.similarities import PythonSimilarity, PythonClassicSimilarity

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

class SimpleSimilarity(PythonClassicSimilarity):

    def lengthNorm(self, numTerms):
        return 1 / math.sqrt(numTerms)

    def tf(self, freq):
        return freq

    def sloppyFreq(self, distance):
        return 1 / (distance + 1)

    def idf(self, docFreq, numDocs):
        return math.log((numDocs - docFreq + 0.5) / (docFreq + 0.5))

    def idfExplain(self, collectionStats, termStats):
        return Explanation.match(1.0, "inexplicable", [])


class SimpleSimilarity2(PythonClassicSimilarity):

    def lengthNorm(self, numTerms):
        return 1 / numTerms

    def tf(self, freq):
        return math.sqrt(freq)

    def sloppyFreq(self, distance):
        return 1 / (distance + 1)

    def idf(self, docFreq, numDocs):
        return math.log((numDocs + 1) / (docFreq + 1))

    def idfExplain(self, collectionStats, termStats):
        return Explanation.match(1.0, "inexplicable", [])

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, root, storeDir):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        # store = SimpleFSDirectory(File(storeDir).toPath())
        store = SimpleFSDirectory(Paths.get(storeDir))
        analyzer = StandardAnalyzer()
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)

        # set a new similarity computing method
        config.setSimilarity(SimpleSimilarity2())

        writer = IndexWriter(store, config)

        self.indexDocs(root, writer)
        ticker = Ticker()
        print('commit index')
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print('done')

    def indexDocs(self, root, writer):

        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.NONE)  # Not Indexed
        
        t2 = FieldType()
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)  # Indexes documents, frequencies and positions.

        for root, dirnames, filenames in os.walk(root):
            for filename in filenames:
                if not filename.endswith('.txt'):
                    continue
                print("adding", filename)
                try:
                    path = os.path.join(root, filename)
                    file = open(path, encoding='gbk')
                    contents = file.read()
                    file.close()
                    doc = Document()
                    doc.add(Field("name", filename, t1))
                    doc.add(Field("path", path, t1))
                    if len(contents) > 0:
                        doc.add(Field("contents", contents, t2))
                    else:
                        print("warning: no content in %s" % filename)
                    writer.addDocument(doc)
                except Exception as e:
                    print("Failed in indexDocs:", e)

if __name__ == '__main__':
    lucene.initVM()#vmargs=['-Djava.awt.headless=true'])
    print('lucene', lucene.VERSION)
    # import ipdb; ipdb.set_trace()
    start = datetime.now()
    try:
        IndexFiles('testfolder', "index2")
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e