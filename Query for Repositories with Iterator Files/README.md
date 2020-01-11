This script returns all the repositories from GitHub which use the API Iterator and generates a CSV-file with information of repositories. Data format as follows:

**Data Format:** index | repository_name | file_url | commit_count | latest_commit_url

**Prerequisites:**

Python 3.6 or above needs to be installed. 
Install the github4 API for Python pip install --pre github3.py https://github.com/sigmavirus24/github3.py.
Ensure that you don't have repositories.txt or code.csv files in the directory where you want to execute the script from a previous run.


**Following are the steps to execute the Python script.**

1. Update get_matching_code_files_python3.py script with valid GitHub username and password. Be aware that you added your credentials to these files before you commit them!
2. $ cd DIR\With\Scripts where DIR\With\Scripts is the directory which contains this Python script.
3. To execute the second python, run the following command: python get_matching_code_files_python3.py --username <githubusername> --repoFile repositories.txt --outputFile code.csv 
4. This will generate the final results in a code.csv file which would have the list of repositories which are using the iterator API.
