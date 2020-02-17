from github import Github
import requests
import csv
import re
import os
import pygraphviz as pgv
import random


""" create a new output file, and return the writer object
    to be used for future writing work. Note: !! The writer object
    will then need to be closed. !!
"""
try:
    os.mkdir('output')
except FileExistsError:
    print("Directory output already exists")
directory = ['addition', 'deletion', 'no-change', 'semantic-change']
for d in directory:
    dirName = 'output/{}'.format(d)
    try:
        # Create target Directory
        os.mkdir(dirName)
        print("Directory " , dirName ,  " Created ") 
    except FileExistsError:
        print("Directory " , dirName ,  " already exists")

def create_file():
    writer = None
    csvfile = open("output_commit.csv", "w")
    fieldnames = [
        "index",
        "repository",
        "commit_id",
        "commit_url",
        "commit_url_date",
        "commit_count",
        "last_commit_of_repo",
        "file_url",
        "commit_type",
        "old_graph_file",
        "new_graph_file",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    return writer


"""
    Convert a row (a list with ordered elements) into a repository object.
"""


def row_to_repository(row):
    # create and configure a repo object
    try:
        repo = {}
        repo["index"] = row[0]
        repo["name"] = row[1]

        return repo
    except IndexError:
        return None


"""
    Load existing repositories, from the result.txt file
"""


def get_existing_repos():
    # a list of repositories
    repo_list = []

    # open input file
    with open("input.txt", "r") as input_file:
        for row in input_file:
            # split the row using delimiter to get the elements
            row = row.split(";")

            # convert the row into a repository object
            repository = row_to_repository(row)
            # add repository to the list
            if repository is not None:
                repo_list.append(repository)
        return repo_list


"""
   Get all the commits of a repository, given the repository name.
"""


def get_all_commits(repository_name):
    repo = g.get_repo(repository_name)
    commits = (
        repo.get_commits().reversed
    )  # reverses the list of all the commits so that the latest one is at the top
    return commits


"""
   Get the diffs of a given commit.
"""


def get_diffs(commit_url, commit_date, commit_id):
    # diffs collecton.
    diffs = []

    # the authorization token, using the Bearer scheme.
    headers = {"Authorization": f"Bearer {access_token}"}

    # the response after the query.
    response = requests.get(f"{commit_url}.diff", headers=headers)

    # the raw diffs that need to be parsed.
    raw_diffs = response.text.split("diff --git")

    # convert the diffs into some dictionary holding
    # critical metadata
    for raw_diff in raw_diffs:
        first_line = raw_diff.split("\n")[0]
        first_line_list = first_line.split(" ")
        file_name = first_line_list[-1][1:]
        try:
            diff = {}
            diff["target_file"] = file_name
            diff["content"] = raw_diff[raw_diff.index("\n@@") + 1 :]
            diff["commit_date"] = None
            diff["commit_url"] = commit_url
            diff["commit_id"] = commit_id
            diff["type"] = ""
            diff["old_graph_file"] = ""
            diff["new_graph_file"] = ""
            diffs.append(diff)
        except ValueError:
            pass
    return diffs


def find_var_names(content, keyword, class_object_map, key):
    regex = f"{keyword}<.*> (\w+) = .*\);"
    r = re.findall(regex, content)
    class_object_map[
        key
    ] = r  # this fixes the problem when there are objects defined with the same name in the file more than once


def identify_if_no_change(old_code_graph, new_code_graph):
    #
    old_code_methods = [r[0].split("-")[0].strip() for r in old_code_graph]
    new_code_methods = [r[0].split("-")[0].strip() for r in new_code_graph]
    if old_code_methods == new_code_methods:
        return "no-change"
    else:
        for l in old_code_methods:
            if l in new_code_methods:
                return "semantic-change"


def identify_diff_type(diff, keyword, old_code_graph=[], new_code_graph=[]):
    identify_no_change = None
    if old_code_graph or new_code_graph:
        identify_no_change = identify_if_no_change(old_code_graph, new_code_graph)

    content = diff["content"]
    has_additions = "\n+" in content
    has_deletions = "\n-" in content
    if keyword in content:
        if identify_no_change == "no-change":
            diff["type"] = "no-change"
        elif identify_no_change == "semantic-change":
            diff["type"] = "semantic-change"
        elif has_additions and has_deletions:
            diff["type"] = "modification"
        elif has_additions and not has_deletions:
            diff["type"] = "addition"
        elif not has_additions and has_deletions:
            diff["type"] = "deletion"
        
        if diff.get('old_graph_file'):
            try:
                if (diff['type'] != 'modification'):
                    file_name = diff['old_graph_file'].split("/")[1]
                    new_file_name = f"output/{diff['type']}/{file_name}"
                    os.rename(diff.get('old_graph_file'), new_file_name)
                    diff['old_graph_file'] = new_file_name
            except Exception as e:
                print(e)
        
        if diff.get('new_graph_file'):
            try:
                if (diff['type'] != 'modification'):
                    file_name = diff['new_graph_file'].split("/")[1]
                    new_file_name = f"output/{diff['type']}/{file_name}"
                    os.rename(diff.get('new_graph_file'), new_file_name)
                    diff['new_graph_file'] = new_file_name
            except Exception as e:
                print(e)






def create_and_save_graph(graph, label, filename):
    G = pgv.AGraph(directed=True)
    counter = 0
    if len(graph) > 1:
        for node in graph:
            if counter == 1:  # iter object
                G.add_edge(graph[0][0], graph[1][0])
            elif counter > 1 and counter < len(graph):
                # make an edge from the object iter to the methods from here onwards
                G.add_edge(graph[1][0], graph[counter][0])
            G.add_node(node[0], style=node[1], fillcolor=node[2])
            counter = counter + 1

        G.graph_attr["label"] = label
        G.draw(filename, prog="dot")


def extract_method_name(obj, line):
    regex = f"{obj}\.(\w+\((\w*[, ]*)*\))"
    try:
        method = re.search(regex, line)
        return method.group(1)
    except AttributeError:
        return None


def draw_differences(diff, keyword, object_names):
    has_additions = False
    has_deletions = False

    content = diff["content"]
    content_lines = content.split("\n")[1:]

    # set() does not allow duplicates
    old_code_graph = {"nodes": set(), "edges": set()}
    # new_code_graph = {'nodes': set(), 'edges': set()}
    old_code_graph["nodes"].add((keyword, "filled", "white"))
    # new_code_graph['nodes'].add((keyword, 'filled', 'white'))
    new_code_graph = []
    old_code_graph = []
    method_name_old = None
    method_name_new = None
    counter = 0
    methodCounter = 0
    # print('---Object Names---')
    # print(object_names)
    for line in content_lines:
        for obj in object_names:
            if obj in line:
                if not line.startswith("-"):
                    if keyword in line:
                        counter = random.randint(0, 9999)
                        filename = f"output/{diff['commit_id']}_{random.randint(0, 9999)}_new.png"
                        label = diff["target_file"].split("/")[-1]
                        create_and_save_graph(
                            new_code_graph,
                            f"{label} New",
                            filename,
                        )
                        # diff['new_graph_file'] = filename
                        new_code_graph = [
                            [keyword, "filled", "white"]
                        ]  # initialize the graph with the new keyword
                    if (obj in line) and not line.startswith(
                        "-"
                    ):  # this will give all + lines and lines which have not been changed
                        method_name_new = extract_method_name(obj, line)
                        if method_name_new is not None:
                            has_additions = True
                            objectNode = [obj, "filled", "white"]
                            if objectNode not in new_code_graph:
                                new_code_graph += [objectNode]
                            # Random Integer for reference
                            method_name_new = (
                                f"{method_name_new}-{random.randint(0, 9999)}"
                            )
                            if line.startswith("+"):
                                methodNode = [method_name_new, "filled", "green"]
                            else:
                                methodNode = [method_name_new, "filled", "white"]
                            new_code_graph += [methodNode]
                            break

    for line in content_lines:
        for obj in object_names:
            if obj in line:
                if not line.startswith("+"):
                    if keyword in line:
                        filename = f"output/{diff['commit_id']}_{random.randint(0, 9999)}_new.png"
                        print(filename)
                        label = diff["target_file"].split("/")[-1]
                        create_and_save_graph(
                            old_code_graph,
                            f"{label} New",
                            filename,
                        )
                        # diff["new_graph_file"] = filename
                        old_code_graph = [
                            [keyword, "filled", "white"]
                        ]  # initialize the graph with the new keyword
                    if (
                        obj in line
                    ):  # this will give all + lines and lines which have not been changed
                        method_name_old = extract_method_name(obj, line)
                        if method_name_old is not None:
                            has_deletions = True
                            objectNode = [obj, "filled", "white"]
                            if objectNode not in old_code_graph:
                                old_code_graph += [objectNode]

                            method_name_old = (
                                f"{method_name_old}-{random.randint(0, 9999)}"
                            )
                            if line.startswith("-"):
                                methodNode = [method_name_old, "filled", "red"]
                            else:
                                methodNode = [method_name_old, "filled", "white"]

                            old_code_graph += [methodNode]
                            break
    if has_additions and has_deletions:
        filename = f"output/{diff['commit_id']}"
        label = diff["target_file"].split("/")[-1]
        oldGraphCounter = random.randint(0, 9999)
        newGraphCounter = random.randint(0, 9999)
        create_and_save_graph(
            old_code_graph, f"{label} Old", f"{filename}_{oldGraphCounter}_old.png"
        )
        create_and_save_graph(
            new_code_graph, f"{label} New", f"{filename}_{newGraphCounter}_new.png"
        )
        diff["old_graph_file"] = f"{filename}_{oldGraphCounter}_old.png"
        diff["new_graph_file"] = f"{filename}_{newGraphCounter}_new.png"
        # print (diff['new_graph_file'])
        print(old_code_graph, new_code_graph)
    return old_code_graph, new_code_graph


def process_diff(diff, keyword, class_object_map):
    # add filename to class_object_map
    # if content has keyword in it
    old_code_graph, new_code_graph = [], []
    if diff["target_file"] not in class_object_map:
        if keyword in diff["content"]:
            class_object_map[diff["target_file"]] = set()

    # do further processing only if we have history
    # of keyword in the file
    if diff["target_file"] in class_object_map:
        find_var_names(diff["content"], keyword, class_object_map, diff["target_file"])
        if len(class_object_map[diff["target_file"]]) > 0:
            old_code_graph, new_code_graph = draw_differences(
                diff, keyword, class_object_map[diff["target_file"]]
            )

        identify_diff_type(diff, keyword, old_code_graph, new_code_graph)


"""
   Load  with the API change 'Iterator'.
"""


def load_commits_with_api_change(keyword):
    # get all repos
    repos = get_existing_repos()
    for repo in repos:
        # get all the commits of this repo
        all_commits = get_all_commits(repo["name"])

        class_object_map = {}
        for commit in all_commits:
            # get diffs for each commit.
            diffs = get_diffs(
                commit.html_url, commit.commit.author.date, commit.commit.sha
            )
            # for each diff in the colleciton of filtered diffs, write the content to file.
            for diff in diffs:
                process_diff(diff, keyword, class_object_map)
                if diff["type"]:
                    write_row(repo, diff)

# access token
access_token = "5799786109b592028a03dfefe3bb044ce22e5003"

# create github object using the access token
g = Github(access_token)
writer = create_file()
def write_row(repo, diff):
    if diff['type'] != 'modification':
        writer.writerow(
            {
                "index": l['index'],
                "commit_id": diff["commit_id"],
                "commit_url": diff["commit_url"],
                "commit_url_date": diff["commit_date"],
                "repository": l['repository'],
                "file_url": diff["target_file"],
                "commit_type": diff["type"],
                "old_graph_file": diff["old_graph_file"],
                "new_graph_file": diff["new_graph_file"],
            }
        )

with open('input.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    class_object_map = {}
    keyword = 'Iterator'
    for l in reader:
        if l.get('commit_url'):
            diffs = get_diffs(l['commit_url'], l['commit_url_date'], l['commit_id'])
            for diff in diffs:
                process_diff(diff, keyword, class_object_map)
                if diff["type"]:
                        write_row(l, diff)
    # Deleting unnecessary files that don't fall into category
    dir_name = "output/"
    test = os.listdir(dir_name)
    for item in test:
        if item.endswith(".png"):
            os.remove(os.path.join(dir_name, item))

"""
    Write a row containing the repo info, and commit info.
"""









# create file and return writer


# load_commits_with_api_change("Iterator")
# load_commits_with_api_change('OutputStream')
