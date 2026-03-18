# import statements
import pandas as pd
import glob
import ast
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM

#####################################################################################################################################################
# GLOBAL VARIABLES
# pertinent columns and rows
all_columns = ['width', 'height', 'webaudio', 'browser', 'mobile', 'fullscreen', 'task', 'trial_type', 'trial_index', 'time_elapsed', 'internal_node_id', 'lang_pair', 'words', 'foils', 'subject_id', 'prolific_id', 'study_id', 'session_id', 'condition', 'frequency_ranks', 'success', 'timeout', 'failed_images', 'failed_audio', 'failed_video', 'rt', 'url', 'stimulus', 'response', 'correct', 'image', 'word', 'foil', 'change_audio_order', 'button_1', 'button_2', 'response_audio', 'audioWord_first']
columns_to_keep = ['task', 'lang_pair', 'words', 'subject_id', 'condition', 'frequency_ranks', 'response', 'correct', 'button_1', 'button_2', 'response_audio', 'word', 'foil', 'time_elapsed', 'internal_node_id',]
columns_to_remove = ['width', 'height', 'webaudio', 'browser', 'mobile', 'fullscreen', 'trial_type', 'trial_index', 'foils', 'prolific_id', 'study_id', 'session_id', 'success', 'timeout', 'failed_images', 'failed_audio', 'failed_video', 'rt', 'url', 'stimulus', 'image', 'change_audio_order', 'audioWord_first']
tasks_to_keep = ['segmentation_trial']

# languages
L1s = [
    ["kulego", "nagitu", "tobuma", "midobe"],
    ["lakubi", "negado", "mudile", "kitena"],
    ["dogiba", "kalegu", "tebodi", "minato"],
    ["kinome", "teguda", "bulego", "moditu"],
    ["tobanu", "gukema", "delubo", "lamodi"],
    ["nodebu", "dimate", "mekugo", "gubila"]
]

L2s = [
    ["lemaku", "gibeto", "bugona", "dotumi"],
    ["binaku", "temula", "dokine", "galedi"],
    ["nadite", "lebado", "bogumi", "gitoka"],
    ["gumeki", "letumo", "nodabu", "digote"],
    ["matolu", "nubola", "mogude", "kediba"],
    ["bimegu", "tegoma", "kudino", "labude"]
]

#####################################################################################################################################################
# CLEAN DATA
def concatenate_csv(paths):
    """concatenates all raw CSV files to one file while removing extraneous columns and rows"""

    # concatenates each individual df to one df
    combined_df = pd.concat(
        (
            pd.read_csv(f)
            .drop(columns=columns_to_remove, errors="ignore")  # drops extraneous columns
            .loc[lambda df: df['task'].isin(tasks_to_keep)]  # drops extraneous rows
            for f in glob.glob(paths)
        ),
        ignore_index=True
    )

    return combined_df

import pandas as pd

def remove_subjects_all_same_response(df):
    """"""
    # Find subjects with only one unique response
    subjects_to_remove = df.groupby('subject_id')['response'].nunique()
    subjects_to_remove = subjects_to_remove[subjects_to_remove == 1].index.tolist()
    
    if subjects_to_remove:
        print("Removing subjects with the same response for every trial:")
        for subj in subjects_to_remove:
            print(subj)
    else:
        print("No subjects removed; all subjects have variable responses.")
    
    # Return df without those subjects
    cleaned_df = df[~df['subject_id'].isin(subjects_to_remove)].copy()
    
    return cleaned_df

def get_frequency_ranks(df):
    """add each target word to its own column based on frequency"""

    # gets ranks and adds to df
    df[['rank1','rank2','rank3','rank4']] = df['frequency_ranks'].apply(parse_ranks).apply(pd.Series)
    return df

def parse_ranks(val):
    """separates the target words by frequency"""

    # skips empty rows (uniform condition)
    if pd.isna(val) or val == "":
        return [None, None, None, None]
    try:
        ranks = ast.literal_eval(val)  # convert string to list
        ranks = ranks[:4] + [None]*(4-len(ranks))  # ensure length 4
        return ranks
    except Exception:
        return [None, None, None, None]
    
