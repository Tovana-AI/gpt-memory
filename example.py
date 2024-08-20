from memory import GPTMemoryManager
import os

# Initialize the memory manager with your OpenAI API key
memory_manager = GPTMemoryManager(api_key=os.environ["OPENAI_API_KEY"])

# Update user memory
memory_manager.update_memory("user123", "We also have a pet dog named Charlie")
memory_manager.update_memory("user123", "We also have a pet horse named Luna")
memory_manager.update_memory("user123", "We live in New York City")
memory_manager.update_memory("user123", "I have young girl named Lisa and married to my wife Mai")
memory_manager.update_memory("user123", "I love playing basketball and trading cards")
memory_manager.update_memory("user123", "We're expecting a baby in 3 months")
memory_manager.update_memory("user123", "Our baby was just born!")

# Get user memory
user_memory = memory_manager.get_memory("user123")
print(user_memory)

# Get memory context for LLM
context = memory_manager.get_memory_context("user123")
print(context)