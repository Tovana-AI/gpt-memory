import json
import os
import uuid

import pytest

from gptmem import GPTMemoryManager

memory_manager = GPTMemoryManager(
    api_key=os.environ["OPENAI_API_KEY"],
    business_description="A personal therapist",
    include_beliefs=True,
)


@pytest.mark.skip(reason="need llm as a judge")
def test_belief_important_event() -> None:
    test_user_id = str(uuid.uuid4())

    memory_manager.update_memory(test_user_id, "We're expecting a baby in 3 months")
    memory_manager.update_memory(test_user_id, "Our baby was just born!")

    user_memory = memory_manager.get_memory(test_user_id)
    user_memory_dict = json.loads(user_memory)

    beliefs = json.loads(user_memory_dict["beliefs"])
    # TODO Add LLM As a Judge
    assert beliefs
