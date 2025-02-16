import argparse
import os
import threading

from dotenv import load_dotenv
from scripts.text_inspector_tool import TextInspectorTool
from scripts.text_web_browser import (
    ArchiveSearchTool,
    FinderTool,
    FindNextTool,
    PageDownTool,
    PageUpTool,
    SearchInformationTool,
    SimpleTextBrowser,
    VisitTool,
)
from smolagents.prompts import CODE_SYSTEM_PROMPT
from scripts.visual_qa import visualizer

from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    ManagedAgent,
)
from scripts.smolagents_portkey_support import PortkeyModel
from scripts.portkey_api import o3minihigh

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
    parser.add_argument("--questions", action="store_true", help="Enable clarifying questions")
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
    text_limit = 100000

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
    document_inspection_tool = TextInspectorTool(model, text_limit)

    browser = SimpleTextBrowser(**BROWSER_CONFIG)

    WEB_TOOLS = [
        SearchInformationTool(browser),
        VisitTool(browser),
        PageUpTool(browser),
        PageDownTool(browser),
        FinderTool(browser),
        FindNextTool(browser),
        ArchiveSearchTool(browser),
        TextInspectorTool(model, text_limit),
    ]

    text_webbrowser_system_prompt = CODE_SYSTEM_PROMPT + """
    You are deep research agent, make the response very long and detailed with a lot of sources!
    Make sure to ALWAYS:
    - Search and crawl as many relevant web pages as possible to gather comprehensive information.
    - Search multiple related queries to find different perspectives and sources.
    - For each relevant search result, extract the full webpage content.
    - Cross-reference information from multiple sources to provide complete and accurate answers.
    - Don't stop at just 1-2 sources - aim to gather information from at least 3-5 different relevant webpages.
    - Make sure to ALWAYS return source URLs in your answer!
    """

    text_webbrowser_agent = ToolCallingAgent(
        model=model,
        tools=WEB_TOOLS,
        max_steps=20,
        verbosity_level=2,
        planning_interval=4,
        system_prompt=text_webbrowser_system_prompt,
    )

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

    manager_agent_system_prompt = CODE_SYSTEM_PROMPT + "You are deep research agent, make the response very long and detailed with a lot of sources! Make sure to ALWAYS use the text_webbrowser_agent managed_agent to answer the question! Make sure to ALWAYS return source URLs in your answer!"

    agent_type = os.getenv('AGENT_TYPE', 'tool_calling').lower()

    if agent_type == 'code':
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
    else:
        manager_agent = ToolCallingAgent(
            model=model,
            tools=[visualizer, document_inspection_tool],
            max_steps=12,
            verbosity_level=2,
            planning_interval=4,
            managed_agents=[managed_text_webbrowser_agent],
            system_prompt=manager_agent_system_prompt
        )

    answer = manager_agent.run(enhanced_query)
    print(f"Got this answer: {answer}")


if __name__ == "__main__":
    main()