def get_current_rank(df):
    rank_cols = ['rank1','rank2','rank3','rank4']

    df['rank'] = 0  # default for uniform condition
    for i, col in enumerate(rank_cols, 1):
        df.loc[df['word'] == df[col], 'rank'] = i
    return df

def add_lang_num(df):
    """gets which language in the pair was used as the target"""

    df['lang_num'] = df['words'].apply(get_lang_num)
    return df

def get_lang_num(words):
    """checks if current language is 1 or 2 in pair"""
    
    words = ast.literal_eval(words)
    if words in L1s:
        return 1
    elif words in L2s:
        return 2
    else:
        raise ValueError(f"{words} not found in L1 or L2")
    
def get_item_ids(df):
    """creates a unique item_id for every word-foil pair in the segmentation trials"""

    df["item_id"] = df.groupby(["word", "foil"]).ngroup()
    return df

def filter_participants(df):
    """removes participants whose accuracy is below a certain threshold"""

    # calculate how many questions p needs to have gotten correct
    threshold = 0.6
    num_questions = df.groupby('subject_id').size().iloc[0]
    min_correct = int(threshold * num_questions)

    # compute total correct per subject
    correct_per_subject = df.groupby('subject_id')['correct'].sum()

    # get subjects who meet the threshold
    subjects_to_keep = correct_per_subject[correct_per_subject > min_correct].index
    subjects_to_remove = correct_per_subject[correct_per_subject <= min_correct].index

    # filter original df
    filtered_df = df[df['subject_id'].isin(subjects_to_keep)]
    removed_df = df[df['subject_id'].isin(subjects_to_remove)]

    return filtered_df, removed_df

#####################################################################################################################################################
# BASIC SPOT-CHECKS    
def check_conditions(df):
    """get counts for each condition type to check for roughly even distribution"""

    # pertinent columns with condition information
    columns = ['condition', 'lang_pair', 'words']

    # goes through each condition columna and gets count of how many times each condition has been used
    for column in columns:
        counts = df.groupby('subject_id')[column].first().value_counts()
        print(f'{column}\n{counts}')

def check_accuracy(df):
    """gets group accuracies for uniform and zipfian conditions"""

    # gets number of incorrect and correct responses based on conditon (uniform vs Zipfian distribution)
    counts = df.groupby('condition')['correct'].value_counts()
    print(f'{counts}')

    # gets accuracy for Zipfian condition minus frequent word
    counts = df.groupby('condition')['correct'].value_counts()
    print(f'{counts}')

def compute_mean_accuracies(df, seed=43):
    """"""

    # random seed
    np.random.seed(seed)

    # zipfian overall mean
    zipf = df[(df['condition'] == 'zipfian')]
    mean_zipf = zipf['correct'].mean()

    # uniform overall mean
    uniform = df[(df['condition'] == 'uniform')]
    mean_uniform = uniform['correct'].mean()    
    
    # Zipfian rank 1
    zipf_rank1 = df[(df['condition'] == 'zipfian') & (df['rank'] == 1)]
    mean_zipf1 = zipf_rank1['correct'].mean()
    # Zipfian rank 2
    zipf_rank2 = df[(df['condition'] == 'zipfian') & (df['rank'] == 2)]
    mean_zipf2 = zipf_rank2['correct'].mean()
    # Zipfian rank 3
    zipf_rank3 = df[(df['condition'] == 'zipfian') & (df['rank'] == 3)]
    mean_zipf3 = zipf_rank3['correct'].mean()
    # Zipfian rank 4
    zipf_rank4 = df[(df['condition'] == 'zipfian') & (df['rank'] == 4)]
    mean_zipf4 = zipf_rank4['correct'].mean()
    
    # Zipfian rank 2–4
    zipf_rank2to4 = df[(df['condition'] == 'zipfian') & (df['rank'].isin([2,3,4]))]
    mean_zipf2to4 = zipf_rank2to4['correct'].mean()
    
    # Uniform condition, sample 3 words per subject
    uniform_df = df[df['condition'] == 'uniform']
    
    sampled_rows = []

    for subj, sub_df in uniform_df.groupby('subject_id'):
        # Randomly select 3 words seen by this subject
        words_sample = np.random.choice(sub_df['word'].unique(), size=3, replace=False)
        sampled_rows.append(sub_df[sub_df['word'].isin(words_sample)])
    
    uniform_sample3_df = pd.concat(sampled_rows)
    mean_uniform_sample3 = uniform_sample3_df['correct'].mean()
    
    # print(f'zipfian_rank1: {mean_zipf1}\nzipfian_rank2to4: {mean_zipf2to4}\nzipfian_overall: {mean_zipf}\nuniform_sample3: {mean_uniform_sample3}\nuniform_overall: {mean_uniform}')
    print(f'zipfian_rank1: {mean_zipf1}\nzipfian_rank2: {mean_zipf2}\nzipfian_rank3: {mean_zipf3}\nzipfian_rank4: {mean_zipf4}\n')

