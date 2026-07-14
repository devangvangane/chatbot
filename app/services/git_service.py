# from github import Github, Auth
# from app.config import config
import json

# auth = Auth.Token(config.GITHUB_TOKEN)
# g = Github(auth=auth)

# user = g.get_user()
# with open("github.json", "w", encoding="utf-8") as f:
#     for repo in user.get_repos():
#         user_data = {
#             "name": repo.name,
#             "repo_desc": repo.description,
#             "repo_html": repo.html_url
#         }
#         json.dump(user_data, f, indent=4)
#         # print(repo.name, repo.description, repo.html_url)


from github import Github, Auth
from typing import List, Dict
from app.config import config
import uuid


class GitHubService:

    def __init__(
        self,
        username: str = config.GITHUB_USERNAME,
        token: str = config.GITHUB_TOKEN,
        excluded_repos: list[str] = config.EXCLUDED_REPOS,
    ):
        auth = Auth.Token(token)
        self.g = Github(auth=auth)
        self.username = username
        self.excluded_repos = set(excluded_repos)

    def get_repos(self) -> List[Dict]:
        """
        Fetch all public, non-forked, non-excluded repos for the configured GitHub user.
        """

        repos = []

        user = self.g.get_user(self.username)

        for repo in user.get_repos():
            if repo.fork:
                continue
            if repo.private:
                continue
            if repo.html_url in self.excluded_repos:
                print(f"Skipping (excluded): {repo.name}")
                continue

            print(f"Fetching: {repo.full_name}")

            repos.append({
                "id": str(uuid.uuid4()),
                "title": repo.name,
                "description": repo.description or "No description provided.",
                "url": repo.html_url,
            })

        return repos


if __name__ == "__main__":
    github_s = GitHubService()
    repos = github_s.get_repos()
    print(f"Fetched {len(repos)} repos")
    for r in repos:
        print(r)