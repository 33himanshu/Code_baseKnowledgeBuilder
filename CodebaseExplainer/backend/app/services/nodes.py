import asyncio
import warnings
import copy
import time
from typing import Any, Dict, Optional
from .github_service import GitHubService
from .llm_service import LLMService
from .code_analyzer import CodeAnalyzer

class BaseNode:
    def __init__(self):
        self.params = {}
        self.successors = {}
        
    def set_params(self, params: Dict[str, Any]):
        self.params = params
        
    def next(self, node: 'BaseNode', action: str = "default") -> 'BaseNode':
        if action in self.successors:
            warnings.warn(f"Overwriting successor for action '{action}'")
        self.successors[action] = node
        return node
    
    def prep(self, shared: Dict[str, Any]) -> None:
        pass
    
    def exec(self, prep_res: Any) -> Any:
        pass
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> Any:
        pass
    
    def _exec(self, prep_res: Any) -> Any:
        return self.exec(prep_res)
    
    def _run(self, shared: Dict[str, Any]) -> Any:
        p = self.prep(shared)
        e = self._exec(p)
        return self.post(shared, p, e)
    
    def run(self, shared: Dict[str, Any]) -> Any:
        if self.successors:
            warnings.warn("Node won't run successors. Use Flow.")
        return self._run(shared)
    
    def __rshift__(self, other: 'BaseNode') -> 'BaseNode':
        return self.next(other)
    
    def __sub__(self, action: str) -> '_ConditionalTransition':
        if isinstance(action, str):
            return _ConditionalTransition(self, action)
        raise TypeError("Action must be a string")

class _ConditionalTransition:
    def __init__(self, src: BaseNode, action: str):
        self.src = src
        self.action = action
    
    def __rshift__(self, tgt: BaseNode) -> BaseNode:
        return self.src.next(tgt, self.action)

class Node(BaseNode):
    def __init__(self, max_retries: int = 1, wait: int = 0):
        super().__init__()
        self.max_retries = max_retries
        self.wait = wait
        self.cur_retry = 0
    
    def exec_fallback(self, prep_res: Any, exc: Exception) -> Any:
        raise exc
    
    def _exec(self, prep_res: Any) -> Any:
        for self.cur_retry in range(self.max_retries):
            try:
                return self.exec(prep_res)
            except Exception as e:
                if self.cur_retry == self.max_retries - 1:
                    return self.exec_fallback(prep_res, e)
                if self.wait > 0:
                    time.sleep(self.wait)

class FetchRepo(Node):
    def __init__(self):
        super().__init__(max_retries=3, wait=2)
        self.github_service = GitHubService()
    
    def exec(self, prep_res: Any) -> Dict[str, Any]:
        repo_url = self.params.get("repo_url")
        if not repo_url:
            raise ValueError("Repository URL is required")
            
        repo_data = self.github_service.fetch_repository(repo_url)
        return {
            "repo_data": repo_data,
            "files": self._filter_files(repo_data["files"]),
            "project_name": repo_data["name"]
        }
    
    def _filter_files(self, files: list) -> list:
        include_patterns = self.params.get("include_patterns", [])
        exclude_patterns = self.params.get("exclude_patterns", [])
        max_size = self.params.get("max_file_size", 100000)
        
        filtered_files = []
        for file in files:
            if file["size"] <= max_size:
                include = False
                for pattern in include_patterns:
                    if file["path"].endswith(pattern.lstrip("*")):
                        include = True
                        break
                
                exclude = False
                for pattern in exclude_patterns:
                    if file["path"].startswith(pattern.rstrip("/*")):
                        exclude = True
                        break
                
                if include and not exclude:
                    filtered_files.append(file)
        
        return filtered_files

