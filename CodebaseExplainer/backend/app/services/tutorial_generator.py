from .nodes import (
    FetchRepo,
    IdentifyAbstractions,
    AnalyzeRelationships,
    OrderChapters,
    WriteChapters,
    CombineTutorial
)
from typing import Dict, Any
import copy

class TutorialGenerator:
    def __init__(self):
        # Create the workflow
        self.flow = FetchRepo() >> IdentifyAbstractions() >> AnalyzeRelationships() >> OrderChapters() >> WriteChapters() >> CombineTutorial()

    def generate(
        self,
        repo_url: str,
        language: str = "english",
        include_patterns: list = None,
        exclude_patterns: list = None,
        max_file_size: int = 100000
    ) -> Dict[str, Any]:
        """Generate a complete tutorial for a codebase using the node-based workflow."""
        try:
            # Prepare shared data
            shared = {
                "repo_url": repo_url,
                "language": language,
                "include_patterns": include_patterns or [
                    "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", 
                    "*.pyi", "*.pyx", "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst",
                    "Dockerfile", "Makefile", "*.yaml", "*.yml"
                ],
                "exclude_patterns": exclude_patterns or [
                    "venv/*", ".venv/*", "*test*", "tests/*", "docs/*", "examples/*",
                    "v1/*", "dist/*", "build/*", "experimental/*", "deprecated/*",
                    "legacy/*", ".git/*", ".github/*", ".next/*", ".vscode/*",
                    "obj/*", "bin/*", "node_modules/*", "*.log"
                ],
                "max_file_size": max_file_size
            }

            # Run the workflow
            result = self.flow.run(shared)

            return {
                "status": "success",
                "tutorial": result,
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "language": language
            }

        except Exception as e:
            raise Exception(f"Failed to generate tutorial: {str(e)}")
