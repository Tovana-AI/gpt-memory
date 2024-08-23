import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Optional, List

import aiofiles
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import (ChatPromptTemplate, FewShotPromptTemplate,
                                    PromptTemplate)

from .llms.llms import GenericLLMProvider

MAX_KEY_LENGTH = 17


class BaseAsyncMemory:
    def __init__(
        self,
        llm: BaseChatModel,
        business_description: str,
        include_beliefs: bool = False,
        memory_file: str = "memory.json",
    ):
        self.llm = llm
        self.memory_file = memory_file
        self.business_description = business_description
        self.include_beliefs = include_beliefs
        self.memory = {}

    async def _load_memory(self) -> Dict[str, Dict]:
        if os.path.exists(self.memory_file):
            async with aiofiles.open(self.memory_file, "r") as f:
                content = await f.read()
                return json.loads(content)
        return {}

    async def _save_memory(self):
        async with aiofiles.open(self.memory_file, "w") as f:
            await f.write(json.dumps(self.memory, indent=2))

    async def get_memory(self, user_id: str) -> Optional[str]:
        if user_id in self.memory:
            return json.dumps(self.memory[user_id], indent=2)
        return None

    async def get_beliefs(self, user_id: str) -> Optional[str]:
        if user_id in self.memory:
            return self.memory[user_id].get("beliefs")
        return None

    async def update_memory(self, user_id: str, message: str) -> Dict:
        if user_id not in self.memory:
            self.memory[user_id] = {}

        extracted_info = await self._extract_information(message)
        await self._update_user_memory(user_id, extracted_info)
        return self.memory[user_id]

    async def batch_update_memory(self, user_id: str, messages: List[Dict[str, str]]) -> Dict:
        if user_id not in self.memory:
            self.memory[user_id] = {}

        extracted_info = await self._extract_batch_information(messages)
        await self._update_user_memory(user_id, extracted_info)
        return self.memory[user_id]

    async def _update_user_memory(self, user_id: str, extracted_info: Dict[str, str]):
        for key, value in extracted_info.items():
            existing_key = await self._find_relevant_key(user_id, key)
            if existing_key:
                if isinstance(self.memory[user_id].get(existing_key), list):
                    self.memory[user_id][existing_key].append(value)
                else:
                    new_value = await self._resolve_conflict(
                        existing_key, self.memory[user_id].get(existing_key), value
                    )
                    self.memory[user_id][existing_key] = new_value
            else:
                self.memory[user_id][key] = value

        self.memory[user_id]["last_updated"] = datetime.now().isoformat()

        if self.include_beliefs:
            new_beliefs = await self._generate_new_beliefs(user_id)
            if new_beliefs:
                self.memory[user_id]["beliefs"] = new_beliefs

        await self._save_memory()

    async def _find_relevant_key(self, user_id: str, new_key: str) -> Optional[str]:
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
        relevant_key = await chain.ainvoke(
            input={
                "user_id": user_id,
                "new_key": new_key,
                "existing_keys": existing_keys,
            }
        )
        if relevant_key == "None" or len(relevant_key) > MAX_KEY_LENGTH:
            return None

        return relevant_key

    async def _resolve_conflict(self, key: str, old_value: str, new_value: str) -> str:
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
        resolved_value = await chain.ainvoke(
            input={"key": key, "old_value": old_value, "new_value": new_value}
        )

        return resolved_value

    async def _extract_information(self, message: str) -> Dict[str, str]:
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
                ("system", system_prompt),
                ("human", "Message: {user_message}"),
            ]
        )
        chain = prompt | self.llm | JsonOutputParser()
        extracted_info = await chain.ainvoke({"user_message": message})

        return extracted_info

    async def _extract_batch_information(self, messages: List[Dict[str, str]]) -> Dict[str, str]:
        system_prompt = """
            You are an AI assistant that extracts relevant personal information from conversations between humans and AI agents.
            Extract relevant personal information from the following conversation only related to the human user. 
            Focus on key details such as location, preferences, important events, or any other significant personal information.
            Ignore irrelevant or redundant information. Try to keep all relevant information under the same key. Less is more.
    
            Guidelines:
            1. Only extract information about the user, not the AI assistant.
            2. Prioritize new or updated information over repeated information.
            3. Combine related information under a single key when possible.
            4. Ignore pleasantries, small talk, or information not directly related to the user.
            5. If conflicting information is provided, use the most recent or most specific information.
    
            Return the extracted information as a JSON object with appropriate keys (lower case) and values.
            Do not use any specific format (like ```json), just provide the extracted information as a JSON.
            Remember that the memory could be very long so try to keep values concise and short with no explanations.
            """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Conversation:\n{conversation}"),
        ])

        conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        chain = prompt | self.llm | JsonOutputParser()
        extracted_info = await chain.ainvoke({"conversation": conversation})

        return extracted_info

    async def _generate_new_beliefs(self, user_id: str):
        example_prompt = PromptTemplate.from_template(
            """
            Examples that will help you generate an amazing answer
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
                    You are an AI assistant that extracts relevant actionable insights (beliefs) based on memory about the user and their business description
                    Beliefs are actionable insights that can be used by the AI to provide better assistance and reasoning related to their business description and goals.
                    Given a business description, memories, and existing belief context, generate new beliefs only if necessary. 
                    If no new beliefs are found, return 'None'""",
            suffix="""
                    Do not use any specific format (like ```json), just provide the extracted information as a JSON.
                    Input - business_description: {business_description}, memories: {memories}, beliefs: {beliefs}
                    Output (JSON) - 
                    """,
            input_variables=["business_description", "memories", "beliefs"],
        )

        chain = few_shot_prompt | self.llm | StrOutputParser()
        beliefs = await chain.ainvoke(
            {
                "business_description": self.business_description,
                "memories": await self.get_memory(user_id),
                "beliefs": self.memory.get("beliefs"),
            }
        )
        return beliefs if beliefs != "None" else None

    async def get_memory_context(
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

                filtered_context = await chain.ainvoke(
                    {"context": context, "message": message}
                )
                return filtered_context
            return context
        return "No memory found for this user."

    async def delete_memory(self, user_id: str) -> bool:
        if user_id in self.memory:
            del self.memory[user_id]
            await self._save_memory()
            return True
        return False


class SyncMemory(BaseAsyncMemory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = asyncio.run(self._load_memory())

    def update_memory(self, user_id: str, message: str) -> Dict:
        return asyncio.run((super().update_memory(user_id, message)))

    def batch_update_memory(self, user_id: str, messages: List[Dict[str, str]]) -> Dict:
        return asyncio.run(super().batch_update_memory(user_id, messages))

    def get_beliefs(self, user_id: str) -> Optional[str]:
        return asyncio.run(super().get_beliefs(user_id))

    def get_memory_context(self, user_id: str, message: Optional[str] = "") -> str:
        return asyncio.run(super().get_memory_context(user_id, message))

    def delete_memory(self, user_id: str) -> bool:
        return asyncio.run(super().delete_memory(user_id))


class BaseMemoryManager:
    def __init__(
        self,
        api_key: str,
        provider: str,
        business_description: str = "A personal AI assistant",
        include_beliefs: bool = True,
        **kwargs,
    ):
        self.llm = GenericLLMProvider.from_provider(
            provider=provider, api_key=api_key, **kwargs
        ).llm
        self.business_description = business_description
        self.include_beliefs = include_beliefs


class AsyncMemoryManager(BaseMemoryManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = BaseAsyncMemory(
            llm=self.llm,
            business_description=self.business_description,
            include_beliefs=self.include_beliefs,
        )

    async def get_memory(self, user_id: str) -> str:
        return (
                await self.memory.get_memory(user_id) or "No memory found for this user."
        )

    async def update_memory(self, user_id: str, message: str):
        await self.memory.update_memory(user_id, message)

    async def batch_update_memory(self, user_id: str, messages: List[Dict[str, str]]):
        await self.memory.batch_update_memory(user_id, messages)

    async def delete_memory(self, user_id: str) -> bool:
        return await self.memory.delete_memory(user_id)

    async def get_beliefs(self, user_id: str) -> str:
        return await self.memory.get_beliefs(user_id) or None

    async def get_memory_context(
        self, user_id: str, message: Optional[str] = ""
    ) -> str:
        return await self.memory.get_memory_context(user_id, message)


class MemoryManager(BaseMemoryManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = SyncMemory(
            llm=self.llm,
            business_description=self.business_description,
            include_beliefs=self.include_beliefs,
        )

    def get_memory(self, user_id: str) -> str:
        return (
            asyncio.run(self.memory.get_memory(user_id))
            or "No memory found for this user."
        )

    def update_memory(self, user_id: str, message: str):
        self.memory.update_memory(user_id, message)

    def batch_update_memory(self, user_id: str, messages: List[Dict[str, str]]):
        self.memory.batch_update_memory(user_id, messages)

    def delete_memory(self, user_id: str) -> bool:
        return self.memory.delete_memory(user_id)

    def get_beliefs(self, user_id: str) -> str:
        return self.memory.get_beliefs(user_id) or None

    def get_memory_context(self, user_id: str, message: Optional[str] = "") -> str:
        return self.memory.get_memory_context(user_id, message)
