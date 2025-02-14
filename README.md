# Open Deep Research

This is edited fork of the huggingface Open Deep Research Agent. https://huggingface.co/blog/open-deep-research 

This agent achieves 55% pass@1 on GAIA validation set, vs 67% for OpenAI Deep Research.

## Installation

To install it, first run
```bash
pip install -r requirements.txt
```

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
```

## Running the agent

Run the agent with the following command:
```bash
python run_custom.py --model-id "claude-3-5-sonnet-latest" "Best practices to build AI agents"
```
or
```bash
python run_firecrawl.py --model-id "claude-3-5-sonnet-latest" "Best practices to build AI agents"
```

For the deep research ts agent, you need to install the deep research implementation first:
```bash
cd deep-research-ts
npm install
cd ..
```

Then you can run the smolagents deep research agent with the deep research ts agent as a tool:
```bash
python run_deep_research.py --model-id "claude-3-5-sonnet-latest" "Best practices to build AI agents"
```

Or you can run the deep research ts agent on its own with the following command:
```bash
python deep_research_ts/run.py
```