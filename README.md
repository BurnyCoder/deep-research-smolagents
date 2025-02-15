# Open Deep Research

This is edited fork of the huggingface Open Deep Research Agent. https://huggingface.co/blog/open-deep-research 

This agent achieves 55% pass@1 on GAIA validation set, vs 67% for OpenAI Deep Research.

## Environment Variables

Create a `.env` file in the root directory with the following variables, using the ones from the .envtemplate file.
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
```

## Installation

```bash
pip install -r requirements.txt
npm install
```

## Running the agent

To run smolagents agent with deep research ts agent:

```bash
python run_deep_research.py --model-id "o3-mini" "Best practices to build AI agents"
```

To run deep research ts agent on its own with the following command:
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

