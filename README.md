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
memory_manager = AIMemoryManager(api_key="your-api-key-here", generate_beliefs=True, business_description="an AI therapist")

# Update user memory
memory_manager.update_user_memory("user123", "I just moved from New York to Paris for work.")

# Get user memory
user_memory = memory_manager.get_user_memory("user123")
print(user_memory) -> {'location': 'Paris', 'previous_location': 'New York'}

# Get memory context for LLM
context = memory_manager.get_memory_context("user123")
print(context) -> 'User Memory:\n location: Paris,\n previous_location: New York'

# Get beliefs
beliefs = memory_manager.get_beliefs("user123")
print(beliefs) -> {"beliefs": "- Suggest spending time with Charlie and Luna when user is feeling down\n- Suggest family activities with Lisa and Mai for emotional well-being\n- Recommend playing basketball for physical exercise and stress relief"}
```

## API Reference
The library provides the following main classes and methods:

### GPTMemoryManager
`get_memory(user_id: str) -> JSON`: Retrieves the memory for the given user.

`update_memory(user_id: str, message: str) -> JSON`: Updates the memory for the given user with the information extracted from the message. Returns an updated memory JSON.

`get_memory_context(user_id: str) -> str`: Generates a formatted memory context for the given user.

`get_beliefs(user_id: str) -> str`: Gets actionable beliefs based on the user's memory and business description.

## Belief Generation
Introducing beliefs - a new approach for improving LLM reasoning by providing actionable insights learned over time from memory.

The belief method generates actionable beliefs based on the user's memory and the business description. The beliefs are generated as a string that can be used as input to LLMs to generate personalized responses.

### Examples
#### Input:
- business_description: "a commerce site"
- memories: {'pets': ['dog named charlie', 'horse named luna']}
- belief_context: None
#### Output:

```json
{"beliefs": ",- suggest pet products for dogs and horses"}
```

#### Input:

- business_description: "an AI therapist"
- memories: {'pets': ['dog named charlie', 'horse named luna', 'sleep_time: 10pm']}
- belief_context: "Suggest mediation at 9:30"
#### Output:

```json
{"beliefs": ",- Suggest mediation at 9:30\n- Suggest spending time with Charlie and Luna when user is sad"}
```

## Contributing
Contributions to GPT Memory are welcome! If you find any issues or have suggestions for improvements, please feel free to submit a pull request or open an issue on the GitHub repository.

## License
This project is licensed under the MIT License.
