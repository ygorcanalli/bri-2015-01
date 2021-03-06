# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 15:54:24 2015

@author: ygorcanalli
"""
from __future__ import unicode_literals
import unicodedata
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import *
from nltk import word_tokenize
import matplotlib as mpl
import matplotlib.pyplot as plt
from pylab import setp
from pickle import dump, load
import xml.etree.ElementTree as ET
import re
import logging

models = ['Stemming', 'NoStemming']
colors = ["darkgrey", 'darkgreen']
logging.basicConfig(format='[%(levelname)s %(asctime)s %(name)s]\t%(message)s',filename='application.log',level=logging.INFO)

AVAL_CONFIG_FILE = 'AVAL.CFG'
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

