# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 00:15:40 2015

@author: ygor
"""
from __init__ import *


class Indexer(object):
    
    def __init__(self, config_file_path, vectorizer):
        self.config_file_path = config_file_path
        self.input_path = None
        self.output_path = None
        self.contents = []
        self.document_id_array = None
        self.therm_document_matrix = []
        self.vectorizer = vectorizer
        self.logger = logging.getLogger(__name__)
        self.stemmer = PorterStemmer()
        
    def _extract_paths(self):
        config_file = open(self.config_file_path, "r")
        i = 1 
        
        for i in range(2):   
            line = config_file.readline()
            splited = line.split(COMMAND_SEPARATOR)
        
            if len(splited) != 2:
                raise Exception("Error parsing %s on line %d! Mal formated command." % (self.config_file_path, i))
            
            command = splited[0]
            path = splited[1].replace('\n', '')
            
            if command == READ_COMMAND:
                self.input_path = path
            elif command == WRITE_COMMAND:
                self.output_path = path
            else:
                raise Exception("Error parsing % on line %d! Unknow command \'%s\'" % (self.config_file_path, i, command))
        
        if self.input_path is None:  
            raise Exception("Error parsing %s! There's no read command." % self.config_file_path)
            
        if self.output_path is None:
            raise Exception("Error parsing %s! There's no write command." % self.config_file_path)
    
    def _rebuild_content(self):
        input_file = open(self.input_path, "r")
        i = 1 
        
        for line in input_file.readlines():
            splited = line.split(CSV_SEPARATOR)
            
            if len(splited) != 2:
                raise Exception("Error parsing %s on line %d! Mal formated csv." % (self.input_path, i))
            
            # get token upper case without numbers and special characters
            token = splited[0]
            token = re.sub('[^A-Z]+', '', token.upper())
            
            # get string removing lineend, breckets and spliting in commas  
            document_ids = splited[1][1:-2].split(", ")
            
            # only use tokens with two or more characters
            if len(token) > 1:
                for did in document_ids:
                    did = int(did)
                    # Stemming
                    self.contents.append({})
                    # No stemming
                    self.contents.append({})
                    if did not in self.contents[0]:
                        self.contents[0][did] = ""
                        self.contents[1][did] = ""
                    
                    self.contents[0][did] += self.stemmer.stem(token) + " "                    
                    self.contents[1][did] += token + " "                    
            
            self.document_id_array = []
            self.document_id_array.extend(self.contents[0].keys())
            
            i += 1
            
        self.logger.info("Rebuild %d documents from %d tokens" % (len(self.document_id_array), i) )
        
    def _build_therm_document_matrix(self):
        vec = self.vectorizer(ngram_range=(1,1))
        for i in range(len(models)):
            self.logger.info("Building vector model: %s" % models[i])
            matrix = vec.fit_transform(self.contents[i].values())
            self.therm_document_matrix.append(matrix)
        
    def run(self):
        self.logger.info("Module starting...")
        self.logger.info("Reading configuration file: " + self.config_file_path)
        self._extract_paths()
        self.logger.info("Rebuilding content from inverted index: " + self.input_path)
        self._rebuild_content()
        self.logger.info("Building vector model")
        self._build_therm_document_matrix()
        self.logger.info("Building vector model done")
    
    def write_output(self):
        for i in range(len(models)):
            splited_path = self.output_path.split(".")
            path = ""
            if len(splited_path) > 1:
                path = "%s-%s-%d.%s" % (splited_path[0], models[i], i, ".".join(splited_path[1:]) )
            else:
                path = "%s-%s-%d" % (splited_path[0], models[i], i)
                
            self.logger.info("Writing vector model: %s" % path )
            export = {}
            export["matrix"] = self.therm_document_matrix[i]
            export["contents"] = self.contents[i]
            with open(path, "wb") as file:
                dump(export, file)