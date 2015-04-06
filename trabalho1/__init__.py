# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 15:54:24 2015

@author: ygorcanalli
"""
import unicodedata
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import word_tokenize
from pickle import dump, load
import xml.etree.ElementTree as ET
import re

GLI_CONFIG_FILE = 'GLI.CFG'
PC_CONFIG_FILE = 'PC.CFG'
INDEX_CONFIG_FILE = 'INDEX.CFG'
BUSCA_CONFIG_FILE = 'BUSCA.CFG'
READ_COMMAND = 'LEIA'
WRITE_COMMAND = 'ESCREVA'
MODEL_COMMAND = 'MODELO'
QUERIES_COMMAND = 'CONSULTAS'
RESULTS_COMMAND = 'RESULTADOS'
EXPECTEDS_COMMAND = 'ESPERADOS'
COMMAND_SEPARATOR = '='
CSV_SEPARATOR = ' ; '

