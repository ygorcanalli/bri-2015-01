# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 15:54:24 2015

@author: ygorcanalli
"""
import unicodedata
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import word_tokenize
from pickle import dump, load
import xml.etree.ElementTree as ET
import re

GLI_CONFIG_FILE = 'GLI.CFG'
INDEX_CONFIG_FILE = 'INDEX.CFG'
READ_COMMAND = 'LEIA'
WRITE_COMMAND = 'ESCREVA'
COMMAND_SEPARATOR = '='
CSV_SEPARATOR = ' ; '

class Indexer(object):
    
    def __init__(self, config_file_path, vectorizer):
        self.config_file_path = config_file_path
        self.input_path = None
        self.output_path = None
        self.contents = {}
        self.document_id_array = None
        self.therm_document_matrix = None
        self.vectorizer = vectorizer
        
    def _extract_paths(self):
        config_file = open(self.config_file_path, "r")
        i = 1 
        
        for i in range(2):   
            line = config_file.readline()
            splited = line.split(COMMAND_SEPARATOR)
        
            if len(splited) != 2:
                raise Exception("Error parsing %s on line %d! Mal formated command." % (self.config_file_path, i))
            
            command = splited[0]
            path = splited[1]
            
            if command == READ_COMMAND:
                self.input_path = path
            elif command == WRITE_COMMAND:
                self.output_path = path
            else:
                raise Exception("Error parsing % on line %d! Unknow command \'%s\'" % (self.config_file_path, i, command))
        
        if len(self.input_path) is None:  
            raise Exception("Error parsing %s! There's no read command." % self.config_file_path)
            
        if self.output_path is None:
            raise Exception("Error parsing %s! There's no write command." % self.config_file_path)
    
    def _rebuild_content(self):
        config_file = open(self.input_path, "r")
        i = 1 
        
        for line in config_file.readlines():
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
        
    def _build_therm_document_matrix(self):
        vec = self.vectorizer(ngram_range=(1,1))
        self.therm_document_matrix = vec.fit_transform(self.contents.values())
        
        
    def run(self):
        self._extract_paths()
        self._rebuild_content()
        self._build_therm_document_matrix()
    
    def export_model(self):
        export = {}
        export["matrix"] = self.therm_document_matrix
        export["contents"] = self.contents
        with open(self.output_path, "wb") as file:
            dump(export, file)
    
    def import_model(self):
        with open(self.output_path, "rb") as file:
            imported = load(file)
        
        self.therm_document_matrix = imported["matrix"]
        self.contents = imported["contents"]
        self.document_id_array = []
        self.document_id_array.extend(self.contents.keys())
            
        

class InvertedIndexGenerator(object):
    
    def __init__(self, config_file_path):
        self.inverted_index = InvertedIndex()
        self.config_file_path = config_file_path
        self.input_paths = []
        self.output_path = None
    
    def _parse_xml_file(self, file_name):
        xml_file = ET.parse(file_name).getroot()
        records = xml_file.findall('RECORD')
        
        for record in records:
            recordnum = int(record.find('RECORDNUM').text.strip())
            abstract = record.find('ABSTRACT')
            extract = record.find('EXTRACT')
            if abstract is not None:
                self.inverted_index.parse_document(recordnum, abstract.text)
            elif extract is not None:
                self.inverted_index.parse_document(recordnum, extract.text)
            else:
                print("%s: recordnum %s has no abstract or extract!" % (file_name, recordnum))
    
    def _extract_paths(self):
        config_file = open(self.config_file_path, "r")
        i = 1 
        
        for line in config_file.readlines():
            splited = line.split(COMMAND_SEPARATOR)
        
            if len(splited) != 2:
                raise Exception("Error parsing %s on line %d! Mal formated command." % (self.config_file_path, i))
            
            command = splited[0]
            path = splited[1]
            
            if command == READ_COMMAND:
                self.input_paths.append(path)
            elif command == WRITE_COMMAND:
                self.output_path = path
                break
            else:
                raise Exception("Error parsing % on line %d! Unknow command \'%s\'." % (self.config_file_path, i, command))
                      
            i += 1
        
        if len(self.input_paths) == 0:  
            raise Exception("Error parsing %s! There's no read commands." % self.config_file_path)
            
        if self.output_path is None:
            raise Exception("Error parsing %s! There's no write command." % self.config_file_path)
        
    def run(self):
        self._extract_paths()
        
        for path in self.input_paths:
            self._parse_xml_file(path.replace('\n', ''))
            
    def write_output(self):
        output_file = open(self.output_path, "w")
        output_file.write(self.inverted_index.export_csv())
    
class InvertedIndex(object):
        
    def __init__(self):
        self.index = {}
        
    def parse_document(self, document_id, content):
        normalized_content = unicodedata.normalize('NFKD', content).encode('ascii','ignore').upper().decode('utf-8')
        
        for token in word_tokenize(normalized_content):
            self._insert_token(token, document_id)
            
    def _insert_token(self, token, document_id):
        if not token in self.index:
            self.index[token] = []            
        self.index[token].append(document_id)
        
    def export_csv(self):
        csv_lines = []
        for token, document_list in self.index.items():
            csv_lines.append( str(token) + CSV_SEPARATOR + str(document_list) )
        return "\n".join(csv_lines)
           
    
        
gli = InvertedIndexGenerator(GLI_CONFIG_FILE)
gli.run()
gli.write_output()

index = Indexer(INDEX_CONFIG_FILE, TfidfVectorizer)
index.run()
index.export_model()

        
