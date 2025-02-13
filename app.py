import subprocess

def main():
    # Sample question about Mercedes Sosa's albums
    sample_question = "Best AI agent building practices."
    
    # Construct the command to run run.py with the sample question
    cmd = ["python", "run.py", sample_question]
    
    # Execute the command
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except Exception as e:
        print(f"Error running script: {e}")

if __name__ == "__main__":
    main()

