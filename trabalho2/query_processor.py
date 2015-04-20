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
        self.queries = []
        self.logger = logging.getLogger(__name__)
        self.stemmer = PorterStemmer()
        
    def run(self):
        self.logger.info("Module starting...")
        self.logger.info("Reading configuration file: " + self.config_file_path)
        self._extract_paths()
        
        self.logger.info("Start parsing XML files")
        for path in self.input_paths:
            self._parse_xml_file(path)
        
    def write_output(self):
        
        queries_csv, expecteds_csv = self._export_csv()

        for i in range(len(models)):
            splited_queries_path = self.queries_path.split(".")
            q_path = ""
            if len(splited_queries_path) > 1:
                q_path = "%s-%s-%d.%s" % (splited_queries_path[0], models[i], i, ".".join(splited_queries_path[1:]) )
            else:
                q_path = "%s-%s-%d" % (splited_queries_path[0], models[i], i)
            
            self.logger.info("Writing queries: " + q_path)
            with open(q_path, "w") as queries_file:
                queries_file.write(queries_csv[i])
                
            splited_expecteds_path = self.expecteds_path.split(".")
            e_path = ""
            if len(splited_expecteds_path) > 1:
                e_path = "%s-%s-%d.%s" % (splited_expecteds_path[0], models[i], i, ".".join(splited_expecteds_path[1:]) )
            else:
                e_path = "%s-%s-%d" % (splited_expecteds_path[0], models[i], i)
             
            self.logger.info("Writing expecteds: " + e_path)
            with open(e_path, "w") as expecteds_file:
                expecteds_file.write(expecteds_csv[i])
        
    def _export_csv(self):
        queries_csvs = []
        expecteds_csvs = []
        for i in range(len(models)):
            
            queries_lines = []
            expecteds_lines = []
            for query_number, query_attr in self.queries[i].items():
                queries_lines.append( str(query_number) + CSV_SEPARATOR + str(query_attr['content']) )
                expecteds_lines.append( str(query_number) + CSV_SEPARATOR + str(query_attr['expecteds']) )
            
            queries_csvs.append("\n".join(queries_lines))
            expecteds_csvs.append("\n".join(expecteds_lines))
        return queries_csvs, expecteds_csvs 
           
    def _parse_query(self, query_content):
        normalized_content = unicodedata.normalize('NFKD', query_content).encode('ascii','ignore').upper().decode('utf-8')
        
        # Remove duplicated tokens (pound 1 for each term) and tokens with less than 2 characters    
        tokens = []
        tokens.append( set() )
        tokens.append( set() )
        for token in word_tokenize(normalized_content):
            if len(token) > 1:
                tokens[0].add(self.stemmer.stem(token))
                tokens[1].add(token)
                
        # Rebuild query string stemmed and no-stemmed
        return " ".join(tokens[0]), " ".join(tokens[1])
        
    def _compute_score(self, score):
        integer_score = 0
        # if a source score is more than 1, sum a vote
        for source_score in score:
            integer_score += (int(source_score) > 0)
        
        return integer_score
        
    def _parse_xml_file(self, file_name):
        xml_file = ET.parse(file_name).getroot()
        xml_queries = xml_file.findall('QUERY')
        
        # stemming
        self.queries.append( {} )
        # no stemming
        self.queries.append( {} )
        
        for query in xml_queries:
            query_number = int(query.find('QueryNumber').text.strip())
            stemmed_query_content, nostemmed_query_content = self._parse_query(query.find('QueryText').text)
            
            self.queries[0][query_number] = {}
            self.queries[1][query_number] = {}
            
            self.queries[0][query_number]['content'] = stemmed_query_content
            self.queries[1][query_number]['content'] = nostemmed_query_content
            
            self.queries[0][query_number]['expecteds'] = []
             
            records_items = query.find('Records').findall('Item')
            for item in records_items:
                item_recordnum = int(item.text.strip())
                item_score = self._compute_score(item.get('score'))
                
                self.queries[0][query_number]['expecteds'].append( (item_recordnum, item_score) )
          
            self.queries[0][query_number]['expecteds'].sort(key=lambda tup: tup[1], reverse=True)  
            self.queries[1][query_number]['expecteds'] = self.queries[0][query_number]['expecteds']
            
        self.logger.info("Parsing XML " + file_name + ": %d queries" % len(xml_queries) )  
            
                    
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
