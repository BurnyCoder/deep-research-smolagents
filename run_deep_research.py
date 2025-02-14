import subprocess
import json
import argparse
import os
import threading
from typing import Dict, Any

from dotenv import load_dotenv
from huggingface_hub import login
from scripts.text_inspector_tool import TextInspectorTool
from scripts.visual_qa import visualizer
from smolagents.prompts import CODE_SYSTEM_PROMPT
from smolagents import (
    CodeAgent,
    # HfApiModel,
    LiteLLMModel,
    ToolCallingAgent,
    ManagedAgent,
    tool,
    Tool
)
from smolagents_portkey_support import PortkeyModel
from run_deep_research_ts import research_topic

AUTHORIZED_IMPORTS = [
    "requests",
    "zipfile",
    "os",
    "pandas", 
    "numpy",
    "sympy",
    "json",
    "bs4",
    "pubchempy",
    "xml",
    "yahoo_finance",
    "Bio",
    "sklearn",
    "scipy",
    "pydub",
    "io",
    "PIL",
    "chess",
    "PyPDF2",
    "pptx",
    "torch",
    "datetime",
    "fractions",
    "csv",
]
load_dotenv(override=True)
login(os.getenv("HF_TOKEN"))

append_answer_lock = threading.Lock()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "question",
        type=str,
        nargs='?',
        default="What is the best AI agent building practices?",
        help="for example: 'How many studio albums did Mercedes Sosa release before 2007?'"
    )
    parser.add_argument("--model-id", type=str, default="claude-3-5-sonnet-latest")
    return parser.parse_args()


custom_role_conversions = {"tool-call": "assistant", "tool-response": "user"}

# @tool
# def extract_website_info(url: str) -> str:
#     """A tool for extracting specific information from websites using Firecrawl.
    
#     This tool uses Firecrawl to crawl websites.
    
#     Args:
#         url: The website URL or domain pattern (e.g., "example.com") to crawl
            
#     Returns:
#         str: The extracted information formatted as a string
#     """
#     return "This is a test"

class ResearchTool(Tool):
    name = "research_tool"
    description = "Perform deep research on a given topic by searching and analyzing multiple web sources."
    inputs = {
        "query": {
            "type": "string",
            "description": "The research query or topic to investigate"
        },
        "breadth": {
            "type": "integer",
            "description": "Number of parallel search paths to explore (2-5 recommended)"
        },
        "depth": {
            "type": "integer",
            "description": "How deep to follow each search path (2-5 recommended)"
        }
    }
    output_type = "object"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.process = None
        self.output_buffer = []

    def forward(self, query: str, breadth: int, depth: int) -> Dict[str, Any]:
        breadth = 2
        depth = 2
        # Prepare environment variables
        env = os.environ.copy()

        # Format the command with arguments
        command = f'"{query}" {breadth} {depth}'
        
        try:
            # Call the TypeScript project and wait for complete output
            process = subprocess.Popen(
                ['npm', 'start', command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Collect all output
            full_output = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    full_output.append(output.strip())
                    print(output.strip())  # Optional: Print output in real-time
            
            # Wait for the process to complete and get return code
            return_code = process.wait()
            
            if return_code != 0:
                stderr = process.stderr.read()
                raise subprocess.CalledProcessError(return_code, ['npm', 'start', command], stderr=stderr)
            
            # Join all output lines and return as a dictionary
            complete_output = '\n'.join(full_output)
            try:
                # Try to parse as JSON if the output is in JSON format
                return json.loads(complete_output)
            except json.JSONDecodeError:
                # If not JSON, return as string in a dictionary
                return {"output": complete_output}
                
        except subprocess.CalledProcessError as e:
            print(f"Error running research: {e}")
            print(f"stderr: {e.stderr}")
            return {"error": str(e), "stderr": e.stderr}

def main():
    args = parse_args()
    text_limit = 100000

    model = PortkeyModel(
        args.model_id,
        max_completion_tokens=8192,
        custom_role_conversions=custom_role_conversions,
        reasoning_effort="high",
    )

    manager_agent_system_prompt = CODE_SYSTEM_PROMPT + """
    You are deep research agent. You are given a question and you need to generate a detailed answer with a lot of sources.
    You have to to:
    - Use the research_tool to perform deep research on topics!
    - Make the response very long and detailed with a lot of sources!
    - Search multiple related queries to find different perspectives and sources!
    - Cross-reference information from multiple sources to provide complete and accurate answers!
    - Don't stop at just 1-2 sources - aim to gather information from at least 3-5 different relevant webpages!
    - Make sure to ALWAYS return source URLs in your answer!
    """

    # Initialize the research tool
    research_tool = ResearchTool()

    manager_agent = ToolCallingAgent(
        model=model,
        tools=[research_tool],
        max_steps=12,
        verbosity_level=2,
        planning_interval=4,
        system_prompt=manager_agent_system_prompt
    )

    answer = manager_agent.run(args.question)
    print(f"Got this answer: {answer}")


if __name__ == "__main__":
    main()
