import sys

from __init__ import *
from inverted_index_generator import InvertedIndexGenerator
from indexer import Indexer
from query_processor import QueryProcessor
from search_engine import SearchEngine

def __main__(argv):
    
    gli = InvertedIndexGenerator(GLI_CONFIG_FILE)
    gli.run()
    gli.write_output()
    
    index = Indexer(INDEX_CONFIG_FILE, TfidfVectorizer)
    index.run()
    index.write_output()
    
    pc = QueryProcessor(PC_CONFIG_FILE)
    pc.run()
    pc.write_output()
    
    buscador = SearchEngine(BUSCA_CONFIG_FILE, TfidfVectorizer)
    buscador.run()
    buscador.write_output()

if __name__ == "__main__":
    __main__(sys.argv[1:])