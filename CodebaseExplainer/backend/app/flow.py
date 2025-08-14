from typing import Dict, Any, Callable, Optional, List
from .services.nodes import BaseNode

class Flow:
    def __init__(self, start: BaseNode):
        """Initialize the flow with a starting node."""
        self.start = start
        self.current_node = start
        self.shared_data = {}
        self.history = []
        
    def run(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the flow from start to finish."""
        if params:
            self.shared_data.update(params)
            
        current = self.start
        result = None
        
        while current:
            # Store current node in history
            self.history.append(current)
            
            # Prepare node
            current.prep(self.shared_data)
            
            # Execute node
            prep_result = current._run(self.shared_data)
            
            # Get next node based on result
            next_node = None
            for action, node in current.successors.items():
                if callable(action):
                    if action(prep_result):
                        next_node = node
                        break
                else:
                    next_node = node
                    break
            
            # Update result
            result = prep_result
            
            # Move to next node
            current = next_node
            
        return result

    def reset(self):
        """Reset the flow to its initial state."""
        self.current_node = self.start
        self.shared_data = {}
        self.history = []

def create_tutorial_flow():
    """Creates and returns the codebase tutorial generation flow."""
    from .services.nodes import (
        FetchRepo,
        IdentifyAbstractions,
        AnalyzeRelationships,
        OrderChapters,
        WriteChapters,
        CombineTutorial
    )

    # Instantiate nodes with retry settings
    fetch_repo = FetchRepo()
    identify_abstractions = IdentifyAbstractions(max_retries=5, wait=20)
    analyze_relationships = AnalyzeRelationships(max_retries=5, wait=20)
    order_chapters = OrderChapters(max_retries=5, wait=20)
    write_chapters = WriteChapters(max_retries=5, wait=20)
    combine_tutorial = CombineTutorial()

    # Connect nodes in sequence
    fetch_repo >> identify_abstractions
    identify_abstractions >> analyze_relationships
    analyze_relationships >> order_chapters
    order_chapters >> write_chapters
    write_chapters >> combine_tutorial

    # Create the flow
    tutorial_flow = Flow(start=fetch_repo)
    
    return tutorial_flow

if __name__ == "__main__":
    # Example usage
    flow = create_tutorial_flow()
    
    try:
        # Run the flow with parameters
        result = flow.run({
            "repo_url": "https://github.com/pydantic/pydantic",
            "language": "english",
            "include_patterns": ["*.py", "*.md"],
            "exclude_patterns": ["*test*.py", "*tests/*"],
            "max_file_size": 1 * 1024 * 1024  # 1 MB
        })
        
        print("\nTutorial generation complete!")
        print(f"Generated tutorial: {result['title']}")
        print(f"Number of chapters: {len(result['chapters'])}")
        
    except Exception as e:
        print(f"Error running flow: {str(e)}")
    
    finally:
        # Reset the flow
        flow.reset()
