package retrieval;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopScoreDocCollector;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.RAMDirectory;
import org.apache.lucene.util.Version;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.Charset;
import java.text.Normalizer;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

public class InformationRetrievalSystem {
	
	private static final String invertedIndexPath = "data/indice_invertido.csv";
	private static final String queriesPath = "data/consultas.csv";
	private static final String resultsPath = "data/resultados-StemmingLucene-1.csv";
	private static final String csvSeparator = " ; ";
	private static final Map<String, String> documentsContent = new HashMap<String, String>();
	private static final Map<String, Query> queries = new HashMap<String, Query>();

	public static void main(String[] args) throws IOException, ParseException {
		importInvertedIndex();
		// 0. Specify the analyzer for tokenizing text.
		// The same analyzer should be used for indexing and searching
		Analyzer analyzer = new PorterAnalyzer();

		// 1. create the index
		Directory index = new RAMDirectory();

		IndexWriterConfig config = new IndexWriterConfig(Version.LUCENE_4_10_4,
				analyzer);

		IndexWriter w = new IndexWriter(index, config);
		
		for (Entry<String, String> entry: documentsContent.entrySet()) {
			addDoc(w, entry.getKey(), entry.getValue());	
		}
					
		w.close();

		// 2. query
		importQueries(analyzer);
		

		// 3. search
		int hitsPerPage = documentsContent.size();
		IndexReader reader = DirectoryReader.open(index);
		IndexSearcher searcher = new IndexSearcher(reader);
		
		StringBuffer resultsCSV = new StringBuffer();
		for (Entry<String, Query> entry: queries.entrySet()) {
			Query q = entry.getValue();
			String queryId = entry.getKey();
			
			TopScoreDocCollector collector = TopScoreDocCollector.create(hitsPerPage, true);
			searcher.search(q, collector);
			ScoreDoc[] hits = collector.topDocs().scoreDocs;
			
			// 4. display results
			resultsCSV.append(queryId + csvSeparator + "[");
			for (int i = 0; i < hits.length - 1; ++i) {
				int docId = hits[i].doc;
				float score = hits[i].score;
				Document d = searcher.doc(docId);
				
				resultsCSV.append("(" + i + ", " + d.get("id") + ", " + score + "), ");
			}
			int docId = hits[hits.length - 1].doc;
			float score = hits[hits.length - 1].score;
			Document d = searcher.doc(docId);
			resultsCSV.append("(" + (hits.length - 1) + ", " + d.get("id") + ", " + score + ")]\n");

		}
		
		// reader can only be closed when there
		// is no need to access the documents any more.
		reader.close();
		
		FileWriter fw = new FileWriter(new File(resultsPath));
		BufferedWriter bw = new BufferedWriter(fw);
		bw.write(resultsCSV.toString());
		bw.close();
	}

	private static void addDoc(IndexWriter w, String id, String content)
			throws IOException {
		Document doc = new Document();
		doc.add(new TextField("content", content, Field.Store.YES));

		// use a string field for id because it'll not be tokenized
		doc.add(new StringField("id", id, Field.Store.YES));
		w.addDocument(doc);
	}
	
	private static void importInvertedIndex() {
		String line;
		try (
		    InputStream fis = new FileInputStream(invertedIndexPath);
		    InputStreamReader isr = new InputStreamReader(fis, Charset.forName("UTF-8"));
		    BufferedReader br = new BufferedReader(isr);
		) {
		    while ((line = br.readLine()) != null) {
		        String[] splited = line.split(csvSeparator);
		        String token = splited[0];
		        String[] documentIds = parsePythonFormatedList(splited[1]);
		        String atualContent = null;
		        
		        // Rebuild documents contents
		        for (int i = 0; i < documentIds.length; i++) {
					if (documentsContent.containsKey(documentIds[i])) {
						atualContent = documentsContent.get(documentIds[i]);
						documentsContent.put(documentIds[i], atualContent + " " + token);
					} else {
						documentsContent.put(documentIds[i], token);
					}
				}
		    }
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		String normalizedContent = null;
		// Normalize the contents
		for (Entry<String, String> entry: documentsContent.entrySet()) {
			normalizedContent = normalizeString(entry.getValue());
			documentsContent.put(entry.getKey(), normalizedContent);
			
		}
	}
	
	private static void importQueries(Analyzer analyzer) {
		String line;
		try (
		    InputStream fis = new FileInputStream(queriesPath);
		    InputStreamReader isr = new InputStreamReader(fis, Charset.forName("UTF-8"));
		    BufferedReader br = new BufferedReader(isr);
		) {
		    while ((line = br.readLine()) != null) {
		        String[] splited = line.split(csvSeparator);
		        String queryId = splited[0];
		        String queryContent = normalizeString(splited[1]);
		        Query query = null;
		        // Store queries
				try {
					query = new QueryParser("content", analyzer).parse(QueryParser.escape(queryContent));
					queries.put(queryId, query);
				} catch (ParseException e) {
					e.printStackTrace();
				}
		    }
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}
	
	private static String[] parsePythonFormatedList(String pythonFormatedList) {
		String withNoBreackets = pythonFormatedList.substring(1, pythonFormatedList.length() - 1);
		String[] elements = withNoBreackets.split(", ");
		return elements;
	}
	
	public static String normalizeString(String s) {
		/*
		 * Upper case
		 * parse accents
		 * remove numbers
		 * remove special characters
		 * remove 1 char words
		 */
		return Normalizer
				.normalize(s.toLowerCase(), Normalizer.Form.NFKD)
				.replaceAll("(\\r|\\n)", "")
				.replaceAll("[^a-z\\s]+", "")
				.replaceAll("\\b\\w{1}\\b\\s?", " ");
	}

}
