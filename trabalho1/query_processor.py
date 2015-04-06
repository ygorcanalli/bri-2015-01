# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 00:13:32 2015

@author: ygor
"""
from __init__ import *

class QueryProcessor(object):
    
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.input_paths = []
        self.queries_path = None
        self.expecteds_path = None
        self.queries = {}
        
    def run(self):
        self._extract_paths()
        
        for path in self.input_paths:
            self._parse_xml_file(path)
        
    def write_output(self):
        queries_csv, expecteds_csv = self._export_csv()
        
        with open(self.queries_path, "w") as queries_file:
            queries_file.write(queries_csv)
            
        with open(self.expecteds_path, "w") as expecteds_file:
            expecteds_file.write(expecteds_csv)
        
    def _export_csv(self):
        queries_lines = []
        expecteds_lines = []
        for query_number, query_attr in self.queries.items():
            queries_lines.append( str(query_number) + CSV_SEPARATOR + str(query_attr['content']) )
            expecteds_lines.append( str(query_number) + CSV_SEPARATOR + str(query_attr['expecteds']) )
            
        return "\n".join(queries_lines), "\n".join(expecteds_lines)
           
    def _parse_query(self, query_content):
        normalized_content = unicodedata.normalize('NFKD', query_content).encode('ascii','ignore').upper().decode('utf-8')
        
        # Remove duplicated tokens (pound 1 for each term) and tokens with less than 2 characters    
        tokens = set()
        for token in word_tokenize(normalized_content):
            if len(token) > 1:
                tokens.add(token)
                
        # Rebuild query string
        return " ".join(tokens)
        
    def _compute_score(self, score):
        integer_score = 0
        # if a source score is more than 1, sum a vote
        for source_score in score:
            integer_score += (int(source_score) > 0)
        
        return integer_score
        
    def _parse_xml_file(self, file_name):
        xml_file = ET.parse(file_name).getroot()
        xml_queries = xml_file.findall('QUERY')
        
        for query in xml_queries:
            query_number = int(query.find('QueryNumber').text.strip())
            query_content = self._parse_query(query.find('QueryText').text)
            
            self.queries[query_number] = {}
            self.queries[query_number]['content'] = query_content
            self.queries[query_number]['expecteds'] = []
            
            records_items = query.find('Records').findall('Item')
            for item in records_items:
                item_recordnum = int(item.text.strip())
                item_score = self._compute_score(item.get('score'))
                
                self.queries[query_number]['expecteds'].append( (item_recordnum, item_score) )
            
            self.queries[query_number]['expecteds'].sort(key=lambda tup: tup[1], reverse=True) 
            
                    
    def _extract_paths(self):
        config_file = open(self.config_file_path, "r")
        i = 1 
        
        for line in config_file.readlines():   
            splited = line.split(COMMAND_SEPARATOR)
        
            if len(splited) != 2:
                raise Exception("Error parsing %s on line %d! Mal formated command." % (self.config_file_path, i))
            
            command = splited[0]
            path = splited[1].replace('\n', '')
            
            if self.queries_path is None and command == READ_COMMAND:
                self.input_paths.append(path)
            elif command == QUERIES_COMMAND:
                self.queries_path = path
            elif command == EXPECTEDS_COMMAND:
                self.expecteds_path = path
                break
            else:
                raise Exception("Error parsing %s on line %d! Unknow command \'%s\'" % (self.config_file_path, i, command))
        
        if len(self.input_paths) == 0:  
            raise Exception("Error parsing %s! There's no read commands." % self.config_file_path)
            
        if self.queries_path is None:
            raise Exception("Error parsing %s! There's no queries command." % self.config_file_path)

        if self.expecteds_path is None:
            raise Exception("Error parsing %s! There's no expcteds command." % self.config_file_path)
