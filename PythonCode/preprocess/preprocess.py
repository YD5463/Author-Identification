import os
import pandas as pd
import swifter
import nltk
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from PythonCode.preprocess.FeatureExtraction import FeaturesExtraction
from PythonCode.Constants import *
from pathlib import Path

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')


def simple_style_helper(x) -> pd.DataFrame:
    x = pd.concat(
        [FeaturesExtraction.pos_count(x),
         FeaturesExtraction.stop_words(x),
         FeaturesExtraction.avg_word_len(x),
         FeaturesExtraction.avg_sentence_len(x),
         FeaturesExtraction.punctuation_marks(x)], axis=1)
    return x


def simple_style_handler(x_train, x_test, *args, **kwargs):
    return simple_style_helper(x_train), simple_style_helper(x_test)


def bag_of_words(x_train, x_test, *args, **kwargs):
    vectorizer = CountVectorizer(**kwargs)
    vectorizer.fit(x_train[TEXT_COLUMN_LABEL])
    x_train = pd.DataFrame(columns=vectorizer.get_feature_names(),
                           data=vectorizer.transform(x_train[TEXT_COLUMN_LABEL]).toarray())
    x_test = pd.DataFrame(columns=vectorizer.get_feature_names(),
                          data=vectorizer.transform(x_test[TEXT_COLUMN_LABEL]).toarray())
    return x_train, x_test


def filter_for_base_case():
    """
    filter two authors
    """
    pass


def preprocess_pipeline(data_path: str, repesention_handler, normalize: bool, scaler=StandardScaler(),
                        test_size: float = 0.3,
                        save_path="./Data/clean/", data_filter=None, cache=False, **kwargs) -> (
        pd.DataFrame, pd.DataFrame, pd.Series, pd.Series):
    if cache:
        # TODO: extract y_test_clean...
        return pd.read_csv(os.path.join(data_path, "x_train_clean.csv")), \
               pd.read_csv(os.path.join(data_path, "x_test_clean.csv")), \
               pd.read_csv(os.path.join(data_path, "y_train_clean.csv")), \
               pd.read_csv(os.path.join(data_path, "y_test_clean.csv"))
    df = load_data(data_path)
    if data_filter is not None:
        df = data_filter(df)
    X, Y = pd.DataFrame(df[TEXT_COLUMN_LABEL], columns=[TEXT_COLUMN_LABEL]), df[AUTHOR_NAME_COLUMN_NAME]

    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=test_size)
    x_train, x_test = repesention_handler(x_train, x_test, **kwargs)

    if normalize:
        scaler.fit(x_train)
        x_train, x_test = scaler.transform(x_train), scaler.transform(x_test)

    y_train = pd.factorize(y_train)[0]
    y_test = pd.factorize(y_test)[0]

    # turn to correct format
    x_train = pd.DataFrame(x_train)
    x_test = pd.DataFrame(x_test)
    y_train = pd.Series(y_train)
    y_test = pd.Series(y_test)
    if save_path is not None:
        Path(save_path).mkdir(parents=True, exist_ok=True)
        x_train.to_csv(os.path.join(save_path, "x_train_clean.csv"))
        x_test.to_csv(os.path.join(save_path, "x_test_clean.csv"))
        y_train.to_csv(os.path.join(save_path, "y_train_clean.csv"))
        y_test.to_csv(os.path.join(save_path, "y_test_clean.csv"))

    return x_train, x_test, y_train, y_test


def load_data(path: str) -> pd.DataFrame:
    rows_list = []
    _, authors, _ = next(os.walk(path))
    for author_name in authors:
        curr_row = {AUTHOR_NAME_COLUMN_NAME: author_name}
        author_path = os.path.join(path, author_name)
        _, _, books_files = next(os.walk(author_path))
        for book_name in books_files:
            curr_row[BOOK_NAME_COLUMN_NAME] = book_name
            with open(os.path.join(author_path, book_name), "r") as book:
                curr_row[TEXT_COLUMN_LABEL] = book.read()
            rows_list.append(curr_row.copy())
    return pd.DataFrame(rows_list)


# res = preprocess_pipeline("../../Data/C50/C50train", repesention_handler=bag_of_words, normalize=True,
#                     scaler=StandardScaler(), test_size=0.2,
#                     save_path="./cleaned/", cache=False, min_df=0.01)
#
# print(res)
