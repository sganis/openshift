import subprocess
import os
import sys
import time
import json
from pathlib import Path
from openai import OpenAI, RateLimitError
import dotenv

dotenv.load_dotenv()

SYSTEM_PROMPT = """You are an expert software engineer who writes clear, informative Git commit messages following best practices.

## Commit Message Format
```
<Type>(<scope>):
<description line 1>
<description line 2 if needed>
<more lines for complex changes>
```

## Types
- Feat: New feature
- Fix: Bug fix
- Refactor: Code restructuring without behavior change
- Docs: Documentation changes
- Style: Formatting, whitespace (no code logic change)
- Test: Adding or modifying tests
- Chore: Build process, dependencies, config
- Perf: Performance improvement

## Rules
1. First line: Type(scope): only, capitalized (no description on this line)
2. Following lines: describe WHAT changed and WHY
3. Scale detail to complexity: simple changes get 1-2 lines, complex changes get more
4. Use imperative mood ("Add" not "Added")
5. Be specific about impact and reasoning

## Examples

Simple change:
Feat(docker):
Add 'll' alias for directory listing.

Medium change:
Fix(api):
Handle null response from payment gateway.
Prevents 500 errors when gateway times out during peak traffic.

Complex change:
Refactor(auth):
Extract token validation into dedicated middleware.
Centralizes JWT verification logic previously duplicated across 5 controllers.
Adds automatic token refresh for requests within 5 minutes of expiry.
Improves testability by isolating auth concerns.

Analyze the diff carefully. Identify:
- Files changed and their purpose
- The nature of the change (new feature, bug fix, refactor, etc.)
- Any patterns suggesting the intent (error handling, optimization, etc.)"""

USER_PROMPT_TEMPLATE = """Generate a commit message for this diff.
First line: Type(scope): only (capitalized, nothing else on this line)
Following lines: describe what and why (1-5 lines depending on complexity)

**Original message (if any):** {original_message}

**Diff:**
```
{diff}
```

Respond with ONLY the commit message (no markdown, no extra explanation)."""


def get_openai_client() -> OpenAI:
    """Initialize and return OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment.", file=sys.stderr)
        print("Create a .env file with: OPENAI_API_KEY=your-key-here", file=sys.stderr)
        sys.exit(1)
    return OpenAI(api_key=api_key)


def run_git_command(args: list[str]) -> subprocess.CompletedProcess:
    """Run a git command and return the result."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    return result


def get_commit_logs(limit: int | None = None, since: str | None = None) -> list[dict]:
    """Retrieve commit metadata from Git history."""
    args = ["log", "--pretty=format:%H|%an|%ad|%s", "--date=iso"]
    
    if limit:
        args.append(f"-n{limit}")
    if since:
        args.append(f"--since={since}")
    
    result = run_git_command(args)
    
    if result.returncode != 0:
        print(f"Error reading git log: {result.stderr}", file=sys.stderr)
        return []
    
    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|", 3)  # Split into max 4 parts (subject may contain |)
        if len(parts) >= 4:
            commits.append({
                "hash": parts[0],
                "author": parts[1],
                "date": parts[2],
                "original_message": parts[3]
            })
    return commits


def get_commit_diff(commit_hash: str, max_chars: int = 12000) -> str | None:
    """Retrieve the diff for a commit, handling edge cases."""
    # Check if this is the first commit (no parent)
    parent_check = run_git_command(["rev-parse", f"{commit_hash}^"])
    
    if parent_check.returncode != 0:
        # First commit - diff against empty tree
        result = run_git_command([
            "diff-tree", "--patch", "--unified=3",
            "--root", commit_hash
        ])
    else:
        result = run_git_command([
            "diff", f"{commit_hash}^!", "--unified=3"
        ])
    
    if result.returncode != 0:
        return None
    
    diff = result.stdout
    
    # Smart truncation: try to keep complete file diffs
    if len(diff) > max_chars:
        truncated = diff[:max_chars]
        # Find the last complete file boundary
        last_diff_marker = truncated.rfind("\ndiff --git")
        if last_diff_marker > max_chars // 2:
            truncated = truncated[:last_diff_marker]
        truncated += "\n\n[... diff truncated due to size ...]"
        return truncated
    
    return diff


def generate_commit_message(
    client: OpenAI,
    diff: str,
    original_message: str,
    model: str = "gpt-4o",
    max_retries: int = 3
) -> str | None:
    """Generate a commit message using OpenAI API with retry logic."""
    user_prompt = USER_PROMPT_TEMPLATE.format(
        original_message=original_message or "(none)",
        diff=diff
    )
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.3  # Lower temperature for more consistent output
            )
            return response.choices[0].message.content.strip()
        
        except RateLimitError:
            wait_time = 2 ** attempt * 5  # Exponential backoff
            print(f"  Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"  API error: {e}", file=sys.stderr)
            return None
    
    return None


def save_results(results: list[dict], output_path: Path):
    """Save results to JSON for later use."""
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate meaningful commit messages using AI"
    )
    parser.add_argument(
        "-n", "--limit", type=int, default=None,
        help="Number of commits to process (default: all)"
    )
    parser.add_argument(
        "--since", type=str, default=None,
        help="Process commits since date (e.g., '2024-01-01')"
    )
    parser.add_argument(
        "--model", type=str, default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)"
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="Save results to JSON file"
    )
    parser.add_argument(
        "--delay", type=float, default=0.5,
        help="Delay between API calls in seconds (default: 0.5)"
    )
    
    args = parser.parse_args()
    
    # Verify we're in a git repo
    if run_git_command(["rev-parse", "--git-dir"]).returncode != 0:
        print("Error: Not a git repository", file=sys.stderr)
        sys.exit(1)
    
    client = get_openai_client()
    
    print("Fetching commit history...")
    commits = get_commit_logs(limit=args.limit, since=args.since)
    
    if not commits:
        print("No commits found.")
        return
    
    print(f"Processing {len(commits)} commits...\n")
    
    results = []
    
    for i, commit in enumerate(commits, 1):
        commit_hash = commit["hash"]
        short_hash = commit_hash[:8]
        
        date_short = commit["date"][:10]  # Just YYYY-MM-DD
        print(f"[{i}/{len(commits)}] {short_hash} | {date_short} | {commit['author'][:15]:<15} | {commit['original_message'][:40]}")
        
        diff = get_commit_diff(commit_hash)
        
        if not diff or not diff.strip():
            print("  ⚠ No diff available, skipping")
            continue
        
        new_message = generate_commit_message(
            client, diff, commit["original_message"], model=args.model
        )
        
        if new_message:
            msg_lines = new_message.strip().split("\n")
            print(f"  ✓ {msg_lines[0]}")
            for line in msg_lines[1:]:
                if line.strip():
                    print(f"    {line}")
            results.append({
                "hash": commit_hash,
                "author": commit["author"],
                "date": commit["date"],
                "original": commit["original_message"],
                "suggested": new_message
            })
        else:
            print("  ✗ Failed to generate message")
        
        if i < len(commits):
            time.sleep(args.delay)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Processed: {len(results)}/{len(commits)} commits")
    
    if args.output:
        save_results(results, Path(args.output))
    else:
        print("\nTip: Use -o results.json to save for later review")


if __name__ == "__main__":
    main()