from symspellpy import SymSpell, Verbosity
import pkg_resources
import re
import numpy as np
import pandas as pd


def get_top_sym(term, symspell_obj, verbose=False):
    try:
        return symspell_obj.lookup(term, Verbosity.CLOSEST,
                                   max_edit_distance=3)[0].term
    except IndexError:
        if verbose:
            print(term)
        return term


def parse_text(response, regex):
    """
    Parse responses using our multiline regex
    """
    return regex.findall(str(response))


def compile_regex():
    """
    Compile our hardcoded regular expression
    """
    return re.compile(r'(\S[A-Z0-9\.]+\S)|(\b[\w\-]+\b)')


# def update_


def run_spell_correct(responses: pd.DataFrame, new_counts: pd.DataFrame = None):
    """
    Args:
        responses: responses to correct (np.array of str)
        new_counts: counts from the overall dataset to adjust frequency table
    """

    sym_spell = SymSpell(max_dictionary_edit_distance=3, prefix_length=7)
    dictionary_path = pkg_resources.resource_filename(
        "symspellpy", "frequency_dictionary_en_82_765.txt")
    # term_index is the column of the term and count_index is the
    # column of the term frequency
    sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)

    print('Ebola-->', sym_spell.words['ebola'])
    if new_counts is not None:  # run spell correct with counts passed by user
        make_adjusted_distribution(new_counts, sym_spell)
        print('Ebola-->', sym_spell.words['ebola'])

    regex = compile_regex()

    responses = responses.dropna().values
    corrected_responses = {}
    for line in responses:
        # print(line)
        # exit()
        if line in corrected_responses:
            continue
        line_regex = parse_text(line, regex)
        corrected = ' '.join(
            [get_top_sym(r[1].lower(), sym_spell, verbose=True) if r[0] == '' else r[0] for r in line_regex])
        corrected_responses.update({line: corrected})

    return corrected_responses


def merge_corrected(df, target_col, update_dict):
    """
    Args:
        df: df with string responses
        target_col: column to target remaping
    """
    df[target_col] = df[target_col].map(update_dict)
    return df


def make_adjusted_distribution(new_counts: pd.DataFrame, sym_spell):
    """
    Modify symspell frequency dict with new counts
    Args:
        new_counts: dataframe with counts
        sym_spell: symspell object
    """

    sym_spell_counts = pd.DataFrame([sym_spell.words]).T.sort_values(by=0, ascending=False)  # .values

    combined = sym_spell_counts.merge(new_counts, left_index=True, right_index=True)

    combined.columns = ['Sym_count', 'SMAC_count', 'SMAC_rank', 'SMAC_freq']

    sym_spell_sum = combined.Sym_count.sum()

    new_counts['freq'] = new_counts[0] / new_counts[0].sum()

    for key, val in new_counts[new_counts['freq'] > .0001]['freq'].to_dict().items():

        if key in sym_spell.words:
            sym_spell.delete_dictionary_entry(key)
            sym_spell.create_dictionary_entry(key, int(sym_spell_sum * val))
