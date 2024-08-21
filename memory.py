import json
import os
from typing import Dict, Optional
import openai
from datetime import datetime

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    FewShotPromptTemplate,
)

from llms.llms import llm


class GPTMemory:
    def __init__(
        self,
        api_key: str,
        business_description: str,
        generate_beliefs: bool = False,
        memory_file: str = "memory.json",
    ):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.memory_file = memory_file
        self.business_description = business_description
        self.generate_beliefs = generate_beliefs
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
                    self.memory[user_id][existing_key] = self.resolve_conflict(
                        existing_key, self.memory[user_id].get(existing_key), value
                    )
            else:
                self.memory[user_id][key] = value

        # Add timestamp for the last update
        self.memory[user_id]["last_updated"] = datetime.now().isoformat()

        if self.generate_beliefs:
            # Generate new beliefs based on the updated memory
            new_beliefs = self.generate_new_beliefs(user_id)
            if new_beliefs:
                self.memory[user_id]["beliefs"] = new_beliefs

        self.save_memory()
        return self.memory[user_id]

    def find_relevant_key(self, user_id: str, new_key: str) -> Optional[str]:
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
        chain = prompt | llm | StrOutputParser()
        relevant_key = chain.invoke(
            input={
                "user_id": user_id,
                "new_key": new_key,
                "existing_keys": ", ".join(self.memory[user_id].keys()),
            }
        )

        return relevant_key if relevant_key != "None" else None

    def resolve_conflict(self, key: str, old_value: str, new_value: str) -> str:
        template = """
        Resolve the conflict between the old and new values for the following key in the user's memory:

        Key: {key}
        Old value: {old_value}
        New value: {new_value}

        Determine which value is more current or relevant. If the new value represents an update or change, use it.
        If the old value is still valid and the new value is complementary, combine them.
        For example, if the key is "pet" and old value is "Charlie the dog" and the new value is "Luna the horse", combine them as "{{"{{pets: ['Charlie the dog', 'Luna the horse']}}"}}.
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
        chain = prompt | llm | StrOutputParser()
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
        chain = prompt | llm | JsonOutputParser()
        extracted_info = chain.invoke({"user_message": message})

        return extracted_info

    def generate_new_beliefs(self, user_id: str):
        example_prompt = PromptTemplate.from_template(
            """
                <example>
                    <input> {{input}} </input>
                    <output> {{output}} </output>
                </example>
            """,
            template_format="mustache",
        )

        examples = [
            {
                "input": "business_description: a commerce site, memories: {{pets: ['dog named charlie', 'horse named luna'], beliefs: None}}",
                "output": """{{"beliefs": "- suggest pet products for dogs and horses"}}""",
            },
            {
                "input": "business_description: an AI therapist, memories: {{pets: ['dog named charlie', 'horse named luna', sleep_time: '10pm'], beliefs: 'Suggest mediation at 9:30pm'}}",
                "output": """{{"beliefs": "- Suggest mediation at 9:30\\n- Suggest spending time with Charlie and Luna when user is sad"}}""",
            },
            {
                "input": "business_description: an AI personal assistant, memories: {{pets: ['dog named charlie', 'horse named luna', sleep_time: '10pm'], beliefs: None}}",
                "output": """{{"beliefs": "- Don't schedule meetings after 9pm"}}""",
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
            <input>business_description: {business_description}, memories: {memories}, beliefs: {beliefs} </input>
            """,
            input_variables=["business_description", "memories", "beliefs"],
        )

        chain = few_shot_prompt | llm | StrOutputParser()
        beliefs = chain.invoke(
            {
                "business_description": self.business_description,
                "memories": self.get_memory(user_id),
                "beliefs": self.memory.get("beliefs"),
            }
        )
        return beliefs if beliefs != "None" else None

    def get_memory_context(self, user_id: str) -> str:
        if user_id in self.memory:
            context = "User Memory:\n"
            for key, value in self.memory[user_id].items():
                if key != "last_updated":
                    context += f"{key}: {value}\n"
            return context
        return "No memory found for this user."


class GPTMemoryManager:
    def __init__(
        self,
        api_key: str,
        business_description: str = "A personal AI assistant",
        generate_beliefs: bool = True,
    ):
        self.memory = GPTMemory(
            api_key=api_key,
            business_description=business_description,
            generate_beliefs=generate_beliefs,
        )

    def get_memory(self, user_id: str) -> str:
        return self.memory.get_memory(user_id) or "No memory found for this user."

    def update_memory(self, user_id: str, message: str):
        self.memory.update_memory(user_id, message)

    def get_beliefs(self, user_id: str) -> str:
        return self.memory.get_beliefs(user_id) or None

    def get_memory_context(self, user_id: str) -> str:
        return self.memory.get_memory_context(user_id)
