The script derives Directed Acyclic Graphs and classify the commit difference between the recent commit and old commit. The script also compares commits with previous commits on a files and classifies them as:

-Addition Commit    
-Deletion Commit    
-No change commit   
-Sematic change     

**Prerequisites:**


-Python 3.7 needs to be installed     
-Install the requests package -- pip install requests   
-Install the requests package pip install pygraphviz  
    
**Following are the steps to execute the Python script:**   

1. Generate your access token from the GitHub -- https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line
2. $ cd DIR\With\Scripts where DIR\With\Scripts is the directory which contains this Python script.   
3. Make sure to create an output folder before running the script.  
4. To execute the Python script, run command --python get_DAG_commit.py
