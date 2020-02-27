import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


def load_smac_data(filepath='../data/all_paper_data.xlsx', sheet_name='Trigger Other'):
    """
    Load SMC data from excel format
    """

    return pd.read_excel(filepath, sheet_name=sheet_name)


def generate_distributions(df, columns):
    """
    Generate Zipf distributions for a concatenated collection of columns

    Helpful when pulling data from all text columns in a dataframe
    """

    print(df[columns])

    all_columns = [' '.join(res.astype(str)) for res in df[columns].dropna().values]

    word_vec = CountVectorizer(all_columns)

    ret = word_vec.fit_transform(all_columns)

    ind2word = {v: k for k, v in word_vec.vocabulary_.items()}

    counts = pd.DataFrame(ret.sum(axis=0)).T
    counts.sort_values(by=0, ascending=False, inplace=True)
    counts['word'] = counts.index.map(ind2word)
    counts['rank'] = counts[0].rank(ascending=False)
    counts.set_index('word', inplace=True)

    counts['freq'] = counts[0] / counts[0].sum()

    return counts




