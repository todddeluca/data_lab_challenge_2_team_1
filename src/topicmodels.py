from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.cluster import KMeans
import numpy as np


def smac_topic(documents: list, counts=False, grid_search=False):
    """

    Args:
        documents (str): list of documents to fit topic model

    Returns:

    """

    TFIDF = TfidfVectorizer()
    tfidf_mat = TFIDF.fit_transform(documents)

    LDA = LatentDirichletAllocation(verbose=1, learning_decay=.9)

    if grid_search:
        LDA_grid_search(LDA, tfidf_mat)
    else:
        LDA.fit_transform(tfidf_mat)

    get_model_metrics(LDA, tfidf_mat)

    top_indices = assign_responses(LDA, tfidf_mat)

    print_model_features(LDA, TFIDF.get_feature_names(), 10, top_indices, documents)

    cluster_topic_modes(tfidf_mat, documents)


def cluster_topic_modes(doc_mat, documents=None):
    """
    Cluster documents based on LDA vectors for each document
    Args:
        doc_mat (np.array):

    Returns:

    """

    n_clusters = 15

    clusters = KMeans(n_clusters=n_clusters).fit_predict(doc_mat)

    if documents is not None:
        for i in range(n_clusters):
            print(f'Cluster {i}')
            inds = np.where(clusters == i)[0][:10]

            #print(inds)
            #exit()
            print(documents[inds])

    return clusters


def LDA_grid_search(lda, doc_mat):
    model = GridSearchCV(lda, param_grid={'n_components': [10, 15, 20, 25, 30], 'learning_decay': [.5, .7, .9]})

    model.fit(doc_mat)

    print('Best model and score:', model.best_estimator_, model.best_score_)


def get_model_metrics(model: LatentDirichletAllocation, doc_mat: np.array):
    """

    Args:
        model ():
        doc_mat ():

    Returns:

    """

    print(doc_mat.shape)

    print('Perplexity: ', model.perplexity(doc_mat))

    print('Log likelihood', model.score(doc_mat))

    print('Params', model.get_params())


def print_model_features(model,
                         feature_names,
                         n_top_words,
                         topic_indeces=None,
                         documents=None,
                         counts=0):
    """
    Print model features. See https://scikit-learn.org/stable/auto_examples/applications
    /plot_topics_extraction_with_nmf_lda.html#sphx-glr-auto-examples-applications-plot-topics-extraction-with-nmf-lda
    -py

    Args:
        topic_indeces ():
        model ():
        feature_names ():
        n_top_words ():

    Returns:


    """

    for topic_idx, topic in enumerate(model.components_):
        message = f"Topic #{topic_idx} "
        message += " ".join([feature_names[i]
                             for i in topic.argsort()[:-n_top_words - 1:-1]])

        if topic_indeces is not None and documents is not None:
            print('Topic Indices', topic_indeces)
            # print('documents', documents[:20])

            selected_docs = documents[np.where(topic_indeces == topic_idx)][:20]

            print(selected_docs)

        print(message)


def assign_responses(model: LatentDirichletAllocation, doc_mat):
    """
    Assign response to given topic models
    Args:
        model ():
        doc_mat ():

    Returns:
        top_topic (np.array): index of most likely topic
    """

    probs = model.transform(doc_mat)

    print('Probs', probs)

    top_topic = np.argmax(probs, axis=1)

    print('Argmax', top_topic)

    return top_topic
