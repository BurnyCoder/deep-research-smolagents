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
    
    # Prepare environment variables
    env = os.environ.copy()

    # Format the command with arguments
    command = f'"{query}" {breadth} {depth}'
    
    try:
        # Call the TypeScript project and wait for complete output
        process = subprocess.Popen(
            ['npm', 'start', command],
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
            raise subprocess.CalledProcessError(return_code, ['npm', 'start', command], stderr=stderr)
        
        # Join all output lines and return as a dictionary
        complete_output = '\n'.join(full_output)
        try:
            # Try to parse as JSON if the output is in JSON format
            return json.loads(complete_output)
        except json.JSONDecodeError:
            # If not JSON, return as string in a dictionary
            return {"output": complete_output}
            
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
    print(json.dumps(results, indent=2))
