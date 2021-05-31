from git import Repo
import csv
import difflib


# change types: 0) A - added, 1) D - deleted, 2) M - modified, 3) R - renamed

# commit types:
# 1) build: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
# 2) ci: Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
# 3) docs: Documentation only changes
# 4) feat: A new feature
# 5) fix: A bug fix
# 6) perf: A code change that improves performance
# 7) refactor: A code change that neither fixes a bug nor adds a feature
# 8) style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
# 9) test: Adding missing tests or correcting existing tests

repo_path = 'components'
repo = Repo(repo_path)
write_to = 'data/test/' + repo_path + '_ts.csv'


def get_commit_type(commit):
    message = commit.message.lower().lstrip()
    index = message.find('build')
    if index != -1:
        return 1
    index = message.find('ci')
    if index != -1:
        return 2
    index = message.find('doc')
    if index != -1:
        return 3
    index = message.find('feat')
    if index != -1:
        return 4
    index = message.find('fix')
    if index != -1:
        return 5
    index = message.find('perf')
    if index != -1:
        return 6
    index = message.find('refactor')
    if index != -1:
        return 7
    index = message.find('style')
    if index != -1:
        return 8
    index = message.find('test')
    if index != -1:
        return 9
    return False


def check_file_type(diff_item):
    ignore_types = ['.jpg', '.jpeg', '.ico', '.png', '.svg', '.gif', '.swp', 'dir', 'token', '.ttf', '.DS_Store']

    # 5%
    # valid_types = ['.ts', '.js', '.json', '.bazel', '.md', '.html', '.dart']
    # 1%
    # valid_types = ['.ts', '.js', '.json', '.bazel', '.lock', '.html', '.sh', '.bzl', '.md', 'workspace',
    #                '.yml', '.dart', '.scss', '.css', '.es6', '.lock']

    valid_types = ['.ts']

    type = get_file_type(diff_item)

    for i in range(0, len(valid_types)):
        if type == valid_types[i]:
            return i + 1
    return False

    # for i in range(0, len(ignore_types)):
    #     if type == ignore_types[i]:
    #         return False
    # return type


def get_file_type(diff_item):
    filename = diff_item.b_path
    index = filename.rfind('.')
    if index != -1:
        if filename.find('token') != -1:
            return 'token'
        if filename.find('.ttf') != -1:
            return '.ttf'
        if filename.find('.ttf') != -1:
            return '.DS_Store'
        else:
            return str(filename)[index:]
    else:
        if filename.find('WORKSPACE') != -1:
            return 'workspace'
        if filename.find('token') != -1:
            return 'token'
        return 'dir'


def get_diff_type(diff_item):
    diff_type = diff_item.change_type
    if diff_type == 'A':
        return 0
    if diff_type == 'D':
        return 1
    if diff_type == 'M':
        return 2
    if diff_type == 'R':
        return 3


def get_file_info(diff_item):
    name = diff_item.b_path
    if check_file_type(diff_item):
        file_before = ' '
        file_after = ' '
        a = ' '
        b = ' '

        if diff_item.a_blob:
            file_before = diff_item.a_blob.data_stream.read().decode('utf-8')
            a = file_before.splitlines()

        if diff_item.b_blob:
            file_after = diff_item.b_blob.data_stream.read().decode('utf-8')
            b = file_after.splitlines()

        d = difflib.Differ()
        changes = d.compare(a, b)
        changes = [l for l in changes if l.startswith('- ') or l.startswith('+ ')]
        changes_all = ' '
        for change in changes:
            changes_all = changes_all + change

        diff_type = get_diff_type(diff_item)

        file = {'name': name,
                'file_type': check_file_type(diff_item),
                'diff_type': diff_type,
                'diff': changes_all,
                'file_before': file_before,
                'file_after': file_after,
                'commit_id': commit.hexsha}
        return file

    return False


def write_file(file):
    name = file.get('name')
    before = file.get('file_before')
    after = file.get('file_after')

    index = name.find('/')
    if index != -1:
        name = name.replace('/', ':')

    dir = 'data/test/files_' + repo_path '/'

    file_name_before = dir + name + '_' + file.get('commit_id') + '_' + 'before.ts'
    file_name_after = dir + name + '_' + file.get('commit_id') + '_' + 'after.ts'

    with open(file_name_before,'w') as file_before:
        file_before.write(before)

    with open(file_name_after,'w') as file_after:
        file_after.write(after)


def get_remote_branches(repo):
    local_repo = repo

    for remote in local_repo.remotes:
        remote.fetch()

    remote_repo = local_repo.remote()
    remote_branches = []

    for this_branch in remote_repo.refs:
        remote_branches.append(this_branch.remote_head)

    return remote_branches



with open(write_to, 'w', encoding="utf-8") as data:
    features = ['file_name', 'file_type', 'file_diff_type', 'is_added', 'is_deleted', 'is_modified', 'is_renamed',
                'file_diff', 'file_before', 'file_after', 'commit_id', 'commit_type']

    writer = csv.DictWriter(data, fieldnames=features)
    writer.writeheader()

    commit_set = set()

    branch_number = 0
    commit_number = 0
    file_number = 1
    for branch in get_remote_branches(repo):
        branch_number = branch_number + 1
        commits = list(repo.iter_commits('origin/' + branch))

        for commit in commits:
            commit_type = get_commit_type(commit)
            if not commit_type:
                continue
            if str(commit.hexsha) in commit_set:
                continue
            commit_number = commit_number + 1
            diff = commit.diff(commit.parents[0])

            for diff_item in diff:
                print(diff_item.b_path)
                file = get_file_info(diff_item)
                if file:
                    file_diff_type = file.get('diff_type')
                    writer.writerow({'file_name': file.get('name'),
                                     'file_type': file.get('file_type'),
                                     'file_diff_type': file_diff_type,
                                     'is_added': 1 if file_diff_type == 0 else 0,
                                     'is_deleted': 1 if file_diff_type == 1 else 0,
                                     'is_modified': 1 if file_diff_type == 2 else 0,
                                     'is_renamed': 1 if file_diff_type == 3 else 0,
                                     'file_diff': file.get('diff'),
                                     'file_before': file.get('file_before'),
                                     'file_after': file.get('file_after'),
                                     'commit_id': file.get('commit_id'),
                                     'commit_type': commit_type})
                    print('branch:', branch_number, 'commit:', commit_number, 'file:', file_number,
                          get_file_type(diff_item), commit_type)
                    file_number = file_number + 1

                    write_file(file)

            commit_set.add(str(commit.hexsha))
