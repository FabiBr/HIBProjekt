import java.util.Properties;

public class MyAnalyser {

	public static void main(String[] args) {
	}
	
	private int analyseLine(String line) {
		Properties props = new Properties();
        props.setProperty("annotators", "tokenize, ssplit, parse, sentiment");
        edu.stanford.nlp.pipeline.StanfordCoreNLP pipeline = new edu.stanford.nlp.pipeline.StanfordCoreNLP(props);
        int mainSentiment = 0;
        if (line != null && line.length() > 0) {
            int longest = 0;
            edu.stanford.nlp.pipeline.Annotation annotation = pipeline.process(line);
            for (edu.stanford.nlp.util.CoreMap sentence : annotation.get(edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation.class)) {
                edu.stanford.nlp.trees.Tree tree = sentence.get(edu.stanford.nlp.sentiment.SentimentCoreAnnotations.SentimentAnnotatedTree.class);
                int sentiment = edu.stanford.nlp.neural.rnn.RNNCoreAnnotations.getPredictedClass(tree);
                String partText = sentence.toString();
                if (partText.length() > longest) {
                    mainSentiment = sentiment;
                    longest = partText.length();
                }
 
            }
        }
        if (mainSentiment == 2 || mainSentiment > 4 || mainSentiment < 0) {
            return Integer.MIN_VALUE;
        }
        return mainSentiment;
	}

}
