import argparse
import requests
from github import Github
import keyring
import tempfile


def create_pr(repo_url, issue_number, fix_details,):
    """
    Creates a pull request for the specified issue on the given repo.

    Args:
        repo_url (str): URL of the GitHub repository.
        issue_number (int): Issue number to address.
        fix_details (str): Description of the fix implemented.
        repo_content (str): Content of the repository to send to Gemini.
    """

    # Construct the API request URL
    url = f"https://api.gemini.com/v1/projects/{repo_url}/issues/{issue_number}/pull-requests"

    # Prepare the request data
    data = {
        "title": f"Fix issue #{issue_number}",
        "body": f"{fix_details}\n\nThis pull request addresses issue #{issue_number}.",
        # Add other necessary data for the PR
    }

    # Set headers with API key
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}"
    }

    # Send the POST request to create the PR
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"Pull request created successfully for issue #{issue_number}")
    else:
        print(f"Error creating pull request: {response.text}")

def send_repo_to_gemini(repo):
    """
    Downloads the specified GitHub repository and sends it to Gemini for analysis.

    Args:
        repo (github.Repository.Repository): The GitHub repository object.
    """

    # Create a temporary directory to store the downloaded repository
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download the repository as a ZIP archive
        repo.archive(temp_dir, format="zipball")

        # Get the path to the ZIP archive
        zip_path = f"{temp_dir}/{repo.name}-master.zip"  # Adjust filename if needed

        # Read the ZIP archive content
        with open(zip_path, "rb") as zip_file:
            repo_content = zip_file.read()

        # Send the repository content to Gemini API
        url = "https://api.gemini.com/v1/projects"  # Replace with actual Gemini endpoint
        headers = {
            "Authorization": f"Bearer {GEMINI_API_KEY}"
        }
        data = {
            "name": repo.name,
            "content": repo_content,
            # Add other necessary data for Gemini analysis
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:
            print("Repository sent to Gemini for analysis successfully.")
        else:
            print(f"Error sending repository to Gemini: {response.text}")

def configure():
    """
    Prompts the user for a GitHub access token and stores it.
    """

    github_token = input("Enter your GitHub access token: ")
    gemini_api_key = input("Enter your Gemini API key: ")

    # Store the token in the keyring
    keyring.set_password("your_app_name", "github_token", github_token)
    keyring.set_password("your_app_name", "gemini_api_key", gemini_api_key)

    print("Credentials configured successfully!")

def main():
    """
    Parses command-line arguments and calls appropriate functions.
    """

    parser = argparse.ArgumentParser(description="Create PRs using Gemini API")
    parser.add_argument("-url","repo_url", help="URL of the GitHub repository")
    parser.add_argument("-i", "--issue_number", type=int, help="Issue number to address")
    parser.add_argument("-env","--configure", action="store_true", help="Configure credentials needed")


    args = parser.parse_args()

    if args.configure:
        configure()
        return # Exit after config

    # Get Credentials
    github_token = keyring.get_password("github_issue_fixer", "github_token")
    gemini_api_key = keyring.get_password("github_issue_fixer", "gemini_api_key")

    if not args.repo_url:
        parser.error("The 'repo_url' argument is required.")

    # Connect to GitHub
    gh = Github(github_token)

    # Extract repository information
    repo_owner, repo_name = args.repo_url.split("/")[-2:]
    repo = gh.get_repo(f"{repo_owner}/{repo_name}")


    # Get issue details if issue number is provided
    if args.issue_number:
        try:
            issue = repo.get_issue(number=args.issue_number)
            # Extract issue details for fix_details
            # ...
        except GithubException as e:
            if e.status == 404:
                print(f"Error: Issue #{args.issue_number} does not exist in the repository.")
            else:
                print(f"An error occurred while fetching issue details: {e}")

    # Get repository content (replace with your method of obtaining content)
    repo_content = "REPO_CONTENT"

    # Send repository to Gemini
    send_repo_to_gemini(args.repo_url, repo_content)

    # Create the pull request
    create_pr(args.repo_url, args.issue_number, fix_details, repo_content)

if __name__ == "__main__":
    main()