class IdentifyAbstractions(Node):
    def __init__(self):
        super().__init__(max_retries=3, wait=2)
        self.code_analyzer = CodeAnalyzer()
    
    def exec(self, prep_res: Any) -> Dict[str, Any]:
        files = prep_res["files"]
        analysis = self.code_analyzer.analyze_files(files)
        return {
            "abstractions": analysis["abstractions"],
            "relationships": analysis["relationships"],
            "core_components": analysis["core_components"]
        }

class AnalyzeRelationships(Node):
    def __init__(self):
        super().__init__(max_retries=3, wait=2)
        self.llm_service = LLMService()
    
    def exec(self, prep_res: Any) -> Dict[str, Any]:
        abstractions = prep_res["abstractions"]
        relationships = prep_res["relationships"]
        
        prompt = f"""
        Analyze these code abstractions and their relationships:
        {abstractions}
        
        Relationships:
        {relationships}
        
        Generate a detailed analysis of how these components interact.
        Focus on:
        1. Core data flow
        2. Component dependencies
        3. Key patterns and architectural decisions
        """
        
        analysis = self.llm_service.generate(prompt)
        return {
            "relationship_analysis": analysis,
            "interaction_patterns": self._extract_patterns(analysis)
        }
    
    def _extract_patterns(self, analysis: str) -> list:
        # Implementation to extract patterns from LLM response
        return []

class OrderChapters(Node):
    def __init__(self):
        super().__init__(max_retries=3, wait=2)
        self.llm_service = LLMService()
    
    def exec(self, prep_res: Any) -> Dict[str, Any]:
        analysis = prep_res["relationship_analysis"]
        patterns = prep_res["interaction_patterns"]
        
        prompt = f"""
        Create a logical chapter order for this tutorial:
        {analysis}
        
        Key patterns:
        {patterns}
        
        Generate a chapter order that:
        1. Starts with fundamental concepts
        2. Builds on previous knowledge
        3. Maintains logical progression
        """
        
        order = self.llm_service.generate(prompt)
        return {
            "chapter_order": self._parse_order(order)
        }
    
    def _parse_order(self, order: str) -> list:
        # Implementation to parse chapter order from LLM response
        return []

