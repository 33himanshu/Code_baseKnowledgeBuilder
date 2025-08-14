import os
import json
import difflib
from typing import Dict, List, Any
from pathlib import Path

# Import both implementations
import sys
import os

# Add both project directories to Python path
sys.path.append(os.path.abspath("../.."))
sys.path.append(os.path.abspath("../../../PocketFlow-Tutorial-Codebase-Knowledge"))

from backend.app.main import run_flow as run_our_flow
from flow import run_flow as run_pocketflow_flow

def similar_content(str1: str, str2: str, threshold: float = 0.9) -> bool:
    """
    Check if two strings are similar enough based on similarity ratio.
    """
    seq = difflib.SequenceMatcher(None, str1, str2)
    return seq.ratio() >= threshold

def compare_files_in_directories(dir1: str, dir2: str) -> None:
    """
    Compare files in two directories recursively.
    """
    dir1_files = set(Path(dir1).rglob("*"))
    dir2_files = set(Path(dir2).rglob("*"))
    
    # Check if both directories have the same files
    assert len(dir1_files) == len(dir2_files), \
        f"Directory structures differ: {len(dir1_files)} vs {len(dir2_files)} files"
    
    # Compare each file
    for file1, file2 in zip(sorted(dir1_files), sorted(dir2_files)):
        assert file1.name == file2.name, f"File name mismatch: {file1.name} vs {file2.name}"
        
        if file1.is_file() and file2.is_file():
            with open(file1, 'r', encoding='utf-8') as f1, \
                 open(file2, 'r', encoding='utf-8') as f2:
                content1 = f1.read()
                content2 = f2.read()
                
                # Compare file contents
                if not similar_content(content1, content2):
                    print(f"\nContent mismatch in {file1.name}")
                    print("\nDifferences:")
                    for line in difflib.unified_diff(
                        content1.splitlines(),
                        content2.splitlines(),
                        fromfile=str(file1),
                        tofile=str(file2)
                    ):
                        print(line)
                    raise AssertionError(f"Content mismatch in {file1.name}")

def compare_implementations(repo_url: str, config: Dict[str, Any]) -> None:
    """
    Compare the output of both implementations for a given repository.
    """
    print(f"\nRunning comparison for repository: {repo_url}")
    
    # Run PocketFlow implementation
    print("\nRunning PocketFlow implementation...")
    pocketflow_result = run_pocketflow_flow(repo_url, config)
    
    # Run our implementation
    print("\nRunning our implementation...")
    our_result = run_our_flow(repo_url, config)
    
    # Compare shared data
    print("\nComparing shared data...")
    assert pocketflow_result["project_name"] == our_result["project_name"], \
        f"Project names differ: {pocketflow_result['project_name']} vs {our_result['project_name']}"
    assert pocketflow_result["repo_url"] == our_result["repo_url"], \
        f"Repository URLs differ"
    
    # Compare abstractions
    print("\nComparing abstractions...")
    assert len(pocketflow_result["abstractions"]) == len(our_result["abstractions"]), \
        f"Number of abstractions differ: {len(pocketflow_result['abstractions'])} vs {len(our_result['abstractions'])}"
    
    for pocket_abstr, our_abstr in zip(pocketflow_result["abstractions"], our_result["abstractions"]):
        assert pocket_abstr["name"] == our_abstr["name"], \
            f"Abstraction names differ: {pocket_abstr['name']} vs {our_abstr['name']}"
        assert similar_content(pocket_abstr["description"], our_abstr["description"]), \
            f"Abstraction descriptions differ for {pocket_abstr['name']}"
    
    # Compare relationships
    print("\nComparing relationships...")
    assert len(pocketflow_result["relationships"]) == len(our_result["relationships"]), \
        f"Number of relationships differ"
    
    for pocket_rel, our_rel in zip(pocketflow_result["relationships"], our_result["relationships"]):
        assert pocket_rel["from_abstraction"] == our_rel["from_abstraction"], \
            f"From abstraction indices differ"
        assert pocket_rel["to_abstraction"] == our_rel["to_abstraction"], \
            f"To abstraction indices differ"
        assert similar_content(pocket_rel["label"], our_rel["label"]), \
            f"Relationship labels differ"
    
    # Compare chapter order
    print("\nComparing chapter order...")
    assert pocketflow_result["chapter_order"] == our_result["chapter_order"], \
        f"Chapter order differs"
    
    # Compare chapters
    print("\nComparing chapters...")
    assert len(pocketflow_result["chapters"]) == len(our_result["chapters"]), \
        f"Number of chapters differ"
    
    for pocket_chapter, our_chapter in zip(pocketflow_result["chapters"], our_result["chapters"]):
        assert similar_content(pocket_chapter, our_chapter), \
            "Chapter content differs"
    
    # Compare final output directories
    print("\nComparing output directories...")
    compare_files_in_directories(
        pocketflow_result["final_output_dir"],
        our_result["final_output_dir"]
    )
    
    print("\nAll comparisons successful!")

def main():
    # Test configuration
    config = {
        "output_dir": "output",
        "max_file_size": 1 * 1024 * 1024,  # 1MB
        "include_patterns": ["*.py", "*.ipynb"],
        "exclude_patterns": ["test*", "venv", ".git"],
        "language": "English"
    }
    
    # Test repository
    test_repo = "https://github.com/scikit-learn/scikit-learn"
    
    try:
        compare_implementations(test_repo, config)
    except AssertionError as e:
        print(f"\nComparison failed: {str(e)}")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")

if __name__ == "__main__":
    main()
