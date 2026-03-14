#!/usr/bin/env python3
"""
Advanced GitHub User Scraper
Scrapes comprehensive information including READMEs, project details, and work experience
"""

import requests
import json
import sys
import base64
import re
from datetime import datetime
from collections import defaultdict
from urllib.parse import quote

class AdvancedGitHubScraper:
    def __init__(self, username, token=None):
        """
        Initialize the scraper
        
        Args:
            username (str): GitHub username to scrape
            token (str): Optional GitHub API token for higher rate limits
        """
        self.username = username
        self.base_url = "https://api.github.com"
        self.raw_url = "https://raw.githubusercontent.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        
        if token:
            self.headers["Authorization"] = f"token {token}"
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.data = {}
    
    def _make_request(self, endpoint, is_raw=False):
        """Make API request and handle errors"""
        if is_raw:
            url = f"{self.raw_url}{endpoint}"
        else:
            url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text if is_raw else response.json()
        except requests.exceptions.RequestException as e:
            return None
    
    def scrape_profile(self):
        """Scrape user profile information"""
        print(f"[*] Scraping profile for {self.username}...")
        
        user_data = self._make_request(f"/users/{self.username}")
        if not user_data:
            return False
        
        self.data['profile'] = {
            'username': user_data.get('login'),
            'name': user_data.get('name'),
            'bio': user_data.get('bio'),
            'location': user_data.get('location'),
            'email': user_data.get('email'),
            'blog': user_data.get('blog'),
            'twitter': user_data.get('twitter_username'),
            'company': user_data.get('company'),
            'public_repos': user_data.get('public_repos'),
            'public_gists': user_data.get('public_gists'),
            'followers': user_data.get('followers'),
            'following': user_data.get('following'),
            'created_at': user_data.get('created_at'),
            'updated_at': user_data.get('updated_at'),
            'profile_url': user_data.get('html_url'),
            'avatar_url': user_data.get('avatar_url'),
            'hireable': user_data.get('hireable'),
            'type': user_data.get('type'),
        }
        
        print(f"    ✓ Profile scraped")
        return True
    
    def scrape_profile_readme(self):
        """Scrape the user's profile README"""
        print(f"[*] Scraping profile README...")
        
        readme_content = self._make_request(
            f"/{self.username}/{self.username}/main/README.md",
            is_raw=True
        )
        
        if not readme_content:
            # Try master branch
            readme_content = self._make_request(
                f"/{self.username}/{self.username}/master/README.md",
                is_raw=True
            )
        
        if readme_content:
            self.data['profile_readme'] = {
                'content': readme_content,
                'extracted_info': self._extract_profile_info(readme_content)
            }
            print(f"    ✓ Profile README found")
        else:
            self.data['profile_readme'] = {
                'content': None,
                'extracted_info': {}
            }
            print(f"    ⚠ Profile README not found")
        
        return True
    
    def _extract_profile_info(self, readme_content):
        """Extract work experience and other info from README"""
        info = {
            'work_experience': [],
            'skills': [],
            'projects_mentioned': [],
            'social_links': []
        }
        
        lines = readme_content.split('\n')
        
        # Extract work experience
        work_section = False
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['experience', 'worked', 'employment', 'career']):
                work_section = True
            
            if work_section and (line.startswith('#') and 'experience' not in line.lower()):
                work_section = False
            
            if work_section and any(keyword in line for keyword in ['@', '|', '-', '•']):
                cleaned = line.strip().lstrip('- •').strip()
                if cleaned and len(cleaned) > 5:
                    info['work_experience'].append(cleaned)
        
        # Extract skills
        skills_section = False
        for line in lines:
            if any(keyword in line.lower() for keyword in ['skills', 'technologies', 'tech stack']):
                skills_section = True
            
            if skills_section and line.startswith('#') and 'skill' not in line.lower():
                skills_section = False
            
            if skills_section and any(keyword in line for keyword in ['`', '-', '•', '|']):
                # Extract text between backticks or after bullets
                skills = re.findall(r'`([^`]+)`', line)
                if skills:
                    info['skills'].extend(skills)
        
        # Extract social links and URLs
        urls = re.findall(r'https?://[^\s\)]+', readme_content)
        info['social_links'] = list(set(urls))
        
        # Extract project mentions
        project_links = re.findall(r'\[([^\]]+)\]\(https://github\.com/([^\)]+)\)', readme_content)
        for name, repo_path in project_links:
            info['projects_mentioned'].append({
                'name': name,
                'repo': repo_path
            })
        
        return info
    
    def scrape_repositories(self, limit=None):
        """Scrape all repositories with README content"""
        print(f"[*] Scraping repositories...")
        
        repos = []
        page = 1
        per_page = 100
        count = 0
        
        while True:
            data = self._make_request(
                f"/users/{self.username}/repos?page={page}&per_page={per_page}&sort=updated&type=owner"
            )
            
            if not data or len(data) == 0:
                break
            
            for repo in data:
                if limit and count >= limit:
                    break
                
                repo_info = {
                    'name': repo.get('name'),
                    'url': repo.get('html_url'),
                    'description': repo.get('description'),
                    'stars': repo.get('stargazers_count'),
                    'forks': repo.get('forks_count'),
                    'watchers': repo.get('watchers_count'),
                    'language': repo.get('language'),
                    'topics': repo.get('topics', []),
                    'is_fork': repo.get('fork'),
                    'created_at': repo.get('created_at'),
                    'updated_at': repo.get('updated_at'),
                    'pushed_at': repo.get('pushed_at'),
                    'size': repo.get('size'),
                    'open_issues': repo.get('open_issues_count'),
                    'license': repo.get('license', {}).get('name') if repo.get('license') else None,
                    'is_private': repo.get('private'),
                    'homepage': repo.get('homepage'),
                    'readme': None,
                    'readme_extracted_info': {}
                }
                
                # Get README for this repo
                readme_content = self._get_repo_readme(self.username, repo.get('name'))
                if readme_content:
                    repo_info['readme'] = readme_content
                    repo_info['readme_extracted_info'] = self._extract_project_info(readme_content)
                
                repos.append(repo_info)
                count += 1
            
            if limit and count >= limit:
                break
            
            page += 1
        
        self.data['repositories'] = repos
        print(f"    ✓ Found {len(repos)} repositories with detailed info")
        return True
    
    def _get_repo_readme(self, owner, repo_name):
        """Get README content from a repository"""
        readme_paths = [
            f"/{owner}/{repo_name}/main/README.md",
            f"/{owner}/{repo_name}/master/README.md",
            f"/{owner}/{repo_name}/main/README.rst",
            f"/{owner}/{repo_name}/master/README.rst",
            f"/{owner}/{repo_name}/main/readme.md",
            f"/{owner}/{repo_name}/master/readme.md",
        ]
        
        for path in readme_paths:
            content = self._make_request(path, is_raw=True)
            if content:
                return content
        
        return None
    
    def _extract_project_info(self, readme_content):
        """Extract key information from project README"""
        info = {
            'description': '',
            'features': [],
            'installation': '',
            'usage': [],
            'tech_stack': [],
            'dependencies': [],
            'links': []
        }
        
        lines = readme_content.split('\n')
        
        # Get description from first non-heading paragraph
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('#') and not line.startswith('!['):
                info['description'] = line.strip()
                break
        
        # Extract features
        features_section = False
        for line in lines:
            if any(keyword in line.lower() for keyword in ['features', 'capabilities', 'highlights']):
                features_section = True
                continue
            
            if features_section and line.startswith('#'):
                features_section = False
            
            if features_section and any(marker in line for marker in ['- ', '• ', '* ', '✓', '✨']):
                cleaned = re.sub(r'^[\s\-•*✓✨]+', '', line).strip()
                if cleaned:
                    info['features'].append(cleaned)
        
        # Extract installation section
        for i, line in enumerate(lines):
            if 'installation' in line.lower() or 'setup' in line.lower():
                installation = []
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].startswith('#'):
                        break
                    if lines[j].strip() and not lines[j].startswith('>'):
                        installation.append(lines[j].strip())
                info['installation'] = ' '.join(installation)
                break
        
        # Extract usage examples
        usage_section = False
        for line in lines:
            if 'usage' in line.lower() or 'example' in line.lower():
                usage_section = True
                continue
            
            if usage_section and line.startswith('#'):
                usage_section = False
            
            if usage_section and line.startswith('```'):
                continue
            
            if usage_section and line.strip() and not line.startswith('>'):
                info['usage'].append(line.strip())
        
        # Extract tech stack and dependencies
        for line in lines:
            # Look for language/framework mentions
            if any(tech in line for tech in ['python', 'javascript', 'typescript', 'rust', 'go', 'java', 'c++', 'react', 'vue', 'angular', 'django', 'flask', 'fastapi']):
                tech_match = re.findall(r'\b(Python|JavaScript|TypeScript|Rust|Go|Java|C\+\+|React|Vue|Angular|Django|Flask|FastAPI|Node\.js|Express|SQL|MongoDB|PostgreSQL|Docker|Kubernetes)\b', line, re.IGNORECASE)
                info['tech_stack'].extend(tech_match)
        
        # Extract links
        links = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', readme_content)
        info['links'] = [{'text': text, 'url': url} for text, url in links]
        
        # Remove duplicates
        info['tech_stack'] = list(set(info['tech_stack']))
        
        return info
    
    def scrape_languages(self):
        """Scrape programming languages used"""
        print(f"[*] Analyzing programming languages...")
        
        repos = self.data.get('repositories', [])
        language_stats = defaultdict(int)
        
        for repo in repos:
            if repo['language']:
                language_stats[repo['language']] += 1
        
        self.data['languages'] = dict(sorted(
            language_stats.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        print(f"    ✓ Found {len(self.data['languages'])} languages")
        return True
    
    def scrape_top_repos(self, limit=10):
        """Get top repositories by stars"""
        print(f"[*] Identifying top repositories...")
        
        repos = sorted(
            self.data.get('repositories', []),
            key=lambda x: x['stars'],
            reverse=True
        )[:limit]
        
        self.data['top_repositories'] = repos
        print(f"    ✓ Found top {len(repos)} repositories")
        return True
    
    def calculate_stats(self):
        """Calculate additional statistics"""
        print(f"[*] Calculating statistics...")
        
        repos = self.data.get('repositories', [])
        
        stats = {
            'total_stars': sum(repo['stars'] for repo in repos),
            'total_forks': sum(repo['forks'] for repo in repos),
            'most_starred_repo': max(repos, key=lambda x: x['stars']) if repos else None,
            'most_forked_repo': max(repos, key=lambda x: x['forks']) if repos else None,
            'average_stars_per_repo': sum(repo['stars'] for repo in repos) / len(repos) if repos else 0,
            'total_open_issues': sum(repo['open_issues'] for repo in repos),
            'repositories_with_topics': sum(1 for repo in repos if repo['topics']),
            'repositories_with_readme': sum(1 for repo in repos if repo['readme']),
            'most_used_language': self.data.get('languages', {}) and list(self.data['languages'].keys())[0],
        }
        
        self.data['statistics'] = stats
        print(f"    ✓ Statistics calculated")
    
    def scrape_all(self, repo_limit=None):
        """Scrape all available data"""
        print(f"\n{'='*70}")
        print(f"Advanced GitHub User Scraper - {self.username}")
        print(f"{'='*70}\n")
        
        if not self.scrape_profile():
            print(f"Error: User '{self.username}' not found")
            return False
        
        self.scrape_profile_readme()
        self.scrape_repositories(limit=repo_limit)
        self.scrape_languages()
        self.scrape_top_repos(limit=10)
        self.calculate_stats()
        
        print(f"\n{'='*70}")
        print(f"Scraping complete!")
        print(f"{'='*70}\n")
        
        return True
    
    def save_to_json(self, filename=None):
        """Save scraped data to JSON file"""
        if filename is None:
            filename = f"{self.username}_github_detailed.json"
        
        # Create a serializable version
        data_to_save = self._make_serializable(self.data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"[+] Data saved to {filename}")
        return filename
    
    def _make_serializable(self, obj):
        """Convert objects to serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)
    
    def print_detailed_summary(self):
        """Print detailed summary with project info"""
        profile = self.data.get('profile', {})
        stats = self.data.get('statistics', {})
        languages = self.data.get('languages', {})
        profile_info = self.data.get('profile_readme', {}).get('extracted_info', {})
        
        print(f"\n{'='*70}")
        print(f"DETAILED PROFILE SUMMARY - {profile.get('username', 'N/A').upper()}")
        print(f"{'='*70}\n")
        
        # Basic Info
        print(f"{'─'*70}")
        print("BASIC INFORMATION")
        print(f"{'─'*70}")
        print(f"Name: {profile.get('name', 'N/A')}")
        print(f"Bio: {profile.get('bio', 'N/A')}")
        print(f"Location: {profile.get('location', 'N/A')}")
        print(f"Company: {profile.get('company', 'N/A')}")
        print(f"Website: {profile.get('blog', 'N/A')}")
        print(f"Twitter: @{profile.get('twitter', 'N/A')}")
        print(f"Member Since: {profile.get('created_at', 'N/A')[:10]}")
        print(f"Followers: {profile.get('followers', 0):,} | Following: {profile.get('following', 0):,}")
        
        # Work Experience
        if profile_info.get('work_experience'):
            print(f"\n{'─'*70}")
            print("WORK EXPERIENCE (from profile README)")
            print(f"{'─'*70}")
            for experience in profile_info.get('work_experience', [])[:10]:
                print(f"  • {experience}")
        
        # Skills from README
        if profile_info.get('skills'):
            print(f"\n{'─'*70}")
            print("SKILLS (from profile README)")
            print(f"{'─'*70}")
            skills = list(set(profile_info.get('skills', [])))[:20]
            print(f"  {', '.join(skills)}")
        
        # Repository Statistics
        print(f"\n{'─'*70}")
        print("REPOSITORY STATISTICS")
        print(f"{'─'*70}")
        print(f"Public Repositories: {profile.get('public_repos', 0):,}")
        print(f"Total Stars: {stats.get('total_stars', 0):,}")
        print(f"Total Forks: {stats.get('total_forks', 0):,}")
        print(f"Total Open Issues: {stats.get('total_open_issues', 0):,}")
        print(f"Repositories with README: {stats.get('repositories_with_readme', 0)}")
        print(f"Avg Stars Per Repo: {stats.get('average_stars_per_repo', 0):.2f}")
        
        # Top Projects
        top_repos = self.data.get('top_repositories', [])
        if top_repos:
            print(f"\n{'─'*70}")
            print("TOP PROJECTS BY STARS")
            print(f"{'─'*70}")
            for i, repo in enumerate(top_repos[:5], 1):
                print(f"\n  {i}. {repo['name']} ⭐ {repo['stars']:,}")
                if repo['description']:
                    print(f"     Description: {repo['description'][:100]}")
                
                repo_info = repo.get('readme_extracted_info', {})
                
                if repo_info.get('description'):
                    print(f"     What it does: {repo_info['description'][:120]}")
                
                if repo['language']:
                    print(f"     Language: {repo['language']}")
                
                if repo_info.get('features'):
                    print(f"     Key Features:")
                    for feature in repo_info['features'][:3]:
                        print(f"       - {feature[:80]}")
                
                if repo['topics']:
                    print(f"     Topics: {', '.join(repo['topics'][:5])}")
        
        # Languages
        if languages:
            print(f"\n{'─'*70}")
            print("TOP PROGRAMMING LANGUAGES")
            print(f"{'─'*70}")
            for lang, count in list(languages.items())[:10]:
                bar = "█" * count
                print(f"  {lang:15} {bar} ({count} repos)")
        
        print(f"\n{'='*70}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python advanced_github_scraper.py <username> [--token YOUR_TOKEN] [--limit NUM]")
        print("\nExample:")
        print("  python advanced_github_scraper.py torvalds")
        print("  python advanced_github_scraper.py octocat --token ghp_xxxxxxxxxxxx --limit 50")
        print("\nNote: Using a token increases API rate limits from 60 to 5000 requests/hour")
        sys.exit(1)
    
    username = sys.argv[1]
    token = None
    repo_limit = None
    
    # Parse arguments
    for i in range(2, len(sys.argv)):
        if sys.argv[i] == "--token" and i + 1 < len(sys.argv):
            token = sys.argv[i + 1]
        elif sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
            try:
                repo_limit = int(sys.argv[i + 1])
            except ValueError:
                pass
    
    # Create scraper and run
    scraper = AdvancedGitHubScraper(username, token)
    
    if scraper.scrape_all(repo_limit=repo_limit):
        scraper.print_detailed_summary()
        scraper.save_to_json()
    else:
        print(f"Failed to scrape user: {username}")
        sys.exit(1)


if __name__ == "__main__":
    main()
