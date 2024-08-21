import json
import os
from typing import Dict, List, Optional
import openai
from datetime import datetime


class GPTMemory:
    def __init__(self, api_key: str, business_description: str,
                 include_beliefs: bool = False, memory_file: str = "memory.json"):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.memory_file = memory_file
        self.business_description = business_description
        self.include_beliefs = include_beliefs
        self.memory = self.load_memory()

    def load_memory(self) -> Dict[str, Dict]:
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {}

    def save_memory(self):
        with open(self.memory_file, 'w') as f:
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
                        existing_key,
                        self.memory[user_id].get(existing_key),
                        value
                    )
            else:
                self.memory[user_id][key] = value

        # Add timestamp for the last update
        self.memory[user_id]['last_updated'] = datetime.now().isoformat()

        if self.include_beliefs:
            # Generate new beliefs based on the updated memory
            new_beliefs = self.generate_new_beliefs(user_id)
            if new_beliefs:
                self.memory[user_id]['beliefs'] = new_beliefs

        self.save_memory()
        return self.memory[user_id]

    def find_relevant_key(self, user_id: str, new_key: str) -> Optional[str]:
        prompt = f"""
        Find the most relevant existing key in the user's memory for the new information.
        If no relevant key exists, return "None".

        Existing keys: {', '.join(self.memory[user_id].keys())}
        New key: {new_key}

        Return only the existing key that is most relevant, or "None" if no relevant key exists.
        """

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant that finds relevant keys in user memory."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        relevant_key = response.choices[0].message.content.strip()
        return relevant_key if relevant_key != "None" else None

    def resolve_conflict(self, key: str, old_value: str, new_value: str) -> str:
        prompt = f"""
        Resolve the conflict between the old and new values for the following key in the user's memory:

        Key: {key}
        Old value: {old_value}
        New value: {new_value}

        Determine which value is more current or relevant. If the new value represents an update or change, use it.
        If the old value is still valid and the new value is complementary, combine them. For example, if the key is "pet" and old value is "Charlie the dog" and the new value is "Luna the horse", combine them as "{"{pets: ['Charlie the dog', 'Luna the horse']}"}.
        Return the resolved value as a string. You must keep the value short and concise with no explanation.
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "You are an AI assistant that resolves conflicts in user memory updates."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        resolved_value = response.choices[0].message.content.strip()
        return resolved_value

    def extract_information(self, message: str) -> Dict[str, str]:
        prompt = f"""
        Extract relevant personal information from the following message. 
        Focus on key details such as location, preferences, important events, or any other significant personal information.
        Ignore irrelevant or redundant information. Try to keep all relevant information under the same key. Less is more.

        Message: {message}

        Return the extracted information as a JSON object with appropriate keys (lower case) and values.
        Do not use any specific format (like ```json), just provide the extracted information as a JSON.
        Remembers that the memory could be very long so try to keep values concise and short with no explanations.
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "You are an AI assistant that extracts relevant personal information from messages."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        extracted_info = json.loads(response.choices[0].message.content)
        return extracted_info

    def generate_new_beliefs(self, user_id: str):
        examples = """
        Input - business_description: a commerce site, memories: {pets: ['dog named charlie', 'horse named luna'], beliefs: None
        Output (JSON) - {"beliefs": "- suggest pet products for dogs and horses"}

        Input - business_description: an AI therapist, memories: {pets: ['dog named charlie', 'horse named luna', sleep_time: '10pm'], beliefs: 'Suggest mediation at 9:30pm'}
        Output (JSON) - {"beliefs": "- Suggest mediation at 9:30\\n- Suggest spending time with Charlie and Luna when user is sad"}
        
        Input - business_description: an AI personal assistant, memories: {pets: ['dog named charlie', 'horse named luna', sleep_time: '10pm'], beliefs: None}
        Output (JSON) - {"beliefs": "- Don't schedule meetings after 9pm"}
        """

        prompt = f"""
        Given a business description, memories, and existing belief context, generate new actionable beliefs if necessary. 
        If no new beliefs are found, return 'None'.

        {examples}
        
        Do not use any specific format (like ```json), just provide the extracted information as a JSON.

        Input - business_description: {self.business_description}, memories: {self.get_memory(user_id)}, beliefs: {self.memory.get("beliefs")}
        Output (JSON) - 
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "You are an AI assistant that extracts relevant actionable "
                            "insights based on memory about the user and their business description."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        beliefs = response.choices[0].message.content.strip()
        return beliefs if beliefs != "None" else None

    def get_memory_context(self, user_id: str) -> str:
        if user_id in self.memory:
            context = "User Memory:\n"
            for key, value in self.memory[user_id].items():
                if key != 'last_updated':
                    context += f"{key}: {value}\n"
            return context
        return "No memory found for this user."


class GPTMemoryManager:
    def __init__(self, api_key: str, business_description: str = "A personal AI assistant",
                 include_beliefs: bool = True):
        self.memory = GPTMemory(api_key=api_key,
                                business_description=business_description,
                                include_beliefs=include_beliefs)

    def get_memory(self, user_id: str) -> str:
        return self.memory.get_memory(user_id) or "No memory found for this user."

    def update_memory(self, user_id: str, message: str):
        self.memory.update_memory(user_id, message)

    def get_beliefs(self, user_id: str) -> str:
        return self.memory.get_beliefs(user_id) or None

    def get_memory_context(self, user_id: str) -> str:
        return self.memory.get_memory_context(user_id)