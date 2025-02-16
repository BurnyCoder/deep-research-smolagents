# Open Deep Research

This is edited version of Hugginface's Open Deep Research Agent https://huggingface.co/blog/open-deep-research and dzhng's Deep Research agent https://github.com/dzhng/deep-research combined into one agent.

## Environment Variables

Create a `.env` file in the root directory with the following variables. You can use the `.envtemplate` file as a reference.

```bash
HF_TOKEN=your_huggingface_token  # Required for accessing Hugging Face models and resources
SERPAPI_API_KEY=your_serpapi_key  # Enables web search functionality through SerpAPI
OPENAI_API_KEY=your_openai_key  # Required for using OpenAI language models
FIRECRAWL_API_KEY=your_firecrawl_key  # Enables web crawling and content extraction
PORTKEY_API_BASE=https://api.portkey.ai/v1  # Base URL for Portkey API service
PORTKEY_API_KEY=your_portkey_key  # Main authentication key for Portkey services
PORTKEY_VIRTUAL_KEY_GROQ=your_groq_virtual_key  # Virtual key for accessing Groq models via Portkey
PORTKEY_VIRTUAL_KEY_ANTHROPIC=your_anthropic_virtual_key  # Virtual key for accessing Anthropic models
PORTKEY_VIRTUAL_KEY_OPENAI=your_openai_virtual_key  # Virtual key for accessing OpenAI models through Portkey
PORTKEY_VIRTUAL_KEY_GOOGLE=your_google_virtual_key  # Virtual key for accessing Google AI models
OPENAI_MODEL="o3-mini"  # Specifies which OpenAI model to use by default
AGENT_TYPE="code" # Determines whether to use tool-based or code-based agent
MANAGER_AGENT_SYSTEM_PROMPT=system_prompt_here  # Defines the behavior and capabilities of the manager agent
```

## Installation

Clone the repository:
```bash
git clone https://github.com/BurnyCoder/deep-research-smolagents
cd deep-research-smolagents
```

Optionally create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
npm install
```

## Running the agent

Parameters Explained:
- `--model-id`: Specifies which AI model to use (e.g., "o3-mini", "claude-3-5-sonnet-latest")
- `--questions`: When included, enables interactive clarifying questions mode where the agent will ask questions to better understand your research query
- `--b`: Research breadth parameter (range: 3-10, default: 4)
- `--d`: Research depth parameter (range: 1-5, default: 2)

To run smolagents deep research agent with deep reserach TS agent as a tool with optional parameters:
```bash
python run_deep_research.py --questions --model-id "o3-mini" "Best practices to build AI agents" 
```
- If you don't pass query in the parameter, it will prompt you to enter a question.
- If you dont pass --question in the parameter, it will not ask clarifying questions.
- If you don't pass --model-id in the parameter, it will use o3-mini as the model.

To run deep research TS agent alone with optional parameters:
```bash
python run_deep_research_ts.py --questions --b 2 --d 2 "Best practices to build AI agents" 
```
- If you don't pass query in the parameter, it will prompt you to enter a question.
- If you dont pass --question in the parameter, it will not ask clarifying questions.
- If you don't pass --b and --d (breadth and depth) in the parameter, it will use 2 and 2 as the default values.

To run smolagents agents with serapi:
```bash
python run_serapi.py --questions --model-id "claude-3-5-sonnet-latest" "Best practices to build AI agents"
```

To run smolagents agents with firecrawl:
```bash
python run_firecrawl.py --questions--model-id "claude-3-5-sonnet-latest" "Best practices to build AI agents"
```
