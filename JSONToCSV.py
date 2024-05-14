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
#----------------------------------------------------------------------------------------------------------------------
def extract_data(pr):
    data = {
        "issue": clean_text(pr.get("title", "")),
        "Pull Request": pr.get("is_pr", ""),
        "issue text": clean_text(pr.get("title", "")),
        "issue description": clean_text(pr.get("body", "")),
        "pull request text": clean_text(pr.get("title", "")),
        "pull request description": clean_text(pr.get("body", "")),
    }

    # Extract the last commit
    if pr.get("commits"):
        last_commit = pr["commits"][str(len(pr["commits"]) - 1)]
        for key, value in last_commit.items():
            if key == "files":
                data["files"] = ", ".join(value["file_list"])
            elif key == "patch_text":
                data["patch_text"] = " ".join(clean_text(patch) for patch in value)
            else:
                data[key] = clean_text(value)

    # Extract comments
    if pr.get("comments"):
        for i, comment in pr["comments"].items():
            data[f"userlogin_comment_{i}"] = comment["userlogin"]
            data[f"comment_body_{i}"] = clean_text(comment["body"])

    return data
#----------------------------------------------------------------------------------------------------------------------
# End of function extract_data
#----------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------
# Main script to read JSON data, process it, and write to a CSV file
# Input - JSON file (jabref_output.json) containing pull request data
# Output - CSV file (jabref_output.csv) with processed pull request data
# Written by Adonijah Farner
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
        "pull request text", "pull request description"
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
