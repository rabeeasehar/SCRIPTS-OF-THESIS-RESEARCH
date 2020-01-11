from repositories_query import getQuery
from repositories_query_cursored import getQueryWithCursor
from commit_count_filter import isValid
import requests
import datetime
import csv 



#Oath Token used on the GraphQL end point 
token = "Bearer 56c5c3dc7e7e1168a8e0878f909eeb1e16b14153"

# the page size to be fetched at a time 
pageSize = 10

# the GraphQL end point 
endpoint = "https://api.github.com/graphql"

#query string 
queryString = "is:public pushed:2019-01-01..2019-01-31 language:java stars:>400"

# commit count filter
commitCountRule = ">100"

# Run query and reutn the results 
def runQuery(): 
    # authentication header to be sent 
    authHeader = {'Authorization': token} 

    # init the remaining cost to the default github value 
    remainingCost = 5000

    # the 'next' cursor 
    nextCursor = "" 

    # whether the there is a next page 
    hasNextPage = True 

    # page count 
    pageCount = 1 

    # number of items written to file so far  
    numRecords = 0

    print("Page size per request: " + str(pageSize))

    while hasNextPage and remainingCost > 1000:

        # the query data to be sent 
        queryData = {'query': getQueryWithCursor(queryString, nextCursor, pageSize)}

        if nextCursor == "":
            queryData =  {'query': getQuery(queryString, pageSize)}
        
        # send the request and get the response
        response = requests.post(endpoint, headers=authHeader, json=queryData).json() 

        if nextCursor == "":
            totalRepositories = response["data"]["search"]["repositoryCount"]
            print("Total Repositories Found: " + str(totalRepositories) + " for further processing")

        print("Fetched page..................." + str(pageCount))

        remainingCost = response["data"]["rateLimit"]["remaining"]
        nextCursor = response["data"]["search"]["pageInfo"]["endCursor"]
        hasNextPage =  response["data"]["search"]["pageInfo"]["hasNextPage"]

        # now get the file name to which to save the data 
        file_name = "result.txt"

        # save data to file, return the number of records saved, update the current num records
        numRecords = saveResult(response, file_name, numRecords) + numRecords

        pageCount = pageCount + 1

    print("Saved data to file " + file_name)


# save the result to file 
def saveResult(json_data, file_name, numRecords): 
    if json_data["data"] is None: 
        print(json_data["errors"][0]["message"])
        return 0
    else: 
        data = json_data["data"]
        repositories = data["search"]["edges"]
    
        # rows to be written to file 
        rows = [] 

        for repository in repositories: 
            # first convert the repository into a row
            row = getRow(repository)

            # only add the row to the collection of rows if the commit count 
            # matches the specified value 
            if isValid(commitCountRule, row[2]):
                rows.append(row)

        index = numRecords + 1
        # once done, then write the rows to file 
        with open(file_name, 'a', newline='') as csv_file:
            repo_writer = csv.writer(csv_file, delimiter=";")
            for row in rows:
                row.insert(0, index)
                repo_writer.writerow(row)
                index = index + 1
        return len(rows)


def getFirstIndex(pageNumber): 
    return (pageNumber * pageSize) - (pageSize - 1)


# create a row from a repository 
def getRow(repository):
    name = repository["node"]["nameWithOwner"]
    url = repository["node"]["url"]
    commitCount = repository["node"]["defaultBranchRef"]["target"]["history"]["totalCount"]
    
    latestCommitDate = ""
    commitUrl = "" 

    if len(repository["node"]["defaultBranchRef"]["target"]["history"]["edges"]) > 0:
        latestCommitDate = repository["node"]["defaultBranchRef"]["target"]["history"]["edges"][0]["node"]["committedDate"]
        commitUrl = repository["node"]["defaultBranchRef"]["target"]["history"]["edges"][0]["node"]["commitUrl"]

    return [name, url, commitCount, latestCommitDate, commitUrl]