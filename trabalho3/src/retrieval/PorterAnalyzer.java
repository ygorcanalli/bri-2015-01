package retrieval;

import java.io.Reader;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.Tokenizer;
import org.apache.lucene.analysis.core.LowerCaseTokenizer;
import org.apache.lucene.analysis.en.PorterStemFilter;

public class PorterAnalyzer extends Analyzer {

	@Override
	protected TokenStreamComponents createComponents(String fieldName, Reader reader) {
		// TODO Auto-generated method stub
        @SuppressWarnings("deprecation")
		Tokenizer source = new LowerCaseTokenizer(getVersion(), reader);
        return new TokenStreamComponents(source, new PorterStemFilter(source));
	}

}
