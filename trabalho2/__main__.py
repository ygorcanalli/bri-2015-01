import sys

from __init__ import *
from inverted_index_generator import InvertedIndexGenerator
from indexer import Indexer
from query_processor import QueryProcessor
from search_engine import SearchEngine
from evaluator import Evaluator

#%%

def __main__(argv):
    #%%
    logger = logging.getLogger(__name__)
    logger.info("VECTOR MODEL INFORMATION RETRIEVAL SYSTEM START")    
    
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
    #%%
    avaliador = Evaluator(AVAL_CONFIG_FILE)
    avaliador.run()
    avaliador.write_output()
    
    logger.info("VECTOR MODEL INFORMATION RETRIEVAL SYSTEM DONE")     
    #%%
if __name__ == "__main__":
    __main__(sys.argv[1:])