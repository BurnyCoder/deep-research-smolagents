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


def main():
    args = parse_args()
    text_limit = 100000

    model = PortkeyModel(
        args.model_id,
        max_completion_tokens=8192,
        custom_role_conversions=custom_role_conversions,
        reasoning_effort="high",
    )
    document_inspection_tool = TextInspectorTool(model, text_limit)

    def research_tool(query: str, breadth: int = 4, depth: int = 2) -> Dict[str, Any]:
        """Research tool that uses TypeScript deep research implementation"""
        return research_topic(query=query, breadth=breadth, depth=depth)

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

    manager_agent = CodeAgent(
        model=model,
        tools=[research_tool],
        max_steps=12,
        verbosity_level=2,
        additional_authorized_imports=AUTHORIZED_IMPORTS,
        planning_interval=4,
        system_prompt=manager_agent_system_prompt
    )

    answer = manager_agent.run(args.question)
    print(f"Got this answer: {answer}")


if __name__ == "__main__":
    main()
