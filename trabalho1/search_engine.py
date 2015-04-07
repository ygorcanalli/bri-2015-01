# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 17:18:36 2015

@author: ygor
"""
from __init__ import *
from pprint import pformat

class SearchEngine(object):
    
    def __init__(self, config_file_path, vectorizer):
        self.config_file_path = config_file_path
        self.model_path = None
        self.queries_path = None
        self.results_path = None
        self.contents = {}
        self.queries = {}
        self.queries_id_array = None
        self.document_id_array = None
        self.therm_document_matrix = None
        self.queries_matrix = None
        self.distances = None
        self.ranking = None
        self.vectorizer = vectorizer
        self.logger = logging.getLogger(__name__)
        
    def write_output(self):
        self.logger.info("Writing retrieval results: " + self.results_path)
        with open(self.results_path, "w") as results_file:
            results_file.write(self._export_csv())
        
    def _export_csv(self): 
        results_lines = []
        for i in range(self.ranking.shape[0]):
            query_id = self.queries_id_array[i]
            query_results = []
            for j in range(self.ranking.shape[1]):
                ranking = j
                document_index = self.ranking[i][j]
                document_id = self.document_id_array[document_index]   
                distance = self.distances[i][document_index]
                
                query_results.append( (ranking, document_id, distance) )

            results_lines.append( str(query_id) + CSV_SEPARATOR + str(query_results) )
            
        return  "\n".join(results_lines)

    def run(self):
        self.logger.info("Module starting...")
        self.logger.info("Reading configuration file: " + self.config_file_path)
        self._extract_paths()
        self.logger.info("Reading vector model: " + self.model_path)
        self._import_model()
        self.logger.info("Reading queries: " + self.queries_path)
        self._import_queries()
        self.logger.info("Building queries matrix")
        self._build_queries_matrix()
        self.logger.info("Executing retrieval")
        self._execute_retrieval()
        self.logger.info("Executing retrieval done")
        
    def _execute_retrieval(self):
        self.distances = pairwise_distances(self.queries_matrix, self.therm_document_matrix, metric="cosine", n_jobs=4)
        #similarities = np.ones(self.distances.shape) - self.distances
        self.ranking = np.argsort(self.distances, axis=1)
        #pprint(queries_ranking)
        
    def _build_queries_matrix(self):
        vec = self.vectorizer(ngram_range=(1,1))
        vec.fit(self.contents.values())
        self.queries_matrix = vec.transform(self.queries.values())
        
    def _import_queries(self):
        queries_file = open(self.queries_path, "r")
        i = 1 
        
        for line in queries_file.readlines():
            splited = line.split(CSV_SEPARATOR)
            
            if len(splited) != 2:
                raise Exception("Error parsing %s on line %d! Mal formated csv." % (self.input_path, i))
            
            # get token upper case without numbers and special characters
            query_id = int(splited[0])
            query_content = splited[1]
            
            self.queries[query_id] = query_content
        
        self.queries_id_array = []
        self.queries_id_array.extend(self.queries.keys())
        
        self.logger.info("Reading queries: %d queries" % len(self.queries_id_array) ) 

    def _import_model(self):
        with open(self.model_path, "rb") as file:
            imported = load(file)
        
        self.therm_document_matrix = imported["matrix"]
        self.contents = imported["contents"]
        self.document_id_array = []
        self.document_id_array.extend(self.contents.keys())
        
        self.logger.info("Reading vector model: %d documents" % len(self.document_id_array) ) 
        
    def _extract_paths(self):
        config_file = open(self.config_file_path, "r")
        i = 1 
        
        for line in config_file.readlines():   
            splited = line.split(COMMAND_SEPARATOR)
        
            if len(splited) != 2:
                raise Exception("Error parsing %s on line %d! Mal formated command." % (self.config_file_path, i))
            
            command = splited[0]
            path = splited[1].replace('\n', '')
            
            if command == MODEL_COMMAND:
                self.model_path = path
            elif command == QUERIES_COMMAND:
                self.queries_path = path
            elif command == RESULTS_COMMAND:
                self.results_path = path
                break
            else:
                raise Exception("Error parsing %s on line %d! Unknow command \'%s\'" % (self.config_file_path, i, command))
        
        if self.model_path is None:  
            raise Exception("Error parsing %s! There's no model command." % self.config_file_path)
            
        if self.queries_path is None:
            raise Exception("Error parsing %s! There's no queries command." % self.config_file_path)

        if self.results_path is None:
            raise Exception("Error parsing %s! There's no results command." % self.config_file_path)
