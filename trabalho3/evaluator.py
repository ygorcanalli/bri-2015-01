# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 06:56:19 2015

@author: ygor
"""
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from pylab import setp
import re

models = ['StemmingNLTK', 'StemmingLucene']
colors = ["darkgrey", 'darkgreen']

AVAL_CONFIG_FILE = 'AVAL.CFG'
COMMAND_SEPARATOR = '='
CSV_SEPARATOR = ' ; '
RESULTS_COMMAND = 'RESULTADOS'
EXPECTEDS_COMMAND = 'ESPERADOS'

class Evaluator(object):
    
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.expecteds_paths = []
        self.results_paths = []
        self.expecteds_documents = []
        self.expecteds_relevances = []
        self.results_matrix = []
        self.precisions_at_k = []
        self.recalls_at_k = []
        self.queries_number = []
        
        self.precisions_at_10 = None
        self.maps = None
        self.precision_recall_curves = None
        self.dcgs = None
        self.ndcgs = None
        self.f1s = None
        
    def run(self):
        self._extract_paths()
        
        for i in range(len(self.results_paths)):
            self._parse_csv_files(self.expecteds_paths[i], self.results_paths[i])
        
        self._mesure_precision_recall()    
        self.precisions_at_10 = self._get_precisions_at_k(10)
        self.maps = self._get_MAP()
        self.precision_recall_curves = self._get_interpolated_precision_recall()
        #self.dcgs, self.ndcgs = self._get_discounted_cumulative_gain()   
        #self.f1s = self._get_f1()
        
        
    def write_output(self):
        self._plot_pat10(self.precisions_at_10)
        self._plot_MAP(self.maps)
        self._plot_precision_recall_curve(self.precision_recall_curves)
        #self._plot_dcg(self.dcgs)
        #self._plot_ndcg(self.ndcgs)
        #self._plot_f1(self.f1s)
        
        precisions_at_10_csvs = self._export_precisions_at_10_csv()
        precision_recall_curves_csv = self._export_precision_recall_curves_csv()
        #gcd_csvs = self._export_gcd_csv()
        #ngcd_csv = self._export_ngcd_csv()
        #f1_csv = self._export_f1_csv()
        
        for i in range(len(models)):
            with open("data/pat10-%s-%d.csv" % (models[i], i), "w") as file:
                file.write(precisions_at_10_csvs[i])
            with open("data/interpolated_precision_recall-%s-%d.csv" % (models[i], i), "w") as file:
                file.write(precision_recall_curves_csv[i])
            #with open("data/dcg-%s-%d.csv" % (models[i], i), "w") as file:
            #    file.write(gcd_csvs[i])
            #with open("data/ndcg-%s-%d.csv" % (models[i], i), "w") as file:
            #    file.write(ngcd_csv[i])
            #with open("data/f1-%s-%d.csv" % (models[i], i), "w") as file:
            #    file.write(f1_csv[i])
                
        with open("RELATORIO.TXT", "w") as file:
            file.write(self._export_report())
                
    def _export_report(self):
        report = "============MAP============\n"
        for i in range(len(models)):
            report += "---------%s---------\n" % models[i]
            report += str(self.maps[i]) + "\n"
            
        report += "\n============11 Points precision recall curve============\n"
        for i in range(len(models)):
            report += "\n---------%s---------\n" % models[i]
            report += str(self.precision_recall_curves[i]) + "\n"
            
        report += "\n============Precision@10============\n"
        for i in range(len(models)):
            report += "\n---------%s---------\n" % models[i]
            for j in range(np.shape(self.precisions_at_10[i])[0]):
                report += str(self.queries_number[j]) + CSV_SEPARATOR + str(self.precisions_at_10[i][j]) + "\n"
        '''        
        report += "\n============DCG============\n"
        for i in range(len(models)):
            report += "\n---------%s---------\n" % models[i]
            for j in range(np.shape(self.dcgs[i])[0]):
                report += str(self.queries_number[j]) + CSV_SEPARATOR + str(self.dcgs[i][j][-1]) + "\n"

        report += "\n============nDCG============\n"
        for i in range(len(models)):
            report += "\n---------%s---------\n" % models[i]
            for j in range(np.shape(self.ndcgs[i])[0]):
                report += str(self.queries_number[j]) + CSV_SEPARATOR + str(self.ndcgs[i][j][-1]) + "\n"
                
        report += "\n============F1============\n"
        for i in range(len(models)):
            report += "\n---------%s---------\n" % models[i]
            for j in range(np.shape(self.f1s[i])[0]):
                report += str(self.queries_number[j]) + CSV_SEPARATOR + str(self.f1s[i][j][-1]) + "\n"
        '''        
        return report
        
        

    def _export_precisions_at_10_csv(self):
        csvs = []
        for i in range(len(models)):
            lines = []
            
            for j in range(np.shape(self.precisions_at_10[i])[0]):
                lines.append( str(self.queries_number[j]) + CSV_SEPARATOR + str(self.precisions_at_10[i][j]) )

            csvs.append("\n".join(lines))
        return csvs

    def _export_precision_recall_curves_csv(self):
        csvs = []
        for i in range(len(models)):
            lines = []
            
            for j in range(np.shape(self.precision_recall_curves[i])[0]):
                lines.append( str(j/10)  + CSV_SEPARATOR + str(self.precision_recall_curves[i][j].tolist()) )

            csvs.append("\n".join(lines))
        return csvs

    def _export_gcd_csv(self):
        csvs = []
        for i in range(len(models)):
            lines = []
            
            for j in range(np.shape(self.dcgs[i])[0]):
                lines.append( str(self.queries_number[j]) + CSV_SEPARATOR + str(self.dcgs[i][j].tolist()) )

            csvs.append("\n".join(lines))
        return csvs
        
    def _export_ngcd_csv(self):
        csvs = []
        for i in range(len(models)):
            lines = []
            
            for j in range(np.shape(self.ndcgs[i])[0]):
                lines.append( str(self.queries_number[j]) + CSV_SEPARATOR + str(self.ndcgs[i][j].tolist()) )

            csvs.append("\n".join(lines))
        return csvs
        
    def _export_f1_csv(self):
        csvs = []
        for i in range(len(models)):
            lines = []
            
            for j in range(np.shape(self.f1s[i])[0]):
                lines.append( str(self.queries_number[j]) + CSV_SEPARATOR + str(self.f1s[i][j].tolist()) )

            csvs.append("\n".join(lines))
        return csvs
        
    def _get_f1(self):
        f1s = []
        i = 0
        for i in range(len(self.precisions_at_k)):
            f1 = (2 * self.precisions_at_k[i] * self.recalls_at_k[i]) / (self.precisions_at_k[i] + self.recalls_at_k[i])
            f1s.append(f1)
        return f1s
            
    
    def _get_discounted_cumulative_gain(self):
        i = 0        
        discounted_cumulative_gains = []
        normalized_discounted_cumulative_gains = []
        for i in range(len(self.expecteds_relevances)):
            n_queries = len(self.expecteds_relevances[i])  
            n_documents = len(self.results_matrix[i][1])
            dcg = np.zeros((n_queries,n_documents))
            ndcg = np.zeros((n_queries,n_documents))
            j = 0
            for q in self.results_matrix[i].keys():
                relevances = np.zeros(n_documents)
                k = 0
                for d in self.results_matrix[i][q]:
                    if d in self.expecteds_relevances[i][q]:
                        relevances[k] = self.expecteds_relevances[i][q][d]
                    k += 1
                # Sort and reverse relevances
                sorted_relevances = np.sort(relevances)
                sorted_relevances = sorted_relevances[::-1]
                ideal_dcg = 0
                for p in range(n_documents):
                    from_two = np.arange(2, p + 3)
                    logs = np.log2(from_two)
                    powers = np.power(2, relevances[0:(p+1)]) - 1
                    dcg[j][p] = np.sum(powers/logs)
                    ideal_dcg += sorted_relevances[p]
                    ndcg[j][p] = dcg[j][p] / ideal_dcg
                
                j += 1
            
            discounted_cumulative_gains.append(dcg)
            normalized_discounted_cumulative_gains.append(ndcg)
        
        return discounted_cumulative_gains, normalized_discounted_cumulative_gains
        
    def _get_interpolated_precision_recall(self):
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
        
    def _get_precisions_at_k(self, k):
        pak = []
        for precisions in self.precisions_at_k:
            pak.append(precisions[:, (k-1)])
        return pak

    def _get_MAP(self):
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
        relevances = {}
        
        for line in expecteds_csv_file.readlines():
            splited = line.split(CSV_SEPARATOR)
            
            if len(splited) != 2:
                raise Exception("Error parsing %s on line %d! Mal formated csv." % (expecteds_file_name, i))
            
            query_number = int(splited[0])
            relevants[query_number] = []
            relevances[query_number] = {}
            self.queries_number.append(query_number)
             
            # Extract the list values
            list_string = re.sub('[^0-9 ]+', '', splited[1])   
            values_list = list_string.split(" ")
            for i in range(0, len(values_list) - 1, 2):
                relevants[query_number].append(int(values_list[i]))
                relevances[query_number][int(values_list[i])] = int(values_list[i+1])
                    
        self.expecteds_documents.append(relevants)
        self.expecteds_relevances.append(relevances)
        
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

    def _plot_f1(self, f1):
        N = len(models)
        n_docs = np.shape(f1[0])[1]
        ind = np.arange(1, n_docs + 1) # the x locations for the groups
        
        fig, ax = plt.subplots()
        for i in range(N):
            ax.plot(ind, np.mean(f1[i], axis=0) * 100, label=models[i], color=colors[i])
    
        # add some text for labels, title and axes ticks
        ax.set_ylabel("F1 (%)")
        ax.set_xlabel("k")
        ax.set_title("F1 (at k) Analysis")
        ax.legend(loc='upper right')
    
        fig.subplots_adjust(bottom=0.2)
        plt.xlim((1, n_docs + 1))
        plt.ylim((0, 100))
    
        plt.savefig("data/f1.pdf", format="pdf", dpi=300)

    def _plot_dcg(self, dcg):
        N = len(models)
        n_docs = np.shape(dcg[0])[1]
        ind = np.arange(1, n_docs + 1) # the x locations for the groups
        
        fig, ax = plt.subplots()
        for i in range(N):
            ax.plot(ind, np.mean(dcg[i], axis=0), label=models[i], color=colors[i])
    
        # add some text for labels, title and axes ticks
        ax.set_ylabel("DGC")
        ax.set_xlabel("p")
        ax.set_title("Discounted Cumulative Gain (at p) Analysis")
        ax.legend(loc='upper right')
    
        fig.subplots_adjust(bottom=0.2)
        plt.xlim((1, n_docs + 1))
    
        plt.savefig("data/dcg.pdf", format="pdf", dpi=300)

    def _plot_ndcg(self, ndcg):
        N = len(models)
        n_docs = np.shape(ndcg[0])[1]
        ind = np.arange(1, n_docs + 1) # the x locations for the groups
        
        fig, ax = plt.subplots()
        for i in range(N):
            ax.plot(ind, np.mean(ndcg[i], axis=0) * 100, label=models[i], color=colors[i])
    
        # add some text for labels, title and axes ticks
        ax.set_ylabel("NDGC (%)")
        ax.set_xlabel("p")
        ax.set_title("Normalized Discounted Cumulative Gain (at p) Analysis")
        ax.legend(loc='upper right')
    
        fig.subplots_adjust(bottom=0.2)
        plt.xlim((1, n_docs + 1))
        plt.ylim((0, 100))
    
        plt.savefig("data/ndcg.pdf", format="pdf", dpi=300)
 

    def _plot_precision_recall_curve(self, interpolated_precision_recall):
        N = len(models)
        ind = np.arange(0, 110, 10) # the x locations for the groups
        
        fig, ax = plt.subplots()
        for i in range(N):
            ax.plot(ind, interpolated_precision_recall[i] * 100, label=models[i], color=colors[i])
    
        # add some text for labels, title and axes ticks
        ax.set_ylabel("Precision (%)")
        ax.set_xlabel("Recall (%)")
        ax.set_title("11 point Interpolated Precision Recall Curve Analysis")
        ax.legend(loc='upper right')
    
        fig.subplots_adjust(bottom=0.2)
        plt.xlim((0, 100))
        plt.ylim((0, 100))
    
        plt.savefig("data/interpolated_precision_recall.pdf", format="pdf", dpi=300)
 
    def _plot_pat10(self, pat10):
        N = len(models)
        width = 0.35       # the width of the bars
        ind = np.arange(N) # the x locations for the groups

        mean_pat10 = []
        for i in range(N):
            mean_pat10.append(np.mean(pat10[i]) * 100)
        
        fig, ax = plt.subplots()
        rects = ax.bar(ind + width, mean_pat10, width, color=colors)
    
        # add some text for labels, title and axes ticks
        ax.set_ylabel("mean p@10 (%)")
        ax.set_title("Precision at 10 Analysis")
        ax.set_xticks(ind + (1.5*width)) 
        ax.set_xticklabels(models , rotation=45, ha='right')

        autolabel(rects, ax)
    
        fig.subplots_adjust(bottom=0.2)
        plt.xlim((0, N))
        plt.ylim((0, 100))
    
        plt.savefig("data/pat10.pdf", format="pdf", dpi=300)

    def _plot_MAP(self, MAP):
        N = len(models)
        width = 0.35	   # the width of the bars
        ind = np.arange(N) # the x locations for the groups
        
        fig, ax = plt.subplots()
        rects = ax.bar(ind + width, np.array(MAP) * 100, width, color=colors)
    
        # add some text for labels, title and axes ticks
        ax.set_ylabel("MAP (%)")
        ax.set_title("Mean Average Precision Analysis")
        ax.set_xticks(ind + (1.5*width)) 
        ax.set_xticklabels(models , rotation=45, ha='right')

        autolabel(rects, ax)
    
        fig.subplots_adjust(bottom=0.2)
        plt.xlim((0, N))
    
        plt.savefig("data/map.pdf", format="pdf", dpi=300)
        
        
def autolabel(rects, ax):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, "%.3f"%float(height),
                ha="center", va="bottom")

def __main__(argv):
    avaliador = Evaluator(AVAL_CONFIG_FILE)
    avaliador.run()
    avaliador.write_output()    

if __name__ == "__main__":
    __main__(sys.argv[1:])
