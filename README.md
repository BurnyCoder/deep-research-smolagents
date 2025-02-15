# Open Deep Research

This is edited version of Hugginface's Open Deep Research Agent https://huggingface.co/blog/open-deep-research and dzhng's Deep Research agent https://github.com/dzhng/deep-research combined into one agent.

## Environment Variables

Create a `.env` file in the root directory with the following variables. You can use the `.envtemplate` file as a reference.

```bash
HF_TOKEN=your_huggingface_token
SERPAPI_API_KEY=your_serpapi_key
OPENAI_API_KEY=your_openai_key
FIRECRAWL_API_KEY=your_firecrawl_key
PORTKEY_API_BASE=https://api.portkey.ai/v1
PORTKEY_API_KEY=your_portkey_key
PORTKEY_VIRTUAL_KEY_GROQ=your_groq_virtual_key
PORTKEY_VIRTUAL_KEY_ANTHROPIC=your_anthropic_virtual_key
PORTKEY_VIRTUAL_KEY_OPENAI=your_openai_virtual_key
PORTKEY_VIRTUAL_KEY_GOOGLE=your_google_virtual_key
OPENAI_MODEL="o3-mini"
MANAGER_AGENT_SYSTEM_PROMPT=system_prompt_here
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

To run smolagents agent with deep research ts agent:

```bash
python run_deep_research.py --model-id "o3-mini" "Best practices to build AI agents"
```

To run deep research ts agent on its own:
```bash
python run_deep_research_ts.py "Best practices to build AI agents" --model-id "o3-mini" --b 2 --d 2
```

To run smolagents agents with serapi:
```bash
python run_serapi.py --model-id "claude-3-5-sonnet-latest" "Best practices to build AI agents"
```

To run smolagents agents with firecrawl:
```bash
python run_firecrawl.py --model-id "claude-3-5-sonnet-latest" "Best practices to build AI agents"
```

