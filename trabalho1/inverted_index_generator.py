# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 00:18:34 2015

@author: ygor
"""
from __init__ import *

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
        output_file.write(self.inverted_index.export_cvs())
    
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
        
    def export_cvs(self):
        csv_lines = []
        for token, document_list in self.index.items():
            csv_lines.append( str(token) + CSV_SEPARATOR + str(document_list) )
        return "\n".join(csv_lines)