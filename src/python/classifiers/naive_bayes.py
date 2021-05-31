
import pandas as pd
from sklearn import metrics
from sklearn.compose import make_column_transformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB, ComplementNB

data = pd.read_csv('../../../data/train/angular_ts.csv')
data.head(5)

data_test = pd.read_csv('../../../data/test/components_ts.csv')
data_test.head(5)

def parse_file_name(name):
    # file name pattern: name_commitId_before/after.tsww.win2.cn/g10


    index = name.rfind('_')
    file_type = name[index+1:-3]

    name = name[:index]
    index = name.rfind('_')
    commit_id = name[index+1:]

    name = name[17:index]

    index = name.find(':')
    if index != -1:
        name = name.replace(':', '/')

    return name, commit_id, file_type


def vec_to_float(list):
    list_float = [float(l) for l in list]
    return list_float


def get_file_vectors(tokens_file, vectors_file):
    with open(tokens_file, 'r') as tokens, \
            open(vectors_file, 'r') as vectors:
        tokens = tokens.read().splitlines()
        vectors_list = vectors.read().splitlines()

        names = []
        for i in range(0, len(tokens)):
            if i % 2 == 0:
                if tokens[i].startswith('raw_data/val_dir'):
                    names.append(tokens[i])


    filenames = []
    commits = []
    types = []

    for name in names:
        filename, commit_id, file_type = parse_file_name(name)
        filenames.append(filename)
        commits.append(commit_id)
        types.append(file_type)

    file_vectors = []

    for i in range(0, len(names)):
        vector_list = vectors_list[i].split()
        vector_list = vec_to_float(vector_list)

        same_file = [file for file in file_vectors
                   if (file.get('name') == filenames[i] and file.get('commit_id') == commits[i])]

        if same_file:
            if types[i] == 'before':
                same_file[0]['vector_before'] = vector_list
            elif types[i] == 'after':
                same_file[0]['vector_after'] = vector_list
        else:
            if types[i] == 'before':
                file_vec = {'name': filenames[i], 'commit_id': commits[i], 'vector_before': vector_list}
            elif types[i] == 'after':
                file_vec = {'name': filenames[i], 'commit_id': commits[i], 'vector_after': vector_list}
            file_vectors.append(file_vec)

    return file_vectors


file_vectors = get_file_vectors('../../../data/train/vectors_data/val_raw.txt', '../../../data/train/vectors_data/ts_dataset.val.c2v.vectors')
file_test_vectors = get_file_vectors('../../../data/test/vectors_data/components_vectors/val_raw.txt',
                                     '../../../data/test/vectors_data/components_vectors/ts_dataset.val.c2v.vectors')

data_vectors = pd.DataFrame(file_vectors)
data_test_vectors = pd.DataFrame(file_test_vectors)

data_vectors = data_vectors.fillna(0)
data_test_vectors = data_test_vectors.fillna(0)

data_vectors = data_vectors.rename(columns={'name': 'file_name'})
data_test_vectors = dadata_test_vectors.rename(columns={'name': 'file_name'})

merged = pd.merge(left=data, right=data_vectors, on=['file_name', 'commit_id'], how='inner')
merged_test = pd.merge(left=data_test, right=data_test_vectors, on=['file_name', 'commit_id'], how='inner')

table = merged[['is_added', 'is_deleted', 'is_modified', 'is_renamed', 'file_before', 'file_after', 'commit_type']]
table_test = merged_test[['is_added', 'is_deleted', 'is_modified', 'is_renamed', 'file_before', 'file_after', 'commit_type']]

data_test = table_test[['file_type', 'file_diff_type', 'file_diff']]
y_data_test = table_test[['commit_type']]

X_train, X_test, y_train, y_test = train_test_split(
    table[['file_type', 'file_diff_type', 'file_diff']],
    table[['commit_type']], test_size=0.2)

nb = MultinomialNB()
nb.fit(X_train, y_train)

test_score = nb.score(X_test, y_test)
train_score = nb.score(X_train, y_train)

predicted = nb.predict(data_test)
pred_score = nb.score(data_test, y_data_test)

nb = ComplementNB()
nb.fit(X_train, y_train)

test_score = nb.score(X_test, y_test)
train_score = nb.score(X_train, y_train)

predicted = nb.predict(data_test)
pred_score = nb.score(data_test, y_data_test)
