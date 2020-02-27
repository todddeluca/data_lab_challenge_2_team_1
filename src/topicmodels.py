from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import numpy as np


def smac_topic(documents: list, counts=False):
    """

    Args:
        documents (str): list of documents to fit topic model

    Returns:

    """
    print(documents)
    TFIDF = TfidfVectorizer()
    tfidf_mat = TFIDF.fit_transform(documents)

    LDA = LatentDirichletAllocation(verbose=1)

    LDA.fit_transform(tfidf_mat)

    print_model_features(LDA, TFIDF.get_feature_names(), 10)


def print_model_features(model, feature_names, n_top_words, counts=):
    """
    Print model features. See https://scikit-learn.org/stable/auto_examples/applications
    /plot_topics_extraction_with_nmf_lda.html#sphx-glr-auto-examples-applications-plot-topics-extraction-with-nmf-lda
    -py Args: model (): feature_names (): n_top_words ():

    Returns:

    """

    for topic_idx, topic in enumerate(model.components_):
        message = f"Topic #{topic_idx} "
        message += " ".join([feature_names[i]
                             for i in topic.argsort()[:-n_top_words - 1:-1]])
        print(message)


