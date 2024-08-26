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
    business_description="A personal travel assistant",
    include_beliefs=True,
)
start_time = time.time()

# Conversation messages between human and agent
conversation = [
    {"role": "human", "content": "Hi, I'm planning a trip to Japan next month."},
    {
        "role": "assistant",
        "content": "That's exciting! Japan is a wonderful destination. What kind of activities are you interested in?",
    },
    {
        "role": "human",
        "content": "I love trying local cuisine and visiting historical sites.",
    },
    {
        "role": "assistant",
        "content": "Great choices! Japan offers amazing food and rich history. Any specific cities you'd like to visit?",
    },
    {
        "role": "human",
        "content": "I'm thinking of Tokyo and Kyoto. Maybe Osaka too if I have time.",
    },
    {
        "role": "assistant",
        "content": "Excellent choices. Tokyo is modern and bustling, Kyoto is full of traditional culture, and Osaka is known for its food scene.",
    },
    {
        "role": "human",
        "content": "That sounds perfect. I'll be traveling with my partner, and we're both vegetarians.",
    },
    {
        "role": "assistant",
        "content": "I'll keep that in mind. Japan has been improving its vegetarian options, especially in larger cities. I can help you find suitable restaurants.",
    },
]

# Batch update user memory with the conversation
memory_manager.batch_update_memory(user_id, conversation)

# Get user memory
user_memory = memory_manager.get_memory(user_id)
print("User Memory:")
print(user_memory)

# Get general memory context for LLM
context = memory_manager.get_memory_context(user_id)
print("\nGeneral Memory Context:")
print(context)

# Get specific message related memory context for LLM
context = memory_manager.get_memory_context(
    user_id, message="Can you recommend some restaurants for tonight?"
)
print("\nSpecific Memory Context:")
print(context)

beliefs = memory_manager.get_beliefs(user_id)
print("\nBeliefs:")
print(beliefs)

end_time = time.time()
print(f"\nTotal time taken: {end_time - start_time:.2f} seconds")