#####################################################################################################################################################
# STATS AND VISUALIZATIONS
def plot_accuracy_by_lang(df):
    """"""
    
    # compute subject-level average accuracy per lang
    subject_lang_acc = (
        df.groupby(['subject_id', 'words', 'condition'])['correct']
          .mean()
          .reset_index()
    )
    
    # compute mean accuracy per lang × condition for bar heights
    lang_condition_acc = (
        subject_lang_acc.groupby(['words', 'condition'])['correct']
                         .mean()
                         .reset_index()
    )
    
    # create the plot
    plt.figure(figsize=(12, 6))
    
    # bar plot for means
    sns.barplot(
        data=lang_condition_acc,
        x='words',
        y='correct',
        hue='condition',
        errorbar=lambda x: (np.std(x), np.std(x)),
        palette='pastel'
    )
    
    # overlay individual subject dots
    sns.stripplot(
        data=subject_lang_acc,
        x='words',
        y='correct',
        hue='condition',
        dodge=True,
        palette='dark:gray',
        alpha=0.6,
        jitter=True
    )
    
    plt.ylabel('Accuracy')
    plt.xlabel('Language')
    plt.xticks(rotation=270)
    plt.title('Average Accuracy per Language by Condition')
    
    # Remove duplicate legend entries
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles[:2], labels[:2], title='Condition')
    
    plt.tight_layout()
    plt.savefig('/Users/patricksherlock/Desktop/zipfian_learning/accuracy_Lang_Cond.png')
    plt.show()

def build_glmm(df):
    """GLMM: correct ~ C(condition) + rank + (1|subject) + (1|item)"""

    # random effects: subject and item
    vc = {"subject": "0 + C(subject_id)",
          "item": "0 + C(item_id)"
    }

    # build model
    model = BinomialBayesMixedGLM.from_formula(
        "correct ~ C(condition) + rank",
        vc,
        df
    )

    result = model.fit_vb()

    return result

#####################################################################################################################################################
# MAIN
if __name__ == '__main__':
    df = concatenate_csv(paths="/Users/patricksherlock/Desktop/zipfian_learning/raw_data/*.csv")
    df = remove_subjects_all_same_response(df)
    df = get_frequency_ranks(df)
    df = get_current_rank(df)
    df = add_lang_num(df)
    df = get_item_ids(df)
    filtered_df, removed_df = filter_participants(df)
    check_conditions(df)
    check_conditions(filtered_df)
    check_conditions(removed_df)
    check_accuracy(filtered_df)
    compute_mean_accuracies(filtered_df)
    df.to_csv("/Users/patricksherlock/Desktop/zipfian_learning/data.csv", index=False)  # writes concatenated df to CSV
    plot_accuracy_by_lang(df)
    result = build_glmm(df)
    print(result.summary())
