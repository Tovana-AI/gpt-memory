# GPT Memory

This is a Python library that provides a memory management system for AI agents. It allows you to extract, store, and retrieve important and relevant personal information from user messages, which can be used to provide more contextual and personalized responses.

## Features

- Extracts relevant information from user messages using GPT-4o
- Stores the extracted information in a persistent JSON file
- Handles updates to the memory, ensuring that:
  - Duplicate information is ignored
  - New and relevant information is added
  - Existing information is updated (e.g., location changes)
- Resolves conflicts between new and existing information
- Provides a simple API to get and update user memory
- Generates a formatted memory context that can be used as input to language models

## Installation
You can install the AI Memory Infrastructure library using pip:

```bash
pip install gpt-memory
```

## Usage
Here's an example of how to use the library:

```python
from ai_memory import AIMemoryManager

# Initialize the memory manager with your OpenAI API key
memory_manager = AIMemoryManager(api_key="your-api-key-here")

# Update user memory
memory_manager.update_user_memory("user123", "I just moved from New York to Paris for work.")

# Get user memory
user_memory = memory_manager.get_user_memory("user123")
print(user_memory) >> {'location': 'Paris', 'previous_location': 'New York'}

# Get memory context for LLM
context = memory_manager.get_memory_context("user123")
print(context) >> 'User Memory:\n location: Paris,\n previous_location: New York'
```

## API Reference
The library provides the following main classes and methods:

### GPTMemoryManager
`get_memory(user_id: str) -> JSON`: Retrieves the memory for the given user.

`update_memory(user_id: str, message: str) -> JSON`: Updates the memory for the given user with the information extracted from the message. Returns an updated memory JSON.

`get_memory_context(user_id: str) -> str`: Generates a formatted memory context for the given user.

## Contributing
Contributions to GPT Memory are welcome! If you find any issues or have suggestions for improvements, please feel free to submit a pull request or open an issue on the GitHub repository.

## License
This project is licensed under the MIT License.
