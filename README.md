<div align="center">
<h1 style="display: flex; align-items: center; gap: 10px;">
  <img src="https://github.com/user-attachments/assets/3fb24490-b5f9-4af1-b2eb-8f2f24a6e6b8" alt="Logo" width="25">
  Tovana
</h1>

<h3>Memory Driven Reasoning for Smarter AI Agents</h3>

Tovana is a library that introduces a new approach to improving LLM reasoning through actionable insights (beliefs) derived from continous interactions and long term memory. Supercharge your AI agents with personalized, context-aware responses.

[![PyPI version](https://badge.fury.io/py/gpt-memory.svg)](https://badge.fury.io/py/gptmem)
[![License: Apache 2](https://img.shields.io/badge/License-Apache-yellow.svg)](https://opensource.org/license/apache-2-0)
</div>

## Why Tovana?
Current AI memory systems face significant drawbacks that limit their ability to mimic human-like intelligence. These include their static nature (vector dbs / semantic search), lack of contextual understanding, inability to learn from experience or form beliefs, poor handling of contradictions, limited associative capabilities, and absence of emotional intelligence. Additionally, AI agents struggle with abstraction, lack meta-cognitive abilities, and don't have mechanisms for selectively retaining or forgetting information. These shortcomings collectively restrict AI agents' adaptability, decision-making, and ability to navigate complex, real-world scenarios effectively.

The proposed AI agent memory system is designed to augment human memory and enhance AI agents' capabilities. Its purpose is to create more personalized, adaptive, and context-aware AI interactions by simulating human-like memory processes. This system aims to bridge the gap between static knowledge bases and dynamic, experience-based learning, allowing AI agents to evolve their understanding and behavior over time.

The system is a comprehensive memory and belief management framework for AI agents. It includes components for processing events, storing short-term and long-term memories, managing beliefs, creating associations, and informing decision-making processes. **The core concept revolves around converting experiences (events) into memories, which in turn shape beliefs.** These beliefs then influence the agent's reasoning, responses, and actions.

## 🌟 Features
- 🧠 Supercharge AI with Human like Memory: Transform interactions into lasting memories and beliefs
- 🔍 Smart Information Extraction: Automatically capture and store relevant user details
- 💡 Belief Generation: Create actionable insights to guide personalized AI responses
- 🤖 LLM Friendly Context Generation: Easily integrate memory and beliefs into your AI's decision-making
- 🔌 Simple Integration: Plug into your AI applications with our straightforward API
- 🎭 Conflict Resolution: Smartly handle contradictions in user information
- 🌐 Adaptable Architecture: Designed to work with various LLM providers and models

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

# Initialize with your preferred LLM provider and API key (Refer to the documentation for specific models)
memory_manager = MemoryManager(api_key="your-llm-provider-api-key-here", provider="anthropic",
                               business_description=business_description, include_beliefs=True)

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
print(
  beliefs)  # Output: {"beliefs": "- Suggest spending time with Charlie and Luna when user is feeling down\n- Suggest family activities with Lisa and Mai for emotional well-being\n- Recommend playing basketball for physical exercise and stress relief"}
```

## 🧠 Belief Generation: The Secret Sauce

Tovana introduces a new approach to LLM reasoning: actionable beliefs generated from user memory. These beliefs provide personalized insights that can significantly enhance your agent's planning, reasoning and responses.

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

### AIMemoryManager

- `get_memory(user_id: str) -> JSON`: Fetch user memory
- `update_memory(user_id: str, message: str) -> JSON`: Update memory with relevant information if found in message
- `get_memory_context(user_id: str, message: Optiona[str]) -> str`: Get formatted memory context, general or message specific
- `get_beliefs(user_id: str) -> str`: Get actionable beliefs context

## 🤝 Contributing

We welcome contributions! Found a bug or have a feature idea? Open an issue or submit a pull request. Let's make Tovana even better together! 💪

## 📄 License

Tovana is Apache-2.0 licensed. See the [LICENSE](LICENSE) file for details.

---

Ready to empower your AI agents with memory-driven reasoning? Get started with Tovana! 🚀 If you find it useful, don't forget to star the repo! ⭐
