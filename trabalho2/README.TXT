Trabalho da disciplina de Busca e Recuperação da Informação 2015-01
Aluno: Ygor de Mello Canalli
Curso: Mestrado em Engenharia de Sistemas e Computação - PESC/COPPE/UFRJ
Professor: Geraldo Xexéo

Instruções para uso:

Dependências:

Python3
SciKit-Learn (python3)
NLTK (python3)

Configuração de diretórios:

.
|-- data/
|	|-- cystic-fibrosis/
|		|-- cf74.xml
|		|-- cf75.xml
|		|-- cf76.xml
|		|-- cf77.xml
|		|-- cf78.xml
|		|-- cf79.xml
|		|-- cfquery.xml
|-- trabalho2/			--> raiz do código fonte
	|-- __init__.py
	|-- __main__.py
	|-- inverted_index_generator.py
	|-- indexer.py
	|-- query_processor.py
	|-- search_engine.py
	|-- GLI.CFG
	|-- INDEX.CFG
	|-- PC.CFG
	|-- BUSCA.CFG
	|-- application.log
	!-- evaluator.py
	|-- data/
		|-- consultas-NoStemming-1.csv
		|-- consultas-Stemming-0.csv
		|-- dcg-NoStemming-1.csv
		|-- dcg.pdf
		|-- dcg-Stemming-0.csv
		|-- esperados-NoStemming-1.csv
		|-- esperados-Stemming-0.csv
		|-- f1-NoStemming-1.csv
		|-- f1.pdf
		|-- f1-Stemming-0.csv
		|-- indice_invertido.csv
		|-- interpolated_precision_recall-NoStemming-1.csv
		|-- interpolated_precision_recall.pdf
		|-- interpolated_precision_recall-Stemming-0.csv
		|-- map.pdf
		|-- modelo_vetorial-NoStemming-1.pkl
		|-- modelo_vetorial-Stemming-0.pkl
		|-- ndcg-NoStemming-1.csv
		|-- ndcg.pdf
		|-- ndcg-Stemming-0.csv
		|-- pat10-NoStemming-1.csv
		|-- pat10.pdf
		|-- pat10-Stemming-0.csv
		|-- resultados-NoStemming-1.csv
		|-- resultados-Stemming-0.csv


Forma de executar:

python3 __main__.py
