def research_topic(query: str, breadth: int = 4, depth: int = 2, env_file: str = ".env.local") -> dict:
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
    import subprocess
    import os
    
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"Environment file {env_file} not found")

    # Prepare environment variables
    env = os.environ.copy()
    
    # Read environment file
    with open(env_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                env[key] = value.strip('"').strip("'")

    # Format the command with arguments
    command = f'"{query}" {breadth} {depth}'
    
    try:
        # Call the TypeScript project
        result = subprocess.run(
            ['npm', 'start', command],
            capture_output=True,
            env=env,
            check=True,
            text=True
        )
        
        # Return raw output
        return result.stdout
        
    except subprocess.CalledProcessError as e:
        print(f"Error running research: {e}")
        print(f"stderr: {e.stderr}")
        return e.stdout

# Example usage:
if __name__ == "__main__":
    try:
        results = research_topic(
            query="Best practices for Ai tool calling?",
            breadth=2,
            depth=2
        )
        print("Research Results:", results)
    except Exception as e:
        print(f"Research failed: {e}")
