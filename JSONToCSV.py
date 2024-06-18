import json
import csv
import pickle
import os
import sys
import re
from datetime import datetime

#----------------------------------------------------------------------------------------------------------------------
# Function to clean text by replacing newline characters with spaces
# Input - text: a string which may contain newline characters
# Output - a string with newline characters replaced by spaces
# Written by Adonijah Farner
#----------------------------------------------------------------------------------------------------------------------
def clean_text(text):
    """Replace newline characters with spaces, handling None values."""
    if text is None:
        return ""
    return text.replace('\n', ' ').replace('\r', ' ')
#----------------------------------------------------------------------------------------------------------------------
# End of function clean_text
#----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Function to find linked issues in the body text and the keyword used to describe the PR
# Input - text: The body of a pr
# Output - two lists, one of issues and another of keywords
# Written by Adonijah Farner
# ----------------------------------------------------------------------------------------------------------------------
def find_linked_issues(body_text):
    keywords = [
        "closes", "fixes", "resolves", "in", "solves",
        "addresses", "completes", "connects", "related to", "reverts",
        "implements", "references", "incorporates", "updates", "handles",
        "patches", "adds", "modifies", "enhances", "improves", "adjusts"
    ]
    linked_issues = []
    description_keywords = []

    for keyword in keywords:
        pattern = fr'{keyword} (#\d+|https://github\.com/\S+/issues/\d+)'
        matches = re.findall(pattern, body_text, re.IGNORECASE)

        for match in matches:
            linked_issues.append(match)
            description_keywords.append(keyword)

    return linked_issues, description_keywords
# ----------------------------------------------------------------------------------------------------------------------
# End of function find_linked_issues
# ----------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------
# Function to extract data from a pull request (PR) dictionary
# Input - pr: a dictionary representing a pull request
# Output - a dictionary with cleaned and structured data from the PR
# Written by Adonijah Farner
# Modified to include created_at, closed_at, userlogin, author_name, comments, and files_changed
# Date: 5/15/2024
#----------------------------------------------------------------------------------------------------------------------
def extract_data(pr):
    body_text = clean_text(pr.get("body", ""))
    linked_issues, description_keywords = find_linked_issues(body_text)

    data = {
        "issue": clean_text(pr.get("title", "")),
        "Pull Request": pr.get("is_pr", ""),
        "issue text": " | ".join(linked_issues),
        "issue description": " | ".join(description_keywords),
        "pull request text": clean_text(pr.get("title", "")),
        "pull request description": clean_text(pr.get("body", "")),
        #----------------------------------------------------------------------------------------------------------------------
        # Modified to include created_at, closed_at, and userlogin fields
        # Date: 5/15/2024
        #----------------------------------------------------------------------------------------------------------------------
        "created_at": clean_text(pr.get("created_at", "")),
        "closed_at": clean_text(pr.get("closed_at", "")),
        "userlogin": clean_text(pr.get("userlogin", "")),
    }

    # ----------------------------------------------------------------------------------------------------------------------
    # Modified to include concatenated list of comments
    # Date: 5/18/2024
    # Modified by Adonijah Farner
    # ----------------------------------------------------------------------------------------------------------------------
    # Process comments
    comments = []
    if pr.get("comments"):
        # print(f"Processing comments for PR: {pr}")
        for comment in pr["comments"].values():
            body = clean_text(comment.get("body", ""))
            # print(f"Found comment body: {body}")
            comments.append(body)
    data["comments"] = " | ".join(comments)

    # ----------------------------------------------------------------------------------------------------------------------
    # Modified to include concatenated list of files changed
    # Date: 5/18/2024
    # Modified by Adonijah Farner
    # ----------------------------------------------------------------------------------------------------------------------
    # Collect files changed across all commits
    files_changed = []
    commit_hashes = []
    commits = []
    if pr.get("commits"):
        for commit in pr["commits"].values():
            commit_date = commit.get("date", "")
            if commit_date:  # Only parse if commit_date is not empty
                try:
                    commit_date_obj = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
                    commits.append((commit_date_obj, commit.get("sha", ""), commit.get("author_name", "")))
                except ValueError:
                    continue  # Skip this commit if the date is invalid
            files = commit.get("files", {})
            if files:
                files_changed.extend(files.get("file_list", []))

    # Sort commits by date (newest to oldest)
    commits.sort(key=lambda x: x[0], reverse=True)
    sorted_commit_hashes = [commit[1] for commit in commits]
    newest_commit_hash = sorted_commit_hashes[0] if sorted_commit_hashes else ""

    data["files_changed"] = " | ".join(files_changed)
    data["commit_hashes"] = " | ".join(sorted_commit_hashes)
    data["newest_commit_hash"] = newest_commit_hash
    if commits:
        data["author_name"] = commits[0][2]  # Use the author of the newest commit

    return data
