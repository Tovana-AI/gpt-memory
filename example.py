import json
import os
import uuid

from gptmem import GPTMemoryManager

user_id = str(uuid.uuid4())
# Initialize the memory manager with your OpenAI API key
memory_manager = GPTMemoryManager(
    api_key=os.environ["OPENAI_API_KEY"],
    provider="openai",
    temperature=0,
    business_description="A personal therapist",
    include_beliefs=True,
)

# Update user memory
memory_manager.update_memory(user_id, "We also have a pet dog named Charlie")
memory_manager.update_memory(user_id, "We also have a pet horse named Luna")
memory_manager.update_memory(user_id, "We live in New York City")
memory_manager.update_memory(
    user_id, "I have young girl named Lisa and married to my wife Mai"
)
memory_manager.update_memory(user_id, "I love playing basketball and trading cards")
memory_manager.update_memory(user_id, "We're expecting a baby in 3 months")
memory_manager.update_memory(user_id, "Our baby was just born!")

# Get user memory
user_memory = memory_manager.get_memory(user_id)
# print(user_memory)

# Get general memory context for LLM
context = memory_manager.get_memory_context(user_id)
print(context)


# Get specific message related memory context for LLM
context = memory_manager.get_memory_context(
    user_id, message="there is a new basketball court in the park"
)
print(context)


beliefs = memory_manager.get_beliefs(user_id)
# print(beliefs)
