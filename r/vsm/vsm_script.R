library(tm)
library(SnowballC)
library(slam)

# clean environment first
rm(list=ls())

# load query tweet
query <- "trump präsident usa"

# load docs
csu_doc <- readChar("csu_doc.txt", file.info("csu_doc.txt")$size)
cdu_doc <- readChar("cdu_doc.txt", file.info("cdu_doc.txt")$size)
linke_doc <- readChar("die_linke_doc.txt", file.info("die_linke_doc.txt")$size)
grune_doc <- readChar("gruene_doc.txt", file.info("gruene_doc.txt")$size)
spd_doc <- readChar("spd_doc.txt", file.info("spd_doc.txt")$size)
afd_doc <- readChar("afd_doc.txt", file.info("afd_doc.txt")$size)

doc.list <- list(csu_doc, cdu_doc, linke_doc, grune_doc, spd_doc, afd_doc)
N.docs <- length(doc.list)
names(doc.list) <- list("csu", "cdu", "linke", "gruene", "spd", "afd")

# create corpus
my.docs <- VectorSource(c(doc.list, query))
my.docs$Names <- c(names(doc.list), "query")
my.corpus <- Corpus(my.docs)

# format and stem corpus
my.corpus <- tm_map(my.corpus, removePunctuation)
my.corpus <- tm_map(my.corpus, removeNumbers)
my.corpus <- tm_map(my.corpus, content_transformer(tolower))
my.corpus <- tm_map(my.corpus, stripWhitespace)
my.corpus <- tm_map(my.corpus, removeWords, stopwords("german"))
my.corpus <- tm_map(my.corpus, stemDocument)

# Create Doc Term Matrix
term.doc.matrix.stm <- TermDocumentMatrix(my.corpus)
colnames(term.doc.matrix.stm) <- c(names(doc.list), "query")
term.doc.matrix <- as.matrix(term.doc.matrix.stm)

# Compute tf.idf weights from the term frequency vector
get.tf.idf.weights <- function(tf.vec) {
  n.docs <- length(tf.vec)
  non.zero.tf.vec <- tf.vec[tf.vec > 0] # filter the term frequency vector for docs that contain the term
  doc.frequency <- length(non.zero.tf.vec) # count docs that contain the term
  weights <- rep(0, n.docs) # create a zero matrix with the size of the length of the tf vector
  weights[tf.vec > 0] <- (1 + log2(non.zero.tf.vec)) * log2(n.docs/doc.frequency) # calculate tf.idf weights of the term for each doc that contains it
  return(weights)
}

# Create tf.idf weights matrix of the doc term matrix
tfidf.matrix <- t(apply(term.doc.matrix, 1, FUN = function(row) { get.tf.idf.weights(row) }))
colnames(tfidf.matrix) <- colnames(term.doc.matrix)

# normalize lengths
tfidf.matrix <- scale(tfidf.matrix, center = FALSE, scale = sqrt(colSums(tfidf.matrix^2)))

# seperate query from docs
query.vector <- tfidf.matrix[, (N.docs + 1)]
tfidf.matrix <- tfidf.matrix[, 1:N.docs]

doc.scores <- t(query.vector) %*% tfidf.matrix

# create results data frame
results.df <- data.frame(doc = names(doc.list), score = t(doc.scores))
results.df <- results.df[order(results.df$score, decreasing = TRUE), ]

results.df