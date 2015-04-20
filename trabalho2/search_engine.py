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
        self.contents = []
        self.queries = []
        self.queries_id_array = None
        self.document_id_array = None
        self.therm_document_matrix = []
        self.queries_matrix = []
        self.distances = []
        self.ranking = []
        self.vectorizer = vectorizer
        self.logger = logging.getLogger(__name__)
        
    def write_output(self):
        self.logger.info("Writing retrieval results: " + self.results_path)
        csvs = self._export_csv()
        for i in range(len(models)):
            splited_results_path = self.results_path.split(".")
            path = ""
            if len(splited_results_path) > 1:
                path = "%s-%s-%d.%s" % (splited_results_path[0], models[i], i, ".".join(splited_results_path[1:]) )
            else:
                path = "%s-%s-%d" % (splited_results_path[0], models[i], i)
            with open(path, "w") as results_file:
                results_file.write(csvs[i])
        
    def _export_csv(self):
        csvs = []
        for i in range(len(models)):
            results_lines = []
            for j in range(self.ranking[i].shape[0]):
                query_id = self.queries_id_array[j]
                query_results = []
                for k in range(self.ranking[i].shape[1]):
                    ranking = k
                    document_index = self.ranking[i][j][k]
                    document_id = self.document_id_array[document_index]   
                    distance = self.distances[i][j][document_index]
                    
                    query_results.append( (ranking, document_id, distance) )

                results_lines.append( str(query_id) + CSV_SEPARATOR + str(query_results) )
            csvs.append("\n".join(results_lines))
            
        return csvs

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
        for i in range(len(models)):
            self.distances.append(pairwise_distances(self.queries_matrix[i], self.therm_document_matrix[i], metric="cosine", n_jobs=4))
            self.ranking.append(np.argsort(self.distances[i], axis=1))
            
    def _build_queries_matrix(self):
        for i in range(len(models)):
            vec = self.vectorizer(ngram_range=(1,1))
            vec.fit(self.contents[i].values())
            self.queries_matrix.append(vec.transform(self.queries[i].values()))
        
    def _import_queries(self):
        for i in range(len(models)):
            splited_queries_path = self.queries_path.split(".")
            path = ""
            if len(splited_queries_path) > 1:
                path = "%s-%s-%d.%s" % (splited_queries_path[0], models[i], i, ".".join(splited_queries_path[1:]) )
            else:
                path = "%s-%s-%d" % (splited_queries_path[0], models[i], i)
                
            self.queries.append({})
            
            with open(path, "r") as queries_file:
                j = 1 
                for line in queries_file.readlines():
                    splited = line.split(CSV_SEPARATOR)
                    
                    if len(splited) != 2:
                        raise Exception("Error parsing %s on line %d! Mal formated csv." % (path, j))
                    
                    # get token upper case without numbers and special characters
                    query_id = int(splited[0])
                    query_content = splited[1]
                    
                    self.queries[i][query_id] = query_content
                
        self.queries_id_array = []
        self.queries_id_array.extend(self.queries[0].keys())
        
        self.logger.info("Reading queries: %d queries" % len(self.queries_id_array) ) 

    def _import_model(self):
        for i in range(len(models)):
            splited_model_path = self.model_path.split(".")
            path = ""
            if len(splited_model_path) > 1:
                path = "%s-%s-%d.%s" % (splited_model_path[0], models[i], i, ".".join(splited_model_path[1:]) )
            else:
                path = "%s-%s-%d" % (splited_model_path[0], models[i], i)
                
            with open(path, "rb") as file:
                imported = load(file)
            
            self.therm_document_matrix.append(imported["matrix"])
            self.contents.append(imported["contents"])
        self.document_id_array = []
        self.document_id_array.extend(self.contents[0].keys())
        
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
