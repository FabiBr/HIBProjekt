import net.sf.javaml.classification.Classifier;
import net.sf.javaml.classification.bayes.NaiveBayesClassifier;
import net.sf.javaml.core.Dataset;
import net.sf.javaml.core.SparseInstance;
import net.sf.javaml.tools.data.FileHandler;
import weka.core.Instance;

import java.io.File;
import java.io.IOException;

public class MLController {

	public static void main(String[] args) {

		try {
			Dataset data = FileHandler.loadDataset(new File("/Users/marco.oliva/Desktop/20170109-timeline-sample-twitter-bot.csv"), 0, ",");
			System.out.println(data);
		} catch (IOException e) {
			e.printStackTrace();
		}


		// TODO Auto-generated method stub

	}

}
