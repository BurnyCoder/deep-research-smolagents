import subprocess
import os
import json
import argparse
from typing import Dict, Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def research_topic(query: str, breadth: int = 4, depth: int = 2) -> dict:
    """
    Perform deep research on a given topic.
    
    Args:
        query (str): The research query/topic
        breadth (int): Research breadth parameter (recommended: 3-10, default: 4)
        depth (int): Research depth parameter (recommended: 1-5, default: 2)
    
    Returns:
        dict: Research results containing learnings and visited URLs
        
    Raises:
        FileNotFoundError: If environment file is missing
        subprocess.CalledProcessError: If TypeScript process fails
    """
    
    # Get environment variables
    hf_token = os.getenv('HF_TOKEN')
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

    # Prepare environment variables
    env = {
        'HF_TOKEN': hf_token,
        'FIRECRAWL_KEY': firecrawl_key,
        'CONTEXT_SIZE': context_size,
        'OPENAI_MODEL': openai_model,
        'PORTKEY_API_BASE': portkey_api_base,
        'PORTKEY_API_KEY': portkey_api_key,
        'PORTKEY_VIRTUAL_KEY_GROQ': portkey_virtual_key_groq,
        'PORTKEY_VIRTUAL_KEY_ANTHROPIC': portkey_virtual_key_anthropic,
        'PORTKEY_VIRTUAL_KEY_OPENAI': portkey_virtual_key_openai,
        'PORTKEY_VIRTUAL_KEY_GOOGLE': portkey_virtual_key_google,
        'SERPAPI_API_KEY': serpapi_api_key,
        'PATH': os.environ.get('PATH', '')  # Include PATH from current environment
    }

    # Format the command arguments
    try:
        # Call tsx directly instead of using npm start
        process = subprocess.Popen(
            ['tsx', '--env-file=.env', 'src/run.ts', query, str(breadth), str(depth)],
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
            raise subprocess.CalledProcessError(return_code, ['tsx', '--env-file=.env', 'src/run.ts', query, str(breadth), str(depth)], stderr=stderr)
        
        # Join all output lines and return as a dictionary
        complete_output = '\n'.join(full_output)
        try:
            # Try to parse as JSON if the output is in JSON format
            parsed_output = json.loads(complete_output)
            print("Parsed JSON output:", parsed_output)
            
            # Print contents of output.md if it exists
            try:
                with open('output.md', 'r') as f:
                    print("\nOutput.md contents:")
                    print(f.read())
            except FileNotFoundError:
                print("\noutput.md file not found")
                
            return parsed_output
        except json.JSONDecodeError:
            # If not JSON, return as string in a dictionary
            output_dict = {"output": complete_output}
            print("String output:", output_dict)
            
            # Print contents of output.md if it exists
            try:
                with open('output.md', 'r') as f:
                    print("\nOutput.md contents:")
                    print(f.read())
            except FileNotFoundError:
                print("\noutput.md file not found")
                
            return output_dict
            
    except subprocess.CalledProcessError as e:
        print(f"Error running research: {e}")
        print(f"stderr: {e.stderr}")
        return {"error": str(e), "stderr": e.stderr}

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "question",
        type=str,
        nargs='?',
        default="What is the best AI agent building practices?",
        help="Research query/topic"
    )
    parser.add_argument("--model-id", type=str, default="o3-mini")
    parser.add_argument("--b", type=int, default=4, help="Research breadth (3-10)")
    parser.add_argument("--d", type=int, default=2, help="Research depth (1-5)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    results = research_topic(args.question, args.b, args.d)
    
    
