def parse_log(file_path):
    """
    Parses a simple log file.

    Args:
        file_path (str): The path to the log file.

    Returns:
        list: A list of dictionaries, where each dictionary
              represents a parsed log entry.
    """
    parsed_logs = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Skip empty lines
                if not line.strip():
                    continue

                parts = line.split(':', 1) # Split only on the first colon
                if len(parts) == 2:
                    log_entry = {
                        'level': parts[0].strip(),
                        'message': parts[1].strip()
                    }
                    parsed_logs.append(log_entry)
                else:
                    # Handle lines that don't match the expected format
                    parsed_logs.append({'level': 'UNKNOWN', 'message': line.strip()})
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return parsed_logs

# --- Example Usage ---

# 1. Create a dummy log file named 'app.log'
log_content = """INFO: User logged in successfully
WARNING: Disk space is running low
ERROR: Failed to connect to database
INFO: Data processed
DEBUG: Variable x = 10
"""
with open('app.log', 'w') as f:
    f.write(log_content)

# 2. Parse the log file
log_file = 'app.log'
parsed_data = parse_log(log_file)

# 3. Print the parsed data
for entry in parsed_data:
    print(entry)

# Example: Count entries by log level
error_count = sum(1 for entry in parsed_data if entry['level'] == 'ERROR')
print(f"\nTotal ERROR entries: {error_count}")
