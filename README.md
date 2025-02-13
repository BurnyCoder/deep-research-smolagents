# Open Deep Research

Edited huggingface https://huggingface.co/blog/open-deep-research .

This agent achieves 55% pass@1 on GAIA validation set, vs 67% for OpenAI Deep Research.

To install it, first run
```bash
pip install -r requirements.txt
```

Then you're good to go! Run the run.py script, as in:
```bash
python run_custom.py --model-id "claude-3-5-sonnet-latest" "Best practices to build AI agents"
```
or
```bash
python run_firecrawl.py --model-id "claude-3-5-sonnet-latest" "Best practices to build AI agents"
```
