import json
import os
import time
import uuid

from tovana import MemoryManager

user_id = str(uuid.uuid4())
# Initialize the memory manager with your OpenAI API key
memory_manager = MemoryManager(
    api_key=os.environ["OPENAI_API_KEY"],
    provider="openai",
    temperature=0.2,
    business_description="An AI therapist",
    include_beliefs=True,
)
start_time = time.time()

# Update user memory
memory_manager.update_memory(user_id, "We also have a pet dog named Charlie")
memory_manager.update_memory(user_id, "We also have a pet horse named Luna")
memory_manager.update_memory(user_id, "We live in New York City")
memory_manager.update_memory(
    user_id, "We have young girl named Lisa and I'm married to my wife Gabby"
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

end_time = time.time()
print(f"Total time taken: {end_time - start_time:.2f} seconds")
