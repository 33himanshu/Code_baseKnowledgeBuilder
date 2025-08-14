import os
from github import Github
from typing import Optional, List
from dotenv import load_dotenv
import requests
import base64
import time
from typing import Dict, Any, List, Optional, Set, Union
from urllib.parse import urlparse
import fnmatch

load_dotenv()

class GitHubService:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.client = Github(self.token)
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def validate_repo(self, repo_url: str) -> bool:
        """Validate if the repository URL is valid and accessible."""
        try:
            repo = self._get_repo_from_url(repo_url)
            return True
        except Exception:
            return False

    def fetch_repository(self, repo_url: str):
        """Fetch repository information and contents."""
        repo = self._get_repo_from_url(repo_url)
        return {
            "name": repo.name,
            "description": repo.description,
            "language": repo.language,
            "created_at": repo.created_at.isoformat(),
            "files": self._fetch_files(repo)
        }

    def _get_repo_from_url(self, url: str):
        """Extract repository information from URL and get repository object."""
        parts = url.strip("/").split("/")[-2:]
        if len(parts) != 2:
            raise ValueError("Invalid repository URL format")
        
        owner, repo_name = parts
        return self.client.get_repo(f"{owner}/{repo_name}")

    def _fetch_files(self, repo, path=""):
        """Recursively fetch files from repository."""
        contents = repo.get_contents(path)
        files = []
        
        for content in contents:
            if content.type == "dir":
                files.extend(self._fetch_files(repo, content.path))
            else:
                files.append({
                    "path": content.path,
                    "size": content.size,
                    "type": content.type
                })
        
        return files

    def fetch_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Get branches of the repository"""
        url = f"https://api.github.com/repos/{owner}/{repo}/branches"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 404:
            if not self.token:
                raise Exception(f"Error 404: Repository not found or is private.\n"
                              f"If this is a private repository, please provide a valid GitHub token via the 'token' argument or set the GITHUB_TOKEN environment variable.")
            else:
                raise Exception(f"Error 404: Repository not found or insufficient permissions with the provided token.\n"
                              f"Please verify the repository exists and the token has access to this repository.")
                
        if response.status_code != 200:
            raise Exception(f"Error fetching the branches of {owner}/{repo}: {response.status_code} - {response.text}")

        return response.json()

    def validate_repo(self, repo_url: str) -> bool:
        """Validate if a GitHub repository URL is valid."""
        try:
            # Parse URL to extract owner and repo
            parsed_url = urlparse(repo_url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            if len(path_parts) < 2:
                return False
                
            owner = path_parts[0]
            repo = path_parts[1]
            
            # Try to get repository info
            url = f"https://api.github.com/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 404:
                if not self.token:
                    raise Exception(f"Error 404: Repository not found or is private.\n"
                                  f"If this is a private repository, please provide a valid GitHub token via the 'token' argument or set the GITHUB_TOKEN environment variable.")
                else:
                    raise Exception(f"Error 404: Repository not found or insufficient permissions with the provided token.\n"
                                  f"Please verify the repository exists and the token has access to this repository.")
            
            return response.status_code == 200
            
        except Exception as e:
            raise Exception(f"Failed to validate repository: {str(e)}")

    def fetch_repository(self, repo_url: str, max_file_size: int = 1 * 1024 * 1024,  # 1 MB
                         include_patterns: Union[str, Set[str]] = None,
                         exclude_patterns: Union[str, Set[str]] = None) -> Dict[str, Any]:
        """Fetch repository data and files."""
        try:
            # Parse URL
            parsed_url = urlparse(repo_url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            if len(path_parts) < 2:
                raise ValueError(f"Invalid GitHub URL: {repo_url}")
            
            owner = path_parts[0]
            repo = path_parts[1]
            
            # Check if URL contains a specific branch/commit
            if len(path_parts) > 2 and 'tree' == path_parts[2]:
                join_parts = lambda i: '/'.join(path_parts[i:])

                branches = self.fetch_branches(owner, repo)
                branch_names = map(lambda branch: branch.get("name"), branches)

                if len(branches) == 0:
                    raise Exception("Failed to fetch branches")

                relevant_path = join_parts(3)
                filter_gen = (name for name in branch_names if relevant_path.startswith(name))
                ref = next(filter_gen, None)

                if ref is None:
                    tree = path_parts[3]
                    if not self.check_tree(owner, repo, tree):
                        raise Exception(f"The given path does not match with any branch and any tree in the repository.")
                    ref = tree

                part_index = 5 if '/' in ref else 4
                specific_path = join_parts(part_index) if part_index < len(path_parts) else ""
            else:
                ref = None
                specific_path = ""

            # Convert single pattern to set
            if include_patterns and isinstance(include_patterns, str):
                include_patterns = {include_patterns}
            if exclude_patterns and isinstance(exclude_patterns, str):
                exclude_patterns = {exclude_patterns}

            def should_include_file(file_path: str, file_name: str) -> bool:
                """Determine if a file should be included based on patterns"""
                if not include_patterns:
                    include_file = True
                else:
                    include_file = any(fnmatch.fnmatch(file_name, pattern) for pattern in include_patterns)

                if exclude_patterns and include_file:
                    exclude_file = any(fnmatch.fnmatch(file_path, pattern) for pattern in exclude_patterns)
                    return not exclude_file

                return include_file

            # Dictionary to store path -> content mapping
            files = {}
            skipped_files = []
            
            def fetch_contents(path):
                """Fetch contents of the repository at a specific path and commit"""
                url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
                params = {"ref": ref} if ref is not None else {}
                
                response = requests.get(url, headers=self.headers, params=params)
                
                if response.status_code == 403 and 'rate limit exceeded' in response.text.lower():
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    wait_time = max(reset_time - time.time(), 0) + 1
                    print(f"Rate limit exceeded. Waiting for {wait_time:.0f} seconds...")
                    time.sleep(wait_time)
                    return fetch_contents(path)
                    
                if response.status_code == 404:
                    if not self.token:
                        raise Exception(f"Error 404: Repository not found or is private.")
                    elif not path and ref == 'main':
                        raise Exception(f"Error 404: Repository not found. Check if the default branch is not 'main'")
                    else:
                        raise Exception(f"Error 404: Path '{path}' not found in repository or insufficient permissions with the provided token.")
                
                if response.status_code != 200:
                    raise Exception(f"Error fetching {path}: {response.status_code} - {response.text}")
                
                contents = response.json()
                
                # Handle both single file and directory responses
                if not isinstance(contents, list):
                    contents = [contents]
                
                for item in contents:
                    item_path = item["path"]
                    
                    if item["type"] == "file":
                        if not should_include_file(item_path, item["name"]):
                            print(f"Skipping {item_path}: Does not match include/exclude patterns")
                            continue
                        
                        file_size = item.get("size", 0)
                        if file_size > max_file_size:
                            skipped_files.append((item_path, file_size))
                            print(f"Skipping {item_path}: File size ({file_size} bytes) exceeds limit ({max_file_size} bytes)")
                            continue
                        
                        if "download_url" in item and item["download_url"]:
                            file_url = item["download_url"]
                            file_response = requests.get(file_url, headers=self.headers)
                            
                            content_length = int(file_response.headers.get('content-length', 0))
                            if content_length > max_file_size:
                                skipped_files.append((item_path, content_length))
                                print(f"Skipping {item_path}: Content length ({content_length} bytes) exceeds limit ({max_file_size} bytes)")
                                continue
                                
                            if file_response.status_code == 200:
                                files[item_path] = {
                                    "content": file_response.text,
                                    "size": file_size,
                                    "path": item_path
                                }
                                print(f"Downloaded: {item_path} ({file_size} bytes) ")
                            else:
                                print(f"Failed to download {item_path}: {file_response.status_code}")
                        else:
                            content_response = requests.get(item["url"], headers=self.headers)
                            if content_response.status_code == 200:
                                content_data = content_response.json()
                                if content_data.get("encoding") == "base64" and "content" in content_data:
                                    if len(content_data["content"]) * 0.75 > max_file_size:
                                        estimated_size = int(len(content_data["content"]) * 0.75)
                                        skipped_files.append((item_path, estimated_size))
                                        print(f"Skipping {item_path}: Encoded content exceeds size limit")
                                        continue
                                        
                                    file_content = base64.b64decode(content_data["content"]).decode('utf-8')
                                    files[item_path] = {
                                        "content": file_content,
                                        "size": file_size,
                                        "path": item_path
                                    }
                                    print(f"Downloaded: {item_path} ({file_size} bytes)")
                                else:
                                    print(f"Unexpected content format for {item_path}")
                            else:
                                print(f"Failed to get content for {item_path}: {content_response.status_code}")
                    
                    elif item["type"] == "dir":
                        fetch_contents(item_path)
            
            # Start crawling from the specified path
            fetch_contents(specific_path)
            
            return {
                "files": list(files.values()),
                "stats": {
                    "downloaded_count": len(files),
                    "skipped_count": len(skipped_files),
                    "skipped_files": skipped_files,
                    "base_path": specific_path,
                    "include_patterns": include_patterns,
                    "exclude_patterns": exclude_patterns
                },
                "metadata": {
                    "owner": owner,
                    "repo": repo,
                    "ref": ref,
                    "url": repo_url
                }
            }

        except Exception as e:
            raise Exception(f"Failed to fetch repository: {str(e)}")

    def check_tree(self, owner: str, repo: str, tree: str) -> bool:
        """Check if the repository has the given tree"""
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{tree}"
        response = requests.get(url, headers=self.headers)
        return response.status_code == 200

    def get_file_content(self, repo_url: str, file_path: str) -> str:
        """Get content of a specific file in the repository"""
        try:
            # Parse URL
            parsed_url = urlparse(repo_url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            if len(path_parts) < 2:
                raise ValueError(f"Invalid GitHub URL: {repo_url}")
            
            owner = path_parts[0]
            repo = path_parts[1]
            
            # Get file content
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 404:
                raise Exception(f"File not found: {file_path}")
            elif response.status_code != 200:
                raise Exception(f"Failed to get file content: {response.status_code} - {response.text}")
            
            content_data = response.json()
            if content_data.get("encoding") == "base64" and "content" in content_data:
                return base64.b64decode(content_data["content"]).decode('utf-8')
            else:
                raise Exception(f"Unexpected content format for {file_path}")
                
        except Exception as e:
            raise Exception(f"Failed to get file content: {str(e)}")

if __name__ == "__main__":
    # Example usage
    github_service = GitHubService()
    
    try:
        repo_url = "https://github.com/pydantic/pydantic/tree/6c38dc93f40a47f4d1350adca9ec0d72502e223f/pydantic"
        
        # Example: Get Python and Markdown files, but exclude test files
        result = github_service.fetch_repository(
            repo_url,
            max_file_size=1 * 1024 * 1024,  # 1 MB in bytes
            include_patterns={"*.py", "*.md"},  # Include Python and Markdown files
            exclude_patterns={"*test*.py", "*tests/*"}  # Exclude test files
        )
        
        files = result["files"]
        stats = result["stats"]
        
        print(f"\nDownloaded {stats['downloaded_count']} files.")
        print(f"Skipped {stats['skipped_count']} files due to size limits or patterns.")
        print(f"Base path: {stats['base_path']}")
        print(f"Include patterns: {stats['include_patterns']}")
        print(f"Exclude patterns: {stats['exclude_patterns']}")
        
        # Display all file paths
        print("\nFiles in repository:")
        for file in files:
            print(f"  {file['path']} ({file['size']} bytes)")
            
        # Example: accessing content of a specific file
        if files:
            sample_file = files[0]
            print(f"\nSample file: {sample_file['path']}")
            print(f"Content preview: {sample_file['content'][:200]}...")
            
    except Exception as e:
        print(f"Error: {str(e)}")
