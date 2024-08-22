import json
import logging
import os
from datetime import datetime
from typing import Dict, Optional

import openai
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    PromptTemplate,
)

from gptmem.llms.llms import GenericLLMProvider

MAX_KEY_LENGTH = 17


class GPTMemory:
    def __init__(
        self,
        api_key: str,
        llm: BaseChatModel,
        business_description: str,
        include_beliefs: bool = False,
        memory_file: str = "memory.json",
    ):
        self.api_key = api_key  # TODO remove
        self.llm = llm
        self.memory_file = memory_file
        self.business_description = business_description
        self.include_beliefs = include_beliefs
        self.memory = self.load_memory()

    def load_memory(self) -> Dict[str, Dict]:
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                return json.load(f)
        return {}

    def save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2)

    def get_memory(self, user_id: str) -> Optional[str]:
        if user_id in self.memory:
            return json.dumps(self.memory[user_id], indent=2)
        return None

    def get_beliefs(self, user_id: str) -> Optional[str]:
        if user_id in self.memory:
            return self.memory[user_id].get("beliefs")
        return None

    def update_memory(self, user_id: str, message: str) -> Dict:
        if user_id not in self.memory:
            self.memory[user_id] = {}

        # Extract relevant information from the message
        extracted_info = self.extract_information(message)

        # Update memory with extracted information
        for key, value in extracted_info.items():
            existing_key = self.find_relevant_key(user_id, key)
            if existing_key:
                if isinstance(self.memory[user_id].get(existing_key), list):
                    # Append to the existing list
                    self.memory[user_id][existing_key].append(value)
                else:
                    # Resolve conflict and update the value
                    new_value = self.resolve_conflict(
                        existing_key, self.memory[user_id].get(existing_key), value
                    )
                    self.memory[user_id][existing_key] = new_value
            else:
                self.memory[user_id][key] = value

        self.memory[user_id]["last_updated"] = datetime.now().isoformat()

        if self.include_beliefs:
            # Generate new beliefs based on the updated memory
            new_beliefs = self.generate_new_beliefs(user_id)
            if new_beliefs:
                self.memory[user_id]["beliefs"] = new_beliefs

        self.save_memory()
        return self.memory[user_id]

    def find_relevant_key(self, user_id: str, new_key: str) -> Optional[str]:
        existing_keys = ", ".join(self.memory[user_id].keys())
        template = """
               Find the most relevant existing key in the user's memory for the new information.
               If no relevant key exists, return "None".

               Existing keys: {existing_keys}
               New key: {new_key}

               Return only the existing key that is most relevant, or "None" if no relevant key exists.
               """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an AI assistant that finds relevant keys in user memory",
                ),
                ("human", template),
            ]
        )
        chain = prompt | self.llm | StrOutputParser()
        relevant_key = chain.invoke(
            input={
                "user_id": user_id,
                "new_key": new_key,
                "existing_keys": existing_keys,
            }
        )
        if relevant_key == "None" or len(relevant_key) > MAX_KEY_LENGTH:
            # hack to not include cases with 'None' to be a key in memory
            # or cases where model ignores instruction and adds reasoning as a key
            return None

        return relevant_key

    def resolve_conflict(self, key: str, old_value: str, new_value: str) -> str:
        template = """
                Resolve the conflict between the old and new values for the following key in the user's memory:

                Key: {key}
                Old value: {old_value}
                New value: {new_value}

                Determine which value is more current or relevant. If the new value represents an update or change, use it.
                If the old value is still valid and the new value is complementary, combine them.
                For example, if the key is "pet" and old value is "Charlie the dog" and the new value is "Luna the horse", combine them as "['Charlie the dog', 'Luna the horse']".
                Return the resolved value as a string. You must keep the value short and concise with no explanation.
                """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an AI assistant that resolves conflicts in user memory updates",
                ),
                ("human", template),
            ]
        )
        chain = prompt | self.llm | StrOutputParser()
        resolved_value = chain.invoke(
            input={"key": key, "old_value": old_value, "new_value": new_value}
        )

        return resolved_value

    def extract_information(self, message: str) -> Dict[str, str]:
        system_prompt = """
          You are an AI assistant that extracts relevant personal information from messages
          Extract relevant personal information from the following message. 
          Focus on key details such as location, preferences, important events, or any other significant personal information.
          Ignore irrelevant or redundant information. Try to keep all relevant information under the same key. Less is more.

          Return the extracted information as a JSON object with appropriate keys (lower case) and values.
          Do not use any specific format (like ```json), just provide the extracted information as a JSON.
          Remembers that the memory could be very long so try to keep values concise and short with no explanations.
          """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_prompt,
                ),
                ("human", "Message: {user_message}"),
            ]
        )
        chain = prompt | self.llm | JsonOutputParser()
        extracted_info = chain.invoke({"user_message": message})

        return extracted_info

    def generate_new_beliefs(self, user_id: str):
        example_prompt = PromptTemplate.from_template(
            """
            Input - {input}
            Output (JSON) - {output} 
            """,
        )

        examples = [
            {
                "input": "business_description: a commerce site, memories: {{pets: ['dog named charlie', 'horse named luna'], beliefs: None}}",
                "output": '{{"beliefs": "- suggest pet products for dogs and horses"}}',
            },
            {
                "input": "business_description: an AI therapist, memories: {{pets: ['dog named charlie', 'horse named luna', sleep_time: '10pm'], beliefs: 'Suggest mediation at 9:30pm'}}",
                "output": '{{"beliefs": "- Suggest mediation at 9:30\\n- Suggest spending time with Charlie and Luna when user is sad"}}',
            },
            {
                "input": "business_description: an AI personal assistant, memories: {{pets: ['dog named charlie', 'horse named luna', sleep_time: '10pm'], beliefs: None}}",
                "output": '{{"beliefs": "- Do not schedule meetings after 9pm"}}',
            },
        ]

        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix="""
                    You are an AI assistant that extracts relevant actionable insights based on memory about the user and their business description
                    Given a business description, memories, and existing belief context, generate new actionable beliefs if necessary. 
                                                                If no new beliefs are found, return 'None'""",
            suffix="""
                    Do not use any specific format (like ```json), just provide the extracted information as a JSON.
                    Input - business_description: {business_description}, memories: {memories}, beliefs: {beliefs}
                    Output (JSON) - 
                    """,
            input_variables=["business_description", "memories", "beliefs"],
        )

        chain = few_shot_prompt | self.llm | StrOutputParser()
        beliefs = chain.invoke(
            {
                "business_description": self.business_description,
                "memories": self.get_memory(user_id),
                "beliefs": self.memory.get("beliefs"),
            }
        )
        return beliefs if beliefs != "None" else None

    def get_memory_context(
        self,
        user_id: str,
        message: Optional[str] = "",
    ) -> str:
        if user_id in self.memory:
            context = "User Memory:\n"
            for key, value in self.memory[user_id].items():
                if key != "last_updated":
                    context += f"{key}: {value}\n"

            if message:
                prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            "You are an AI assistant that filters relevant information from user memory based on a given message."
                            "Return only the relevant information from the user memory that relates to the message."
                            "Provide the output in the same format as the input memory",
                        ),
                        (
                            "human",
                            "User Memory:\n{context}\n\nMessage: {message}\n\nUser Memory:",
                        ),
                    ]
                )

                chain = prompt | self.llm | StrOutputParser()

                filtered_context = chain.invoke(
                    {"context": context, "message": message}
                )
                return filtered_context
            return context
        return "No memory found for this user."


class GPTMemoryManager:
    def __init__(
        self,
        api_key: str,
        provider: str,
        business_description: str = "A personal AI assistant",
        include_beliefs: bool = True,
        **kwargs,
    ):
        # initialize model
        llm = GenericLLMProvider.from_provider(provider=provider, **kwargs).llm

        self.memory = GPTMemory(
            api_key=api_key,  # TODO remove
            llm=llm,
            business_description=business_description,
            include_beliefs=include_beliefs,
        )

    def get_memory(self, user_id: str) -> str:
        return self.memory.get_memory(user_id) or "No memory found for this user."

    def update_memory(self, user_id: str, message: str):
        self.memory.update_memory(user_id, message)

    def get_beliefs(self, user_id: str) -> str:
        return self.memory.get_beliefs(user_id) or None

    def get_memory_context(self, user_id: str, message: Optional[str] = "") -> str:
        return self.memory.get_memory_context(user_id, message)
