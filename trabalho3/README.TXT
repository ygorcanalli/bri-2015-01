Trabalho da disciplina de Busca e Recuperação da Informação 2015-01
Aluno: Ygor de Mello Canalli
Curso: Mestrado em Engenharia de Sistemas e Computação - PESC/COPPE/UFRJ
Professor: Geraldo Xexéo

Instruções para uso:

Dependências:

Java
Eclipse
Lucene 4.10.4
Python3 + Numpy + Matplotlib (para comparação dos resultados)

Configuração de diretórios:

.
trabalho3/			--> raiz do projeto eclipse
	|-- src			--> código fonte
		|-- retrieval
			|-- InformationRetrievalSystem.java
			|-- PorterAnalyzer.java
	|-- RELATORIO.TXT
	|-- README.TXT
	|-- evaluator.py			--> Adaptado do trabalho anterior
	|-- AVAL.CFG
	|-- data/
		|-- consultas.csv			--> Oriundo do trabalho anterior
		|-- esperados-StemmingLucene-1.csv
		|-- esperados-StemmingNLTK-0.csv	--> Oriundo do trabalho anterior
		|-- indice_invertido.csv		--> Oriundo do trabalho anterior
		|-- interpolated_precision_recall.pdf
		|-- interpolated_precision_recall-StemmingLucene-1.csv
		|-- interpolated_precision_recall-StemmingNLTK-0.csv
		|-- map.pdf
		|-- pat10.pdf
		|-- pat10-StemmingLucene-1.csv
		|-- pat10-StemmingNLTK-0.csv
		|-- resultados-StemmingLucene-1.csv
		|-- resultados-StemmingNLTK-0.csv	--> Oriundo do trabalho anterior

Forma de executar:

Importar o projeto para o eclipse e rodar a classe InformationRetrievalSystem.java
Após a execução, rodar o script python para comparação dos resultados do Lucene com os do trabalho anterior:
	na raiz do projeto execute "python3 evaluator.py"

Obs.1: O cálculo de métricas foi adaptado do trabalho anterior, mantendo-se os formatos de saída do Lucene compatíveis com os do Python. Foram utilizadas as métricas MAP, precision@10 e 11 pontos de precisão e cobertura
Obs.2: A classe PorterAnalyzer foi feita com base no exemplo fornecido na documentação oficial do Lucene, disponível em https://lucene.apache.org/core/4_0_0/analyzers-common/org/apache/lucene/analysis/en/PorterStemFilter.html
Obs.3: A classe InformationRetrievalSystem foi feita com base no Tuturial "Lucene in 5 minutes", disponível em http://www.lucenetutorial.com/lucene-in-5-minutes.html