#----------------------------------------------------------------------------------------------------------------------
# End of function extract_data
#----------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------
# Function to convert JSON data to a specified pickle format and save it
# Input - data: a dictionary containing pull request data
#         pickle_file: the name of the output pickle file
# Output - a pickle file with the processed pull request data
# Written by Adonijah Farner
# Date: 5/21/2024
#----------------------------------------------------------------------------------------------------------------------
def convert_to_pickle(data, pickle_file):
    """Convert the JSON data to the specified pickle format and save it."""
    # Create a list to store the converted data
    pickle_data = []

    for idx, pr_id in enumerate(data.keys(), start=1):
        try:
            pr = data[pr_id]
            row_data = extract_data(pr)

            # Format the data into the desired structure
            formatted_data = [
                idx,
                pr_id,
                row_data.get("Pull Request", ""),
                row_data.get("issue text", ""),
                row_data.get("issue description", ""),
                row_data.get("pull request text", ""),
                row_data.get("pull request description", ""),
                row_data.get("created_at", ""),
                row_data.get("closed_at", ""),
                row_data.get("userlogin", ""),
                row_data.get("author_name", ""),
                row_data.get("comments", "").split(" | "),
                row_data.get("files_changed", "").split(" | "),
                row_data.get("commit_hashes", "").split(" | "),
                row_data.get("newest_commit_hash", "")
            ]

            # Append the formatted data to the list
            pickle_data.append(formatted_data)

        except Exception as e:
            print(f"Error processing entry {pr_id} for pickle: {e}")

    # ----------------------------------------------------------------------------------------------------------------------
    # Modified to have pickle  file name match json file name
    # Date: 6/10/2024
    # Modified by Adonijah Farner
    # ----------------------------------------------------------------------------------------------------------------------
    # Save the list to a pickle file
    with open(pickle_file, 'wb') as pf:
        pickle.dump(pickle_data, pf)

    print(f"Data successfully saved to {pickle_file}")
#----------------------------------------------------------------------------------------------------------------------
# End of function convert_to_pickle
#----------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------
# Main script to read JSON data, process it, and write to a CSV file
# Input - JSON file (jabref_output.json) containing pull request data
# Output - CSV file (jabref_output.csv) with processed pull request data
# Written by Adonijah Farner
# Modified to include created_at, closed_at, userlogin, author_name, comments, and files_changed
# Date: 5/15/2024
#----------------------------------------------------------------------------------------------------------------------
# Read the JSON file

# ----------------------------------------------------------------------------------------------------------------------
# Modified to read file from command line and have pickle and csv file name match json file name
# Date: 6/10/2024
# Modified by Adonijah Farner
# ----------------------------------------------------------------------------------------------------------------------

# Check if the filename is provided
if len(sys.argv) != 2:
    print("Usage: python JSONToCSV.py <filename.json>")
    sys.exit(1)

json_filename = sys.argv[1]

# Extract base name without extension
base_name = os.path.splitext(os.path.basename(json_filename))[0]

# Construct CSV and pickle file names
csv_filename = f"{base_name}.csv"
pickle_filename = f"{base_name}.pkl"

# Read the JSON file
with open(json_filename, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Open the CSV file for writing
with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    # Write the header
    header = [
        "Row #", "issue", "Pull Request", "issue text", "issue description",
        "pull request text", "pull request description", "created_at", "closed_at", "userlogin", "author_name",
        "comments", "files_changed", "commit_hashes", "newest_commit_hash"
    ]
    writer.writerow(header)

    # Write the data rows
    for idx, pr_id in enumerate(data.keys(), start=1):
        try:
            pr = data[pr_id]
            row_data = extract_data(pr)
            row = [idx, pr_id] + [row_data.get(col, "") for col in header[2:]]
            # print(f"Writing row for PR {pr_id}: {row}")  # Debug statement to check row data
            writer.writerow(row)
        except Exception as e:
            print(f"Error processing entry {pr_id}: {e}")

    print(f"Processed {idx} entries.")

    # Convert to pickle
    convert_to_pickle(data, pickle_filename)
#----------------------------------------------------------------------------------------------------------------------
# End of main script
#----------------------------------------------------------------------------------------------------------------------