class WriteChapters(Node):
    def __init__(self):
        super().__init__(max_retries=3, wait=2)
        self.llm_service = LLMService()
    
    def exec(self, prep_res: Any) -> Dict[str, Any]:
        order = prep_res["chapter_order"]
        analysis = prep_res["relationship_analysis"]
        
        prompt = f"""
{language_instruction}Write a very beginner-friendly tutorial chapter (in Markdown format) for the project `{project_name}` about the concept: "{abstraction_name}". This is Chapter {chapter_num}.

Concept Details{concept_details_note}:
- Name: {abstraction_name}
- Description:
{abstraction_description}

Complete Tutorial Structure{structure_note}:
{item["full_chapter_listing"]}

Context from previous chapters{prev_summary_note}:
{previous_chapters_summary if previous_chapters_summary else "This is the first chapter."}

Relevant Code Snippets (Code itself remains unchanged):
{file_context_str if file_context_str else "No specific code snippets provided for this abstraction."}

Instructions for the chapter (Generate content in {language.capitalize()} unless specified otherwise):
- Start with a clear heading (e.g., `# Chapter {chapter_num}: {abstraction_name}`). Use the provided concept name.

- If this is not the first chapter, begin with a brief transition from the previous chapter{instruction_lang_note}, referencing it with a proper Markdown link using its name{link_lang_note}.

- Begin with a high-level motivation explaining what problem this abstraction solves{instruction_lang_note}. Start with a central use case as a concrete example. The whole chapter should guide the reader to understand how to solve this use case. Make it very minimal and friendly to beginners.

- If the abstraction is complex, break it down into key concepts. Explain each concept one-by-one in a very beginner-friendly way{instruction_lang_note}.

- Explain how to use this abstraction to solve the use case{instruction_lang_note}. Give example inputs and outputs for code snippets (if the output isn't values, describe at a high level what will happen{instruction_lang_note}).

- Each code block should be BELOW 20 lines! If longer code blocks are needed, break them down into smaller pieces and walk through them one-by-one. Aggresively simplify the code to make it minimal. Use comments{code_comment_note} to skip non-important implementation details. Each code block should have a beginner friendly explanation right after it{instruction_lang_note}.

- Describe the internal implementation to help understand what's under the hood{instruction_lang_note}. First provide a non-code or code-light walkthrough on what happens step-by-step when the abstraction is called{instruction_lang_note}. It's recommended to use a simple sequenceDiagram with a dummy example - keep it minimal with at most 5 participants to ensure clarity. If participant name has space, use: `participant QP as Query Processing`. {mermaid_lang_note}.

- Then dive deeper into code for the internal implementation with references to files. Provide example code blocks, but make them similarly simple and beginner-friendly. Explain{instruction_lang_note}.

- IMPORTANT: When you need to refer to other core abstractions covered in other chapters, ALWAYS use proper Markdown links like this: [Chapter Title](filename.md). Use the Complete Tutorial Structure above to find the correct filename and the chapter title{link_lang_note}. Translate the surrounding text.

- Use mermaid diagrams to illustrate complex concepts (```mermaid``` format). {mermaid_lang_note}.

- Heavily use analogies and examples throughout{instruction_lang_note} to help beginners understand.

- End the chapter with a brief conclusion that summarizes what was learned{instruction_lang_note} and provides a transition to the next chapter{instruction_lang_note}. If there is a next chapter

Now, directly provide a super beginner-friendly Markdown output (DON'T need ```markdown``` tags):
"""

        chapter_content = call_llm(prompt)
        # Basic validation/cleanup
        actual_heading = f"# Chapter {chapter_num}: {abstraction_name}"
        if not chapter_content.strip().startswith(f"# Chapter {chapter_num}"):
            # Add heading if missing or incorrect, trying to preserve content
            lines = chapter_content.strip().split('\n')
            if lines and lines[0].strip().startswith("#"):
                lines[0] = actual_heading
                chapter_content = "\n".join(lines)
            else:  # Otherwise, prepend it
                chapter_content = f"{actual_heading}\n\n{chapter_content}"

        # Add the generated content to our temporary list for the next iteration's context
        self.chapters_written_so_far.append(chapter_content)

        return chapter_content

    def post(self, shared, prep_res, exec_res_list):
        # exec_res_list contains the generated Markdown for each chapter, in order
        shared["chapters"] = exec_res_list
        # Clean up the temporary instance variable
        del self.chapters_written_so_far
        print(f"Finished writing {len(exec_res_list)} chapters.")

