import json
def process_file_1(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    new_lines = []
    for line in lines:
        line = line.strip()
        if not line.startswith('{"conversations"'):
            new_lines[-1] = new_lines[-1] +'\\n'+ line
        else:
            new_lines.append(line)

    with open(filepath, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)
def process_file_2(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    new_lines = []
    for line in lines:
        line =line.replace('"assistant":"', '"assistant","content":"')
        parts = line.split('{"conversations"', 1)
        if len(parts) > 1:
            subparts = parts[1].split('{"conversations"')
            if len(subparts) > 1:
                new_line = parts[0] + '{"conversations"' + '\n{"conversations"'.join(subparts)
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(filepath, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)


def first_15_words(text):
    """Return the first 15 words of a given text."""
    return ' '.join(text.split()[:20])

def strip_whitespace(obj):
    if isinstance(obj, dict):
        return {k.strip(): strip_whitespace(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [strip_whitespace(elem) for elem in obj]
    elif isinstance(obj, str):
        return obj.strip()
    else:
        return obj
    
def load_lines_from_file(file_path):
    """Load lines from a file and parse them as JSON objects."""
    conversations = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                line_injson = json.loads(line)
                cleaned_json = strip_whitespace(line_injson)
                conversations.append(cleaned_json)
            except json.JSONDecodeError as e:
                # Display specific error location and surrounding characters
                error_position = e.pos
                context_size = 20  # Number of characters to display before and after the error
                start = max(0, error_position - context_size)
                end = min(len(line), error_position + context_size)
                error_context = line[start:end]
                print(f"Skipping line due to JSONDecodeError at position {error_position}: {error_context}")
    return conversations

def validate_conversation(conv):
    """Validate the structure and content of a conversation."""
    try:
        conversations = conv["conversations"]
        conversations = conv["conversations"]
        for i in range(len(conversations)):
            if i % 2 == 0 and conversations[i]["role"] != "user":
                raise ValueError("Expected 'user' role at position {}".format(i))
            if i % 2 == 1 and conversations[i]["role"] != "assistant":
                raise ValueError("Expected 'assistant' role at position {}".format(i))
            human = conversations[i]["content"].strip()
        return True
    except (KeyError, ValueError, IndexError) as e:
        print(f"Skipping conversation due to validation error: {e} at {conv['conversations']}")
        return False
    
def remove_duplicates(conversations):
    """Remove duplicates based on the first 15 words of the user content."""
    seen = set()
    unique_conversations = []
    for conv in conversations:
        try:
            # Validate 'system'
            system = conv["system"].strip()
            if not system:
                raise ValueError("The 'system' field is empty or missing.")

            # Validate 'conversations'
            conversations = conv["conversations"]
            if not isinstance(conversations, list) or len(conversations) == 0:
                raise ValueError("The 'conversations' field is not a non-empty list.")
            user_content = conv['conversations'][0]['content']
            key = first_15_words(user_content)
            if key not in seen:
                seen.add(key)
                unique_conversations.append(conv)
        except Exception as e:
            print(f'error: {e}')
            continue
    return unique_conversations

def write_lines_to_file(file_path, conversations):
    """Write JSON objects back to the file, each on a new line."""
    with open(file_path, 'w', encoding='utf-8') as file:
        for conv in conversations:
            file.write(json.dumps(conv) + '\n')

def main(file_path):
    conversations = load_lines_from_file(file_path)
    unique_conversations = remove_duplicates(conversations)
    valid_conversations = [conv for conv in unique_conversations if validate_conversation(conv)]
    new_path = r'0609-4.txt'
    write_lines_to_file(new_path, valid_conversations)

if __name__ == "__main__":
    file_path = r'0609.txt'

    process_file_1(file_path)
    process_file_2(file_path)
    main(file_path)