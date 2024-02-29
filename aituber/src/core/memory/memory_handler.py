import os
import abc
import dotenv

from langchain.prompts import (
    ChatPromptTemplate, 
    HumanMessagePromptTemplate, 
    MessagesPlaceholder
    )
from langchain.memory import PostgresChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage


class MemoryHandler(abc.ABC):
    @abc.abstractmethod
    def add_user_message(self, message):
        pass

    @abc.abstractmethod
    def add_ai_message(self, message):
        pass

    @abc.abstractmethod
    def get_messages(self, **kwargs):
        pass


class SimpleMemoryHandler(MemoryHandler):
    def __init__(self):
        self._num_max_memory = 50
        self._memory = list()
    
    def _add_message(self, message):
        self._memory.append(message)
        if len(self._memory) > self._num_max_memory:
            self._memory = self._memory[-self._num_max_memory:]
    
    def add_user_message(self, message):
        self._add_message(message)
    
    def add_ai_message(self, message):
        self._add_message(message)
    
    def get_messages(self, message):
        self.add_user_message(message)
        return "\n".join(self._memory)
    

class LangchainMemoryHandler(MemoryHandler):
    def __init__(self):
        self._num_max_memory = 50
        self._set_memory()

        # Do not change
        self._summarize_description = HumanMessagePromptTemplate.from_template(
            "Summarize our conversation so far and answer the following comment in Japanese."
        )
        self._chat_prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="conversation"),
                self._summarize_description,
                MessagesPlaceholder(variable_name="latest"),
            ]
        )
    
    def _set_memory(self):
        dotenv.load_dotenv()
        _postgresql_hostname = os.environ.get("POSTGRESQL_HOSTNAME")
        _postgresql_password = os.environ.get("POSTGRESQL_PASSWORD")
        _postgresql_database = os.environ.get("POSTGRESQL_DATABASE")
        print(f"postgresql://postgres:{_postgresql_password}" + \
            f"@{_postgresql_hostname}/" + \
            f"{_postgresql_database}")
        self._memory = PostgresChatMessageHistory(
            connection_string= \
                f"postgresql://postgres:{_postgresql_password}" + \
                f"@{_postgresql_hostname}/" + \
                f"{_postgresql_database}",
            session_id="foo",  # Arbitrary ID available, I guess.
        )
    
    def add_user_message(self, message):
        self._memory.add_user_message(message)
    
    def add_ai_message(self, message):
        self._memory.add_ai_message(message)
    
    def get_messages(self, message):
        latest = HumanMessage(content=message)
        message = self._chat_prompt.format_prompt(
            conversation=self._memory.messages[-self._num_max_memory:],
            latest=[latest],
        ).to_messages()
        return message