class CombineTutorial(Node):
    def prep(self, shared):
        project_name = shared["project_name"]
        output_base_dir = shared.get("output_dir", "output")
        output_path = os.path.join(output_base_dir, project_name)
        repo_url = shared.get("repo_url")

        # Get potentially translated data
        relationships_data = shared["relationships"]
        chapter_order = shared["chapter_order"]
        abstractions = shared["abstractions"]
        chapters_content = shared["chapters"]

        # --- Generate Mermaid Diagram ---
        mermaid_lines = ["flowchart TD"]
        # Add nodes for each abstraction using potentially translated names
        for i, abstr in enumerate(abstractions):
            node_id = f"A{i}"
            # Use potentially translated name, sanitize for Mermaid ID and label
            sanitized_name = abstr['name'].replace('"', '')
            node_label = sanitized_name  # Using sanitized name only
            mermaid_lines.append(f'    {node_id}["{node_label}"]')  # Node label uses potentially translated name
        # Add edges for relationships using potentially translated labels
        for rel in relationships_data['details']:
            from_node_id = f"A{rel['from']}"
            to_node_id = f"A{rel['to']}"
            # Use potentially translated label, sanitize
            edge_label = rel['label'].replace('"', '').replace('\n', ' ')  # Basic sanitization
            max_label_len = 30
            if len(edge_label) > max_label_len:
                edge_label = edge_label[:max_label_len-3] + "..."
            mermaid_lines.append(f'    {from_node_id} -- "{edge_label}" --> {to_node_id}')  # Edge label uses potentially translated label

        mermaid_diagram = "\n".join(mermaid_lines)
        # --- End Mermaid ---

        # --- Prepare index.md content ---
        index_content = f"# Tutorial: {project_name}\n\n"
        index_content += f"{relationships_data['summary']}\n\n"  # Use the potentially translated summary directly
        # Keep fixed strings in English
        index_content += f"**Source Repository:** [{repo_url}]({repo_url})\n\n"

        # Add Mermaid diagram for relationships (diagram itself uses potentially translated names/labels)
        index_content += "```mermaid\n"
        index_content += mermaid_diagram + "\n"
        index_content += "````\n\n"

        # Keep fixed strings in English
        index_content += f"## Chapters\n\n"

        chapter_files = []
        # Generate chapter links based on the determined order, using potentially translated names
        for i, abstraction_index in enumerate(chapter_order):
            # Ensure index is valid and we have content for it
            if 0 <= abstraction_index < len(abstractions) and i < len(chapters_content):
                abstraction_name = abstractions[abstraction_index]["name"]  # Potentially translated name
                # Sanitize potentially translated name for filename
                safe_name = "".join(c if c.isalnum() else '_' for c in abstraction_name).lower()
                filename = f"{i+1:02d}_{safe_name}.md"
                index_content += f"{i+1}. [{abstraction_name}]({filename})\n"  # Use potentially translated name in link text

                # Add attribution to chapter content (using English fixed string)
                chapter_content = chapters_content[i]  # Potentially translated content
                if not chapter_content.endswith("\n\n"):
                    chapter_content += "\n\n"
                # Keep fixed strings in English
                chapter_content += f"---\n\nGenerated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)"

                # Store filename and corresponding content
                chapter_files.append({"filename": filename, "content": chapter_content})
            else:
                 print(f"Warning: Mismatch between chapter order, abstractions, or content at index {i} (abstraction index {abstraction_index}). Skipping file generation for this entry.")

        # Add attribution to index content (using English fixed string)
        index_content += f"\n\n---\n\nGenerated by [AI Codebase Knowledge Builder](https://github.com/The-Pocket/Tutorial-Codebase-Knowledge)"

        return {
            "output_path": output_path,
            "index_content": index_content,
            "chapter_files": chapter_files  # List of {"filename": str, "content": str}
        }

    def exec(self, prep_res):
        output_path = prep_res["output_path"]
        index_content = prep_res["index_content"]
        chapter_files = prep_res["chapter_files"]

        print(f"Combining tutorial into directory: {output_path}")
        # Rely on Node's built-in retry/fallback
        os.makedirs(output_path, exist_ok=True)

        # Write index.md
        index_filepath = os.path.join(output_path, "index.md")
        with open(index_filepath, "w", encoding="utf-8") as f:
            f.write(index_content)
        print(f"  - Wrote {index_filepath}")

        # Write chapter files
        for chapter_info in chapter_files:
            chapter_filepath = os.path.join(output_path, chapter_info["filename"])
            with open(chapter_filepath, "w", encoding="utf-8") as f:
                f.write(chapter_info["content"])
            print(f"  - Wrote {chapter_filepath}")

        return output_path  # Return the final path

    def post(self, shared, prep_res, exec_res):
        shared["final_output_dir"] = exec_res  # Store the output path
        print(f"\nTutorial generation complete! Files are in: {exec_res}")

class CombineTutorial(Node):
    def __init__(self):
        super().__init__()
    
    def exec(self, prep_res: Any) -> Dict[str, Any]:
        chapters = prep_res["chapters"]
        project_name = self.params.get("project_name")
        
        tutorial = {
            "title": f"{project_name} Tutorial",
            "chapters": chapters,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "language": self.params.get("language", "english")
        }
        
        return tutorial
