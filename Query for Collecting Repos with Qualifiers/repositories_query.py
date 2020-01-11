def getQuery(queryString, fragmentCount):
    return """{
                rateLimit {
                    cost
                    remaining
                    resetAt
                }
                search(query: "queryString", type: REPOSITORY, first: fragmentCount) {
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
            }""".replace("queryString", queryString).replace("fragmentCount", str(fragmentCount))

