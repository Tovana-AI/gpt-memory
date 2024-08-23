import asyncio
import os
import time
import uuid
from typing import List

from tovana import AsyncMemoryManager


async def update_user_memory(
    memory_manager: AsyncMemoryManager, user_id: str, messages: List[str]
):
    for message in messages:
        await memory_manager.update_memory(user_id, message)

    context = await memory_manager.get_memory_context(user_id)
    print(f"Memory context for user {user_id}:\n{context}\n")

    beliefs = await memory_manager.get_beliefs(user_id)
    print(f"Beliefs for user {user_id}:\n{beliefs}\n")


async def main():
    memory_manager = AsyncMemoryManager(
        api_key=os.environ["MISTRAL_API_KEY"],
        provider="mistralai",
        temperature=0,
        business_description="A personal therapist",
        include_beliefs=True,
    )

    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    user3_id = str(uuid.uuid4())

    # Define messages for each user
    user1_messages = [
        "We have a pet dog named Charlie",
        "We live in New York City",
        "I have a young daughter named Lisa",
        "I love playing basketball",
        "We're expecting a baby in 3 months",
    ]

    user2_messages = [
        "I recently moved to San Francisco",
        "I'm learning to play the guitar",
        "I work as a software engineer",
        "I'm planning a trip to Japan next year",
    ]

    user3_messages = [
        "I'm a college student studying physics",
        "I have two cats named Sun and Moon",
        "I'm passionate about physics issues",
    ]

    # Measure the time it takes to update memory for all users concurrently
    start_time = time.time()

    await asyncio.gather(
        update_user_memory(memory_manager, user1_id, user1_messages),
        update_user_memory(memory_manager, user2_id, user2_messages),
        update_user_memory(memory_manager, user3_id, user3_messages),
    )

    end_time = time.time()
    print(f"Total time taken: {end_time - start_time:.2f} seconds")

    # Demonstrate getting context for a specific message
    context = await memory_manager.get_memory_context(
        user1_id, message="There is a new basketball court in the park"
    )
    print(f"Specific context for user {user1_id}:\n{context}")


if __name__ == "__main__":
    asyncio.run(main())
