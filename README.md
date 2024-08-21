# 🧠 GPT Memory

> Memory-Driven Reasoning for Smarter AI Agents

GPT Memory is a Python library that introduces a new approach to improving LLM reasoning through actionable insights (beliefs) learned over time from memory. Supercharge your AI agents with personalized, context-aware responses.

[![PyPI version](https://badge.fury.io/py/gpt-memory.svg)](https://badge.fury.io/py/gpt-memory)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

- Memory Management
  - `update_user_memory()`: Extract and store relevant information from user messages
  - `get_user_memory()`: Retrieve stored memory for a specific user
  - `get_memory_context()`: Generate formatted memory context for LLM input
- Belief Generation
  - `get_beliefs()`: Create actionable insights based on user memory and business context
  - Beliefs are AI-generated suggestions that help guide LLM responses, improving personalization and relevance
- Smart Data Handling
  - Automatic deduplication of information
  - Intelligent updating of existing data (e.g., location changes)
  - Conflict resolution between new and existing information
- Simple API
  - Easy-to-use methods for integrating memory and belief functionality into your AI applications
- Persistent Storage
  - Automatic saving and loading of user memory in JSON format

## 🏗️ Architecture

![GPT Memory Architecture](https://github.com/user-attachments/assets/b3c8d15b-4cb3-4367-9a6f-082b97537e04)

## 🚀 Quick Start

1. Install GPT Memory:
```bash
pip install gpt-memory
```

2. Use it in your project:
```python
from ai_memory import AIMemoryManager

# Initialize with your OpenAI API key
memory_manager = AIMemoryManager(api_key="your-api-key-here", generate_beliefs=True, business_description="an AI therapist")

# Update user memory
memory_manager.update_user_memory("user123", "I just moved from New York to Paris for work.")

# Get user memory
user_memory = memory_manager.get_user_memory("user123")
print(user_memory)  # Output: {'location': 'Paris', 'previous_location': 'New York'}

# Get memory context for LLM
context = memory_manager.get_memory_context("user123")
print(context)  # Output: 'User Memory:\n location: Paris,\n previous_location: New York'

# Get beliefs
beliefs = memory_manager.get_beliefs("user123")
print(beliefs)  # Output: {"beliefs": "- Suggest spending time with Charlie and Luna when user is feeling down\n- Suggest family activities with Lisa and Mai for emotional well-being\n- Recommend playing basketball for physical exercise and stress relief"}
```

## 🧠 Belief Generation: The Secret Sauce

GPT Memory introduces a new approach to LLM reasoning: actionable beliefs generated from user memory. These beliefs provide personalized insights that can significantly enhance your agent's planning, reasoning and responses.

### Examples
#### Input:
- `business_description`: "a commerce site"
- `memory`: {'pets': ['dog named charlie', 'horse named luna']}
#### Output:

```json
{"beliefs": ",- suggest pet products for dogs and horses"}
```

#### Input:

- `business_description`: "an AI therapist"
- `memory`: {'pets': ['dog named charlie', 'horse named luna', 'sleep_time: 10pm']}
#### Output:

```json
{"beliefs": ",- Suggest mediation at 9:30\n- Suggest spending time with Charlie and Luna when user is sad"}
```

## 🛠️ API Reference

### AIMemoryManager

- `get_memory(user_id: str) -> JSON`: Fetch user memory
- `update_memory(user_id: str, message: str) -> JSON`: Update memory with relevant information if found in message
- `get_memory_context(user_id: str) -> str`: Get formatted memory context
- `get_beliefs(user_id: str) -> str`: Get actionable beliefs context

## 🤝 Contributing

We welcome contributions! Found a bug or have a feature idea? Open an issue or submit a pull request. Let's make GPT Memory even better together! 💪

## 📄 License

GPT Memory is MIT licensed. See the [LICENSE](LICENSE) file for details.

---

Ready to empower your AI agents with memory-driven reasoning? Get started with GPT Memory! 🚀 If you find it useful, don't forget to star the repo! ⭐