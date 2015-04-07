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
|-- trabalho1/			--> raiz do código fonte
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
	|-- data/
		|-- indice_invertido.csv
		|-- modelo_vetorial.pkl
		|-- consultas.csv
		|-- esperados.csv
		|-- resultados.csv

Forma de executar:

python3 __main__.py
