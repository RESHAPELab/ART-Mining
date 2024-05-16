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
# Modified to include created_at, closed_at, userlogin, author_name, and comments
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
        # Modified to include created_at, closed_at, userlogin, and comments fields
        # Date: 5/15/2024
        # Modified by Adonijah Farner
        #----------------------------------------------------------------------------------------------------------------------
        "created_at": clean_text(pr.get("created_at", "")),
        "closed_at": clean_text(pr.get("closed_at", "")),
        "userlogin": clean_text(pr.get("userlogin", "")),
        "comments": " | ".join(f"{c['userlogin']}: {clean_text(c['body'])}" for c in pr.get("comments", {}).values())
    }

    # Extract the last commit
    if pr.get("commits"):
        last_commit = pr["commits"][str(len(pr["commits"]) - 1)]
        #----------------------------------------------------------------------------------------------------------------------
        # Modified to include author_name
        # Date: 5/15/2024
        # Modified by Adonijah Farner
        #----------------------------------------------------------------------------------------------------------------------
        data["author_name"] = clean_text(last_commit.get("author_name", ""))

    return data
#----------------------------------------------------------------------------------------------------------------------
# End of function extract_data
#----------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------
# Main script to read JSON data, process it, and write to a CSV file
# Input - JSON file (jabref_output.json) containing pull request data
# Output - CSV file (jabref_output.csv) with processed pull request data
# Written by Adonijah Farner
# Modified to include created_at, closed_at, userlogin, author_name, and comments
# Date: 5/15/2024
# Modified by Adonijah Farner
#----------------------------------------------------------------------------------------------------------------------
# Read the JSON file
with open('jabref_output.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Open the CSV file for writing
with open('jabref_output.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    # Write the header
    header = [
        "Row #", "issue", "Pull Request", "issue text", "issue description",
        "pull request text", "pull request description", "created_at", "closed_at", "userlogin", "author_name", "comments"
    ]
    writer.writerow(header)

    # Write the data rows
    for idx, pr_id in enumerate(data.keys(), start=1):
        try:
            pr = data[pr_id]
            row_data = extract_data(pr)
            row = [idx] + [row_data.get(col, "") for col in header[1:]]
            writer.writerow(row)
        except Exception as e:
            print(f"Error processing entry {pr_id}: {e}")

    print(f"Processed {idx} entries.")
#----------------------------------------------------------------------------------------------------------------------
# End of main script
#----------------------------------------------------------------------------------------------------------------------
