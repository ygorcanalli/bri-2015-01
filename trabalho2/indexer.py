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
        self.contents = {}
        self.document_id_array = None
        self.therm_document_matrix = None
        self.vectorizer = vectorizer
        self.logger = logging.getLogger(__name__)
        
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
                    if did not in self.contents:
                        self.contents[did] = ""
                    
                    self.contents[did] += token + " "
            
            self.document_id_array = []
            self.document_id_array.extend(self.contents.keys())
            
            i += 1
            
        self.logger.info("Rebuild %d documents from %d tokens" % (len(self.document_id_array), i) )
        
    def _build_therm_document_matrix(self):
        vec = self.vectorizer(ngram_range=(1,1))
        self.therm_document_matrix = vec.fit_transform(self.contents.values())    
        
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
        self.logger.info("Writing vector model: " + self.output_path)
        export = {}
        export["matrix"] = self.therm_document_matrix
        export["contents"] = self.contents
        with open(self.output_path, "wb") as file:
            dump(export, file)