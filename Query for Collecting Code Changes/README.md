This script returns CSV file with URL of all commits having code changes in Iterator API or its methods. The data format of columns given as follows:

**Data Format:** index | repo_name| commit_id |commit_url |commit_url_date |commit_count |last_commit_of_repo | file_url


**Prerequisites:**

JetBrains PyCharm needs to be installed

Python 3.6 or above needs to be installed

Install the requests package -- pip install requests

Ensure that you don't have output.csv file in the directory where you want to execute the script from a previous run.



**Following are the steps to execute the Python script:**


1. Generate your access token from the GitHub -- https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line
2. $ cd DIR\With\Scripts where DIR\With\Scripts is the directory which contains this Python script.
3. To execute the Python script, open JetBrains Pycharm, provide the name of Input.txt file at line 52, and hit Play button. At the end of execution this will write the information of resulting commits to a output.csv file.

