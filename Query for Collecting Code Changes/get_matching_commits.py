from github import Github 
import requests
import csv

# access token
access_token = "56c5c3dc7e7e1168a8e0878f909eeb1e16b14153"

# key words that the commit should have to be considered of interest
key_words = ['Iterator']

# create github object using the access token
g = Github(access_token)

""" create a new output file, and return the writer object
    to be used for future writing work. Note: !! The writer object 
	will then need to be closed. !!
"""
def create_file():
	writer = None
	csvfile = open('output.csv', 'w')
	fieldnames = ['index','repository', 'commit_id', 'commit_url', 'commit_url_date','commit_count','last_commit_of_repo', 'file_url']
	writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
	writer.writeheader()
	return writer

# create file and return writer
writer = create_file()

"""
	Convert a row (a list with ordered elements) into a repository object.
"""
def row_to_repository(row):
	# create and configure a repo object
	repo = {}
	repo['index'] = row[0]
	repo['name'] = row[1]
	repo['repo_url'] = row[2]
	repo['commit_count'] = row[3]
	repo['latest_commit_date'] = row[4]
	repo['last_commit_of_repo'] = row[5]

	return repo

"""
    Load existing repositories, from the result.txt file 
"""
def get_existing_repos():
	# a list of repositories 
	repo_list = []

	# open input file 
	with open('input.txt', 'r') as input_file:
		for row in input_file:
			# split the row using delimiter to get the elements
			row = row.split(';')

			# convert the row into a repository object
			repository = row_to_repository(row)
			
			# add repository to the list
			repo_list.append(repository)
		return repo_list

"""
   Get all the commits of a repository, given the repository name.
"""
def get_all_commits(repository_name):
	repo = g.get_repo(repository_name)
	commits = repo.get_commits()
	return commits

"""
   Get the diffs of a given commit. 
"""
def get_diffs(commit_url, commit_date, commit_id):
	# diffs collection.
	diffs = []

	# the authorization token, using the Bearer scheme. 
	headers = {'Authorization': f"Bearer {access_token}"}

	# the response after the query. 
	response = requests.get(f"{commit_url}.diff", headers=headers)

	# the raw diffs that need to be parsed. 
	raw_diffs = response.text.split('diff --git')

	# convert the diffs into some dictionary holding 
	# critical metadata
	for raw_diff in raw_diffs:
		first_line = raw_diff.split('\n')[0]
		first_line_list = first_line.split(' ')
		file = first_line_list[len(first_line_list) - 1]
		diff = {}
		diff['target_file'] = file
		diff['content'] = raw_diff
		diff['commit_date'] = commit_date
		diff['commit_url'] = commit_url
		diff['commit_id'] = commit_id
		diffs.append(diff)

	# return diffs 
	return diffs

"""
   Checks if the diff content line contains any of the 
   keywords defined above.
"""
def contains_any_keyword(diff_content_line):
	for key in key_words:
		if(key in diff_content_line):
			return True

	return False


"""
    Is the provided diff valid? Valid:- Does any of the 
	content of the diff chunks contain the keywords specified.
"""
def is_diff_valid(diff):
	content = diff['content']
	content_lines = content.split('\n')
	new_content_lines = content_lines[1:]
	for new_content_line in new_content_lines:
		has_prefix = new_content_line.startswith('+')  or new_content_line.startswith('-')
		if has_prefix and  contains_any_keyword(new_content_line):
			return True
	return False
	
"""
   Load commits with the API change 'Iterator'.
"""
def load_commits_with_api_change():
	# get all repos
	repos = get_existing_repos()
	for repo in repos:
		# get all the commits of this repo
		all_commits = get_all_commits(repo['name'])

		for commit in all_commits:
			# get diffs for each commit.
			diffs = get_diffs(commit.html_url, commit.commit.author.date, commit.commit.sha)

			# Notify the user that the script is processing the diffs for the current commit
			print(f'Processing diffs for commit: {commit.commit.sha}')

			# filter the diffs, to get the ones we want.
			filtered_diffs = filter(is_diff_valid, diffs)

			# for each diff in the colleciton of filtered diffs, write the content to file.
			for diff in filtered_diffs:
				write_row(repo, diff)
				
"""
    Write a row containing the repo info, and commit info.
"""
def write_row(repo, diff):
	print(f"Writing commit => {diff['commit_id']}")
	writer.writerow({'index' : repo['index'],
	    'commit_id': diff['commit_id'], 
		'commit_url': diff['commit_url'], 
		'commit_url_date': diff['commit_date'],
		'repository' : repo['name'],
		'file_url' : diff['target_file'],
		'commit_count' : repo['commit_count'],
		'last_commit_of_repo' : repo['last_commit_of_repo']})

load_commits_with_api_change()
