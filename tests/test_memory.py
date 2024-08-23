import json
import os
import uuid

import pytest

from memory import SyncMemoryManager

memory_manager = SyncMemoryManager(
    api_key=os.environ["OPENAI_API_KEY"],
    provider="openai",
    business_description="A personal therapist",
    include_beliefs=True,
)


def test_entity_extraction() -> None:
    test_user_id = str(uuid.uuid4())
    memory_manager.update_memory(test_user_id, "We also have a pet dog named Charlie")

    user_memory = memory_manager.get_memory(test_user_id)
    user_memory_dict = json.loads(user_memory)

    assert user_memory_dict["pet"] == "dog named Charlie"


def test_entity_extraction_multiple_entities_same_type() -> None:
    test_user_id = str(uuid.uuid4())
    memory_manager.update_memory(test_user_id, "We also have a pet dog named Charlie")
    memory_manager.update_memory(test_user_id, "We also have a pet horse named Luna")

    user_memory = memory_manager.get_memory(test_user_id)
    user_memory_dict = json.loads(user_memory)

    assert "dog named Charlie" in user_memory_dict["pet"]
    assert "horse named Luna" in user_memory_dict["pet"]


def test_remember_location() -> None:
    test_user_id = str(uuid.uuid4())
    memory_manager.update_memory(test_user_id, "We also have a pet dog named Charlie")
    memory_manager.update_memory(test_user_id, "We also have a pet horse named Luna")
    memory_manager.update_memory(test_user_id, "We live in New York City")

    user_memory = memory_manager.get_memory(test_user_id)
    user_memory_dict = json.loads(user_memory)

    assert user_memory_dict["location"] == "New York City"


@pytest.mark.xfail(reason="different keys")
def test_relationship_detection() -> None:
    test_user_id = str(uuid.uuid4())
    memory_manager.update_memory(test_user_id, "We also have a pet dog named Charlie")
    memory_manager.update_memory(test_user_id, "We also have a pet horse named Luna")
    memory_manager.update_memory(test_user_id, "We live in New York City")
    memory_manager.update_memory(
        test_user_id, "I have young girl named Lisa and married to my wife Mai"
    )

    user_memory = memory_manager.get_memory(test_user_id)
    user_memory_dict = json.loads(user_memory)

    assert user_memory_dict["family"]
    assert "Lisa" in user_memory_dict["family"]
    assert "Mai" in user_memory_dict["family"]


def test_important_event() -> None:
    test_user_id = str(uuid.uuid4())

    memory_manager.update_memory(test_user_id, "We're expecting a baby in 3 months")
    user_memory = memory_manager.get_memory(test_user_id)

    memory_manager.update_memory(test_user_id, "Our baby was just born!")
    user_memory_dict = json.loads(user_memory)

    user_memory = memory_manager.get_memory(test_user_id)
    user_memory_dict = json.loads(user_memory)

    assert user_memory_dict["important_event"] == "baby born"
