import json
import os
import uuid
from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

import pytest
from langchain_openai import ChatOpenAI

from gptmem import GPTMemoryManager

memory_manager = GPTMemoryManager(
    api_key=os.environ["OPENAI_API_KEY"],
    business_description="A personal therapist",
    include_beliefs=True,
)


class PetInfo(BaseModel):
    pets: List[str] = Field(description="List of pets with their names")

def test_extract_pet_info() -> None:
    res = memory_manager.memory.extract_information(
        "We also have a pet dog named Charlie"
    )

    if "pet" in res:
        assert "Charlie" in res["pet"]
    if "pets" in res:
        assert "Charlie" in res["pets"]

    pared =  PydanticOutputParser(pydantic_object=PetInfo)

    print(pared)