def getQueryWithCursor(queryString, cursor, fragmentCount):
    return """{
                rateLimit {
                    cost
                    remaining
                    resetAt
                }
                search(query: "queryString", type: REPOSITORY, first: fragmentCount, after: "cursor") {
                    repositoryCount
                    pageInfo {
                        endCursor
                        startCursor
                        hasNextPage
                    }
                    edges {
                        node {
                            ... on Repository {
                                nameWithOwner
                                url
                                watchers(first: 1) {
                                    totalCount
                                }
                                stargazers(first: 1) {
                                    totalCount
                                }
                                defaultBranchRef {
                                    target {
                                        ... on Commit {
                                            history(first: 1){
                                                totalCount
                                                edges {
                                                    node {
                                                        commitUrl
                                                        committedDate
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }""".replace("queryString", queryString).replace("fragmentCount", str(fragmentCount)).replace("cursor", cursor)