import requests
import argparse
import os
import threading

from dotenv import load_dotenv
from huggingface_hub import login
from scripts.text_inspector_tool import TextInspectorTool
from scripts.visual_qa import visualizer
from smolagents_portkey_support import PortkeyModel
from firecrawl import FirecrawlApp

from smolagents import (
    CodeAgent,
    # HfApiModel,
    LiteLLMModel,
    ToolCallingAgent,
    ManagedAgent,
    DuckDuckGoSearchTool
)

from smolagents.prompts import CODE_SYSTEM_PROMPT

from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel, tool
from litellm import completion
import os
from firecrawl import FirecrawlApp
from pydantic import BaseModel
from typing import Any, Optional, List


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
    parser.add_argument("--model-id", type=str, default="claude-3-5-sonnet-latest") #default="o3-mini")
    return parser.parse_args()


custom_role_conversions = {"tool-call": "assistant", "tool-response": "user"}

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"

BROWSER_CONFIG = {
    "viewport_size": 1024 * 5,
    "downloads_folder": "downloads_folder",
    "request_kwargs": {
        "headers": {"User-Agent": user_agent},
        "timeout": 300,
    },
    "serpapi_key": os.getenv("SERPAPI_API_KEY"),
}

os.makedirs(f"./{BROWSER_CONFIG['downloads_folder']}", exist_ok=True)

@tool
def extract_website_info(url: str) -> str:
    """A tool for extracting specific information from websites using Firecrawl.
    
    This tool uses Firecrawl to crawl websites.
    
    Args:
        url: The website URL or domain pattern (e.g., "example.com") to crawl
            
    Returns:
        str: The extracted information formatted as a string
    """
    try:
        # Initialize Firecrawl client
        app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))
        data = app.scrape_url(url=url, params={
            'formats': ['markdown'],
        })
        return str(data)
    except Exception as e:
        # Fallback to basic requests.get if Firecrawl fails
        response = requests.get(url)
        response.raise_for_status()
        return response.text

# @tool
# def ask_perplexity_tool(prompt: str) -> str:
#     """A tool for making queries to Perplexity AI's LLM through LiteLLM integration.
    
#     This tool provides an interface to query Perplexity AI's language models. The actual API
#     call is handled internally by LiteLLM, which manages the authentication, request
#     formatting, and response parsing.
    
#     Args:
#         prompt: The prompt to send to Perplexity's model.
#             Should be a clear, well-formed query in natural language.
            
#     Returns:
#         str: The model's response to the prompt. The response will be in natural language text.
    
#     """
#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "You are an artificial intelligence assistant and you need to "
#                 "engage in a helpful, detailed, polite conversation with a user."
#             ),
#         },
#         {   
#             "role": "user",
#             "content": prompt,
#         },
#     ]
    
    
#     response = completion(
#         model="perplexity/sonar-reasoning-pro",
#         messages=messages,
#         api_base="https://api.perplexity.ai",
#         api_key=os.environ["PERPLEXITY_API_KEY"]
#     )
    
#     return response.choices[0].message.content


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

    text_webbrowser_system_prompt = CODE_SYSTEM_PROMPT + """Make sure to ALWAYS:
    - Use the DuckDuckGo search tool to search for relevant web content.
    - Use the extract_website_info tool to extract information from a website.
    - Search and crawl as many relevant web pages as possible to gather comprehensive information.
    - When searching, try multiple related search queries to find different perspectives and sources.
    - For each relevant search result, make sure to extract the full webpage content.
    - Cross-reference information from multiple sources to provide complete and accurate answers.
    - Don't stop at just 1-2 sources - aim to gather information from at least 3-5 different relevant webpages.
    - Make sure to ALWAYS return source URLs in your answer!
    """
    
    text_webbrowser_agent = ToolCallingAgent(
        model=model,
        tools=[extract_website_info, DuckDuckGoSearchTool()],
        max_steps=20,
        verbosity_level=2,
        planning_interval=4,
        system_prompt=text_webbrowser_system_prompt,
    )

    manager_agent_system_prompt = CODE_SYSTEM_PROMPT + "Make sure to ALWAYS use the text_webbrowser_agent managed_agent to answer the question! Make sure to ALWAYS return source URLs in your answer!"

    managed_text_webbrowser_agent = ManagedAgent(
            agent=text_webbrowser_agent,
        name="search_agent",
        description="""A team member that will search the internet to answer your question.
        Ask him for all your questions that require browsing the web.
        Provide him as much context as possible, in particular if you need to search on a specific timeframe!
        And don't hesitate to provide him with a complex search task, like finding a difference between two webpages.
        Your request must be a real sentence, not a google search! Like "Find me this information (...)" rather than a few keywords.
        """
        )
    
    manager_agent = CodeAgent(
        model=model,
        tools=[visualizer, document_inspection_tool],
        max_steps=12,
        verbosity_level=2,
        additional_authorized_imports=AUTHORIZED_IMPORTS,
        planning_interval=4,
        managed_agents=[managed_text_webbrowser_agent],
        system_prompt=manager_agent_system_prompt
    )

    answer = manager_agent.run(args.question)
    print(f"Got this answer: {answer}")


if __name__ == "__main__":
    main()
