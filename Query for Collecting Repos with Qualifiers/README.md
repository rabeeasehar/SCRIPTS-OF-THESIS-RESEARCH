This script returns all the repositories from GitHub that matches the criteria of all qualifiers given by the user. Following are the criteria:

1. Language

2. Number of stars

3. Number of commits

4. Latest updated date of the repository



Prerequisites:

Python 3.6 or above needs to be installed

Install the requests package -- pip install requests



Following are the steps to execute the Python script.


1. Generate your access token from the GitHub -- https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line

2. $ cd DIR\With\Scripts where DIR\With\Scripts is the directory which contains this Python script.

3. To execute the Python script, run the following command: python main.py At the end of execution this will write the information of resulting repositories to a result.txt file.

