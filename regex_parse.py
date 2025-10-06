import re

# Regex parse log file
# Regex to capture timestamp, level, and message
# Example log line: [2025-10-05 19:44:02] INFO: User logged in

def parse_log_regex(file_path):
    # Regex to capture timestamp, level, and message
    # Example log line: [2025-10-05 19:44:02] INFO: User logged in
    log_pattern = re.compile(r'\[(.*?)\]\s(.*?):\s(.*)')
    parsed_logs = []

    try:
        with open(file_path, 'r') as file:
            for line in file:
                match = log_pattern.match(line)
                if match:
                    log_entry = {
                        'timestamp': match.group(1),
                        'level': match.group(2),
                        'message': match.group(3)
                    }
                    parsed_logs.append(log_entry)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")

    return parsed_logs

# --- Example Usage ---
log_content_regex = """[2025-10-05 19:44:02] INFO: User logged in
[2025-10-05 19:45:10] ERROR: Database connection failed
"""
with open('advanced_app.log', 'w') as f:
    f.write(log_content_regex)

parsed_data_regex = parse_log_regex('advanced_app.log')
for entry in parsed_data_regex:
    print(entry)
