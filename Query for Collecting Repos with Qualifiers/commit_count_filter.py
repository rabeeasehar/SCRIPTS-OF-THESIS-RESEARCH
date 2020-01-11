def isValid(commit_count_rule, commit_count_input): 
    # Ignore null values 
    if commit_count_input is None: 
        return False

    if commit_count_rule.startswith(">="):
        commit_count = commit_count_rule.replace(">=", "")
        return commit_count_input >= int(commit_count)

    elif commit_count_rule.startswith(">"): 
        commit_count = commit_count_rule.replace(">", "")
        return commit_count_input > int(commit_count)

    elif commit_count_rule.startswith("<="):
        commit_count = commit_count_rule.replace("<=", "")
        return commit_count_input <= int(commit_count)

    elif commit_count_rule.startswith("<"):
        commit_count = commit_count_rule.replace("<", "")
        return commit_count_input < int(commit_count)

    elif ".." in commit_count_rule:
        commit_counts = commit_count_rule.split("..")
        if len(commit_counts) != 2:
            return False 
        else:
            first_commit_count = commit_counts[0]
            second_commit_count = commit_counts[1]
            return commit_count_input >= int(first_commit_count) and commit_count_input <= int(second_commit_count) 