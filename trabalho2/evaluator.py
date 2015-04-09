# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 06:56:19 2015

@author: ygor
"""

from __init__ import *

class Evaluator(object):
    
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.expecteds_paths = []
        self.results_paths = []
        self.expecteds_documents = []
        self.results_matrix = []
        self.precisions_at_k = []
        self.recalls_at_k = []
        
    def run(self):
        self._extract_paths()
        
        for i in range(len(self.results_paths)):
            self._parse_csv_files(self.expecteds_paths[i], self.results_paths[i])
        
        self._mesure_precision_recall()
        print(self._get_precisions_at_k(10))
        print(self._get_map())
        for interpolated in self._interpolated_precision_recall():
            print(i, interpolated)
    
    def _interpolated_precision_recall(self):
        i = 0
        interpolated_precision_recalls = []
        for i in range(len(self.expecteds_paths)):
            precisions = self.precisions_at_k[i]
            recalls = self.recalls_at_k[i]
            mean_precisions = np.mean(precisions, axis=0)
            mean_recalls = np.mean(recalls, axis=0)
            
            interpolated_precision_recall = np.zeros(11)
            
            for recall_level in range(0,11):
                precision_at_k = 0
                for k in range(len(mean_recalls)):
                    if recall_level <= mean_recalls[k]*10:
                        precision_at_k = max(precision_at_k, mean_precisions[k])
                interpolated_precision_recall[recall_level] = precision_at_k
            interpolated_precision_recalls.append(interpolated_precision_recall)
            
        return interpolated_precision_recalls
                
                
            
            
            
        return pak
        
    def _get_precisions_at_k(self, k):
        pak = []
        for precisions in self.precisions_at_k:
            pak.append(np.mean(precisions[:, (k-1)]))
        return pak

    def _get_map(self):
        maps = []
        for precisions in self.precisions_at_k:
            maps.append(np.mean(precisions))
        return maps
        
    def _mesure_precision_recall(self):
        
        for i in range(len(self.results_matrix)):
            n_queries = len(self.results_matrix[i])
            
            n_documents = 0
            
            for n in self.results_matrix[i].values():
                if len(n) > n_documents:
                    n_documents = len(n)
                    
            queries_numbers = []
            queries_numbers.extend(self.results_matrix[i].keys())
            
            pak = np.zeros( (n_queries, n_documents) )
            rak = np.zeros( (n_queries, n_documents) )    
            
            for j in range(n_queries):
                query_number = queries_numbers[j]
                relevants = len(self.expecteds_documents[i][query_number])
                retrived = len(self.results_matrix[i][query_number])
                relevants_retrived = 0
    
                for k in range(retrived):

                    if self.results_matrix[i][query_number][k] in self.expecteds_documents[i][query_number]:
                        relevants_retrived += 1
                    pak[j][k] = relevants_retrived / (k + 1)
                    rak[j][k] = relevants_retrived / relevants
                    
            self.precisions_at_k.append(pak)
            self.recalls_at_k.append(rak)
        
    def _extract_paths(self):
        config_file = open(self.config_file_path, "r")
        lines = config_file.readlines()
        
        if len(lines) % 2 != 0:
            raise Exception("Error parsing %s! Every expected command must be followed by a result command." % self.config_file_path)
        
        for i in range(len(lines)):
            line = lines[i]
            splited = line.split(COMMAND_SEPARATOR)
        
            if len(splited) != 2:
                raise Exception("Error parsing %s on line %d! Mal formated command." % (self.config_file_path, i))
            
            command = splited[0]
            path = splited[1].replace('\n', '')
            
            if (i % 2 == 0) and command == EXPECTEDS_COMMAND:
                self.expecteds_paths.append(path)
            elif (i % 2 == 1) and command == RESULTS_COMMAND:
                self.results_paths.append(path)
            else:
                raise Exception("Error parsing %s on line %d! Every expected command must be followed by a result command." % (self.config_file_path, i))
        
        if len(self.expecteds_paths) == 0:  
            raise Exception("Error parsing %s! There's no expected commands." % self.config_file_path)
            
        if len(self.results_paths) == 0:  
            raise Exception("Error parsing %s! There's no result commands." % self.config_file_path)
            
    def _parse_csv_files(self, expecteds_file_name, results_file_name):
        expecteds_csv_file = open(expecteds_file_name, "r")
        relevants = {}
        
        for line in expecteds_csv_file.readlines():
            splited = line.split(CSV_SEPARATOR)
            
            if len(splited) != 2:
                raise Exception("Error parsing %s on line %d! Mal formated csv." % (expecteds_file_name, i))
            
            query_number = int(splited[0])
            relevants[query_number] = []
             
            # Extract the list values
            list_string = re.sub('[^0-9 ]+', '', splited[1])   
            values_list = list_string.split(" ")
            for i in range(0, len(values_list) - 1, 2):
                if int(values_list[i+1]) != 0:
                    relevants[query_number].append(int(values_list[i]))
                    
        self.expecteds_documents.append(relevants)
        
        results_csv_file = open(results_file_name, "r")
        
        queries_results = {}
        for line in results_csv_file.readlines():
            splited = line.split(CSV_SEPARATOR)
            
            if len(splited) != 2:
                raise Exception("Error parsing %s on line %d! Mal formated csv." % (results_file_name, i))
            
            # get token upper case without numbers and special characters
            query_number = int(splited[0])
            queries_results[query_number] = []
            
            # Extract the list values
            list_string = re.sub('[\\[\\]\\,\\(\\)]', '', splited[1])
            values_list = list_string.split(" ")
            
            for i in range(1, len(values_list), 3):
                queries_results[query_number].append(int(values_list[i]))
                    
        self.results_matrix.append(queries_results)