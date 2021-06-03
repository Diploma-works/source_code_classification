# source_code_classification
Classification changes in the source code of Angular projects using machine learning methods.
## How to use 

1. Run make_train_data.py and make_test_data.py to make datasets and prepare meta information about files changes. Use repo_path to specify path to project. Results will be in data/.
0. Files in data/train/files_repo_path and data/test/files_repo_path are prepared and must be processed by id2vec. Script get_first_files.sh can help to copy first N files, if you want to process a part of files. 
   
   Original project id2vec is [here](https://github.com/tech-srl/id2vec).
0. Use add_vectors_to_dataset.ipynb for adding vectors after id2vec to dataset or just use one of three classifiers (k_neighbors.py, naive_bayes.py, tree.py).
