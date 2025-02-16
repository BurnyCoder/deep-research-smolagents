import subprocess
import json
import argparse
import os
import threading
from typing import Dict, Any

from dotenv import load_dotenv
from huggingface_hub import login
from smolagents.prompts import CODE_SYSTEM_PROMPT
from smolagents import (
    CodeAgent,
    tool,
    ToolCallingAgent
)
from smolagents_portkey_support import PortkeyModel
from portkey_api import o3minihigh
from run_deep_research_ts import research_topic
# Get environment variables
firecrawl_key = os.getenv('FIRECRAWL_KEY')
context_size = os.getenv('CONTEXT_SIZE')
openai_model = os.getenv('OPENAI_MODEL')
portkey_api_base = os.getenv('PORTKEY_API_BASE')
portkey_api_key = os.getenv('PORTKEY_API_KEY')
portkey_virtual_key_groq = os.getenv('PORTKEY_VIRTUAL_KEY_GROQ')
portkey_virtual_key_anthropic = os.getenv('PORTKEY_VIRTUAL_KEY_ANTHROPIC')
portkey_virtual_key_openai = os.getenv('PORTKEY_VIRTUAL_KEY_OPENAI')
portkey_virtual_key_google = os.getenv('PORTKEY_VIRTUAL_KEY_GOOGLE')
serpapi_api_key = os.getenv('SERPAPI_API_KEY')

AUTHORIZED_IMPORTS = [
    "requests",
    "zipfile",
    "os",
    "numpy",
    "json",
    "bs4",
    "pubchempy",
    "xml",
    "yahoo_finance",
    "Bio",
    "pydub",
    "io",
    "PIL",
    "chess",
    "PyPDF2",
    "pptx",
    "datetime",
    "fractions",
    "csv",
]
load_dotenv(override=True)

append_answer_lock = threading.Lock()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "question",
        type=str,
        nargs='?',
        default=None,
        help="Research query/topic"
    )
    parser.add_argument("--model-id", type=str, default="o3-mini")
    parser.add_argument("--b", type=int, default=2, help="Research breadth (3-10)")
    parser.add_argument("--d", type=int, default=2, help="Research depth (1-5)")
    parser.add_argument("--questions", action="store_true", help="Enable clarifying questions")
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

@tool
def research_tool(query: str) -> str:
    """
    Perform deep research on a given topic.
    
    Args:
        query: The research query/topic
    
    Returns:
        dict: Research results containing learnings and visited URLs
        
    Raises:
        FileNotFoundError: If environment file is missing
        subprocess.CalledProcessError: If TypeScript process fails
    """
    breadth = 2
    depth = 2
    return research_topic(query, breadth, depth)

def ask_clarifying_questions(query: str) -> list:
    """
    Generates clarifying questions for the given research query using the model.
    
    Args:
        query (str): The research query/topic
        
    Returns:
        list: A list of clarifying questions
    """
    clarifying_prompt = f"""
Given this research query, what clarifying questions would you ask to better understand the requirements?
Please respond with a JSON array containing 3 key questions that would help clarify any ambiguities.
Format the response as: ["question 1", "question 2", "question 3"]

Query:
{query}
"""
    
    questions_json = o3minihigh(clarifying_prompt)
    import json
    questions = json.loads(questions_json)
    return questions

def main():
    args = parse_args()

    # Prompt user for research query
    if not args.question:
        query = input("\nEnter your research query: ").strip()
    else:
        query = args.question
        print(f"Using query: {query}")

    enhanced_query = query
    if args.questions:
        # First, get clarifying questions
        print("\nGenerating clarifying questions...\n")
        questions = ask_clarifying_questions(query)
        
        # Ask user to answer each question
        enhanced_query = query + "\n\nAdditional context from clarifying questions:"
        for i, question in enumerate(questions, 1):
            print(f"\n{i}. {question}")
            answer = input(f"\nYour answer to question {i}: ").strip()
            enhanced_query += f"\nQ: {question}\nA: {answer}"
        
        print("\nEnhanced query with clarifying answers:", enhanced_query)
    
    model = PortkeyModel(
        args.model_id,
        max_completion_tokens=8192,
        custom_role_conversions=custom_role_conversions,
        reasoning_effort="high",
    )
    manager_agent_system_prompt = os.getenv('MANAGER_AGENT_SYSTEM_PROMPT', """
    You are deep research agent. You are given a question and you need to generate a detailed answer with a lot of sources.
    You have to to:
    - Use the research_tool to perform deep research on topics!
    - For general, broad questions: provide comprehensive overview answers that cover multiple aspects and perspectives of the topic with extensive sources
    - For specific, concrete questions: provide focused, precise answers that directly address the exact question with relevant sources
    - Search multiple related queries to find different perspectives and sources!
    - Cross-reference information from multiple sources to provide complete and accurate answers!
    - Don't stop at just 1-2 reseach_tool calls - aim to call it as many times as needed, minimum 2 times! In one code block you can call the research_tool as many times as needed, minimum 2 times!
    - Make sure to ALWAYS return source URLs in your answer!
    - Retain and include all relevant information provided by the tool in your answer!
    """)
        
    #print(manager_agent_system_prompt)
    
    manager_agent_system_prompt = CODE_SYSTEM_PROMPT + manager_agent_system_prompt
    
    agent_type = os.getenv('AGENT_TYPE', 'tool_calling').lower()

    if agent_type == 'code':
        manager_agent = CodeAgent(
            model=model,
            tools=[research_tool],
            max_steps=12,
            verbosity_level=2,
            planning_interval=4,
            system_prompt=manager_agent_system_prompt,
            additional_authorized_imports=AUTHORIZED_IMPORTS
        )
    else:
        manager_agent = ToolCallingAgent(
            model=model,
            tools=[research_tool],
            max_steps=12,
            verbosity_level=2,
            planning_interval=4,
            system_prompt=manager_agent_system_prompt
        )

    answer = manager_agent.run(enhanced_query)
    print(f"Got this answer: {answer}")


if __name__ == "__main__":
    main()
