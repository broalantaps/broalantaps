"""Refresh the profile badge using public GitHub repository star counts."""

import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


OWNER = "broalantaps"
EXTRA_REPOS = ("microsoft/AnthropomorphicIntelligence",)
ROOT = Path(__file__).resolve().parents[1]


def github(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "broalantaps-profile-stats",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"https://api.github.com/{path}", headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    repositories = {}
    page = 1
    while True:
        batch = github(f"users/{OWNER}/repos?type=owner&per_page=100&page={page}")
        for repo in batch:
            repositories[repo["full_name"].lower()] = repo["stargazers_count"]
        if len(batch) < 100:
            break
        page += 1
    for name in EXTRA_REPOS:
        repo = github(f"repos/{name}")
        repositories[repo["full_name"].lower()] = repo["stargazers_count"]

    total = sum(repositories.values())
    value = f"{total:,}"
    value_width = max(40, len(value) * 8 + 16)
    width = 76 + value_width
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20" role="img" aria-label="Total stars: {value}">
  <title>Total stars: {value}</title>
  <clipPath id="r"><rect width="{width}" height="20" rx="3"/></clipPath>
  <g clip-path="url(#r)">
    <path fill="#555" d="M0 0h76v20H0z"/>
    <path fill="#e3b341" d="M76 0h{value_width}v20H76z"/>
  </g>
  <g font-family="Verdana,DejaVu Sans,sans-serif" font-size="11" text-anchor="middle">
    <text x="38" y="14" fill="#fff">Total stars</text>
    <text x="{76 + value_width / 2:g}" y="14" fill="#24292f">{value}</text>
  </g>
</svg>
'''
    output = ROOT / "assets" / "total-stars.svg"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")
    print(f"Total stars: {total} across {len(repositories)} repositories")
    for name, stars in sorted(repositories.items()):
        print(f"  {name}: {stars}")


if __name__ == "__main__":
    main()
