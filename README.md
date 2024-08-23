<div align="center">
<!--<h1 style="display: flex; align-items: center; gap: 10px;">
  <img src="https://github.com/user-attachments/assets/3fb24490-b5f9-4af1-b2eb-8f2f24a6e6b8" alt="Logo" width="25">
  GPT Memory
</h1>-->
<h1>🧠 GPT Memory</h1>

<h3>Memory Driven Reasoning for Smarter AI Agents</h3>

GPT Memory is a library powered by Tovana that introduces a new approach to improving LLM reasoning through actionable insights (aka beliefs) derived from continuous interactions and long term memory.

[![PyPI version](https://img.shields.io/pypi/v/tovana?logo=pypi&logoColor=white&style=flat)](https://badge.fury.io/py/tovana)
[![License: Apache 2](https://img.shields.io/badge/License-Apache-yellow.svg)](https://opensource.org/license/apache-2-0)
</div>

## Why GPT Memory?

Current LLMs face significant limitations in their ability to learn and adapt from user-specific interactions over time. While LLMs excel at processing vast amounts of data, they struggle with ongoing personalization and context-aware learning. This gap restricts their ability to provide truly adaptive and evolving AI experiences.

Our Memory manager aims to address these challenges by providing a comprehensive memory and belief management framework for AI agents. Its core concept revolves around converting experiences (events) into memories, which in turn shape beliefs. These beliefs then influence the agent's reasoning, responses, and actions.

By simulating human-like memory processes, GPT Memory enables more personalized, adaptive, and context-aware AI interactions. This framework bridges the gap between static knowledge bases and dynamic, experience-based learning, allowing AI agents to evolve their understanding and behavior over time.
## 🌟 Features

| Feature                          | Status      | Description                                                                                 |
|----------------------------------|-------------|---------------------------------------------------------------------------------------------|
| 🧠 Human-like Memory             | ✅ Available | Transform interactions into lasting memories and actionable beliefs                         |
| 🔍 Smart Information Extraction  | ✅ Available | Automatically capture and store relevant user details from conversations                    |
| 💡 Dynamic Belief Generation     | ✅ Available | Create personalized, context-aware insights to guide AI responses                           |
| 🤖 LLM-Friendly Context          | ✅ Available | Seamlessly integrate memory and beliefs into your AI's decision-making process              |
| 🔌 Easy Integration              | ✅ Available | Plug into your AI applications with a straightforward API                                   |
| 🎭 Conflict Resolution           | ✅ Available | Intelligently handle contradictions in user information                                     |
| 🌐 Flexible Architecture         | ✅ Available | Designed to work with various LLM providers and models                                      |
| 📊 Memory Management             | ✅ Available | Process events, store short-term and long-term memories, and manage beliefs                 |
| 🔗 Advanced Association Creation | ✅ Available | Form connections between memories and beliefs for more nuanced understanding                |
| 🧵 Async Functionality           | ✅ Available | Support for asynchronous operations to enhance performance in concurrent environments       |
| ⛁ Persistent Database Support    | 🔜 Coming Soon | Integration with persistent databases for long-term storage and retrieval of memory data    |
| 🎛️ Custom Belief Generation     | 🔜 Coming Soon | User-generated beliefs offering end-to-end flexibility in shaping the belief system reasoning|

## 🏗️ Architecture
<img width="663" alt="Screenshot 2024-08-21 at 9 04 07" src="https://github.com/user-attachments/assets/2bdfdaa8-e91c-45b0-b200-2e567daadc5d">



## 🚀 Quick Start

1. Install Tovana:
```bash
pip install tovana
```

2. Use it in your project:

```python
from tovana import MemoryManager

business_description = "an AI therapist"
message = "I just moved from New York to Paris for work."
user_id = "user123"

# Initialize with your preferred LLM provider and API key (Refer to the documentation for specific models)
memory_manager = MemoryManager(api_key="your-llm-provider-api-key-here", provider="anthropic",
                               business_description=business_description, include_beliefs=True)

# Update user memory
memory_manager.update_user_memory(user_id=user_id, message=message)

# Get user memory
user_memory = memory_manager.get_user_memory(user_id=user_id)
print(user_memory)  # Output: {'location': 'Paris', 'previous_location': 'New York'}

# Get memory context for LLM
context = memory_manager.get_memory_context(user_id=user_id)
print(context)  # Output: 'User Memory:\n location: Paris,\n previous_location: New York'

# Get beliefs
beliefs = memory_manager.get_beliefs(user_id=user_id)
print(beliefs)  # Output: {"beliefs": "- Suggest spending time with Charlie and Luna when user is feeling down\n- Suggest family activities with Lisa and Mai for emotional well-being\n- Recommend playing basketball for physical exercise and stress relief"}
```

## 🧠 Belief Generation

GPT memory introduces a new approach to LLM reasoning: actionable beliefs generated from user memory. These beliefs provide personalized insights that can significantly enhance your agent's planning, reasoning and responses.

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
{"beliefs": ",- Suggest mediation at 9:30pm\n- Suggest spending time with Charlie and Luna for emotional well-being"}
```

## 🛠️ API Reference

### MemoryManager

- `get_memory(user_id: str) -> JSON`: Fetch user memory
- `delete_memory(user_id: str) -> bool`: Delete user memory
- `update_memory(user_id: str, message: str) -> JSON`: Update memory with relevant information if found in message
- `batch_update_memory(user_id: str, messages: List[Dict[str, str]]) -> JSON`: Update memory with relevant information if found in message
- `get_memory_context(user_id: str, message: Optiona[str]) -> str`: Get formatted memory context, general or message specific
- `get_beliefs(user_id: str) -> str`: Get actionable beliefs context

### Batch Update Memory
Traditional per-message memory updates can be costly and inefficient, especially in longer conversations. They often miss crucial context, leading to suboptimal information retrieval. 

Our batch memory update method addresses these challenges by processing entire conversations at once. This approach not only improves performance and reduces costs but also enhances the quality of extracted information. This results in a more coherent and accurate user memory, ultimately leading to better AI reasoning.

#### Example

```python
user_id = "user123"
messages = [
    {"role": "user", "content": "Hi, I'm planning a trip to Japan."},
    {"role": "assistant", "content": "That's exciting! When are you planning to go?"},
    {"role": "user", "content": "I'm thinking about next spring. I love sushi and technology."}
]

await memory_manager.batch_update_memory(user_id, messages)
```

### Sync vs Async Updates
This library provides both synchronous and asynchronous update methods to cater to different use cases and application architectures:

1. **Asynchronous Updates (`AsyncMemoryManager`)**: Ideal for applications built on asynchronous frameworks like FastAPI or asynchronous Python scripts. This allows for non-blocking memory updates, improving overall application performance, especially when dealing with I/O-bound operations or high-concurrency scenarios.
2. **Synchronous Updates (`MemoryManager`)**: Suitable for traditional synchronous applications or when you need to ensure that memory updates are completed before proceeding with other operations. This can be useful in scripts or applications where the order of operations is critical.

By providing both options, our library offers flexibility, allowing to choose the most appropriate method based on your specific application requirements and architecture.

## 🤝 Contributing

We welcome contributions! Found a bug or have a feature idea? Open an issue or submit a pull request. Let's make Tovana even better together! 💪

## 📄 License

Tovana is Apache-2.0 licensed. See the [LICENSE](LICENSE) file for details.

---

Ready to empower your AI agents with memory-driven reasoning? Get started with GPT Memory! 🚀 If you find it useful, don't forget to star the repo! ⭐
