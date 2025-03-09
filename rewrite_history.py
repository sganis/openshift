import subprocess
from openai import OpenAI
import git
import os 
import dotenv

# Load environment variables from a .env file
dotenv.load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
assert api_key, "API key not found. Make sure you have a .env file in the parent directory."

client = OpenAI()

def get_commit_logs():
    """Retrieve commit hashes, authors, and dates from the Git repository."""
    result = subprocess.run(
        ["git", "log", "--pretty=format:%H|%an|%ad", "--date=iso"],
        capture_output=True, text=True
    )
    commits = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split("|")
        if len(parts) == 3:
            commits.append({
                "hash": parts[0],
                "author": parts[1],
                "date": parts[2]
            })
    return commits

def get_commit_diff(commit_hash):
    """Retrieve the diff for a given commit hash."""
    result = subprocess.run(["git", "diff", f"{commit_hash}^!", "--unified=5"], capture_output=True, text=True)
    return result.stdout[:8980]

def generate_commit_message(diff):
    """Generate a meaningful commit message based on the diff."""
    prompt = f"Analyze the following Git diff and generate a concise and meaningful commit message:\n\n{diff}\n\nCommit message:"
    
    response = client.chat.completions.create(           
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert software engineer writing high-quality commit messages."},
                  {"role": "user", "content": prompt}],
        max_tokens=50
    )
    return response.choices[0].message.content.strip()


def main():
    print("Analyzing commit history...")
    
    commits = get_commit_logs()
    
    for commit in commits:
        commit_hash = commit["hash"]
        author = commit["author"]
        date = commit["date"]

        print(f"\nProcessing commit: {commit_hash}")
        print(f"Author: {author}")
        print(f"Date: {date}")

        diff = get_commit_diff(commit_hash)
        
        if not diff.strip():
            print("No changes detected, skipping...")
            continue
        
        new_message = generate_commit_message(diff)
        print(f"Message: {new_message}\n{'-'*60}")


if __name__ == "__main__":
    main()
