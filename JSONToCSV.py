import json
import csv

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

#----------------------------------------------------------------------------------------------------------------------
# Function to extract data from a pull request (PR) dictionary
# Input - pr: a dictionary representing a pull request
# Output - a dictionary with cleaned and structured data from the PR
# Written by Adonijah Farner
# Modified to include created_at, closed_at, userlogin, author_name, comments, and files_changed
# Date: 5/15/2024
#----------------------------------------------------------------------------------------------------------------------
def extract_data(pr):
    data = {
        "issue": clean_text(pr.get("title", "")),
        "Pull Request": pr.get("is_pr", ""),
        "issue text": clean_text(pr.get("title", "")),
        "issue description": clean_text(pr.get("body", "")),
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
    if pr.get("commits"):
        for commit in pr["commits"].values():
            files = commit.get("files", {})
            files_changed.extend(files.get("file_list", []))
            #----------------------------------------------------------------------------------------------------------------------
            # Modified to include author_name
            # Date: 5/15/2024
            #----------------------------------------------------------------------------------------------------------------------
            data["author_name"] = clean_text(commit.get("author_name", ""))
    data["files_changed"] = " | ".join(files_changed)

    return data
#----------------------------------------------------------------------------------------------------------------------
# End of function extract_data
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
with open('jabref_output.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Open the CSV file for writing
with open('jabref_output_V3.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    # Write the header
    header = [
        "Row #", "issue", "Pull Request", "issue text", "issue description",
        "pull request text", "pull request description", "created_at", "closed_at", "userlogin", "author_name", "comments", "files_changed"
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
#----------------------------------------------------------------------------------------------------------------------
# End of main script
#----------------------------------------------------------------------------------------------------------------------
