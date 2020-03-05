import argparse
from pathlib import Path

from utils import load_smac_data, generate_distributions
from spellcheck import *
from topicmodels import smac_topic
import json


def make_args():
    description = 'Correct spelling errors'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i',
                        '--input',
                        help='input directory',
                        required=False,
                        default=Path('../data/all_paper_data.xlsx'),
                        type=Path)

    parser.add_argument('-o',
                        '--output',
                        help='output directory (will be passed to args.script with -o argument)',
                        required=False,
                        default=None,
                        type=Path)

    parser.add_argument('--spellcheck',
                        help='run sym spell on the input column',
                        action='store_true')

    parser.add_argument('--adjustfreq',
                        help='adjust frequency based on underlying data',
                        action='store_true')

    parser.add_argument('--topicmodel',
                        help='fit a topic model',
                        action='store_true')



    return parser.parse_args()


def main():
    args = make_args()

    sheet_name = 'Trigger Other'

    if args.adjustfreq or args.spellcheck:
        test_smac = load_smac_data(args.input, sheet_name)

    counts = None
    if args.adjustfreq:
        # make the new distribution
        cols = test_smac[10:]
        counts = generate_distributions(test_smac, cols.columns)
        if args.output:
            counts.to_csv(args.output / 'survey_word_counts.csv')

    target_col = 't_q9'

    clean_name = '../data/clean' / Path(
        f'clean_{sheet_name.replace(" ", "_")}_' + str(Path(args.input.stem).with_suffix('.csv')))
    if args.spellcheck:
        corrected_reps = run_spell_correct(test_smac[target_col], counts)

        json.dump(corrected_reps, open(f'../data/corrected_reps{target_col}.json', 'w'), indent=4)

        updated = merge_corrected(test_smac, target_col, corrected_reps)


        print('Saving to:', clean_name)
        updated.to_csv(clean_name)
    else:
        updated = pd.read_csv(clean_name)

    if args.topicmodel:
        print('Running topic model')
        counts = pd.read_csv('../data/clean/survey_word_counts.csv',index_col=0)['0'].to_dict()
        #   print(counts)
        smac_topic(updated[target_col].dropna().unique(), counts)



if __name__ == "__main__":
    main()
