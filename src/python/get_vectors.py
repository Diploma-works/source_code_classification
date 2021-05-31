import csv
import pandas as pd

def parse_file_name(name):
    # file name pattern: name_commitId_before/after.ts

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


def get_file_vectors():
    with open('val_5000/val_raw.txt', 'r') as tokens, open('val_5000/ts_dataset.val.c2v.vectors', 'r') as vectors:
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
        vector_list = vectors_list[i]
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


file_vectors = get_file_vectors()

for vector in file_vectors:
    print(vector)

dataset = pd.DataFrame(file_vectors)
dataset.to_csv('../../data/angular/train/vectors.csv')


