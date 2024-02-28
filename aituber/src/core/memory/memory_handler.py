import os
import abc
import dotenv
from langchain.memory import PostgresChatMessageHistory


class MemoryHandler(abc.ABC):
    @abc.abstractmethod
    def _add_user_message(self, message):
        pass

    @abc.abstractmethod
    def _add_ai_message(self, message):
        pass

    @abc.abstractmethod
    def get_messages(self):
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
    
    def get_messages(self):
        return "\n".join(self._memory)
    

class LangchainMemoryHandler(MemoryHandler):
    def __init__(self):
        self._set_memory()
    
    def _set_memory(self):
        dotenv.load_dotenv()
        _postgresql_hostname = os.environ.get("POSTGRESQL_HOSTNAME")
        _postgresql_password = os.environ.get("POSTGRESQL_PASSWARD")
        _postgresql_database = os.environ.get("POSTGRESQL_DATABASE")
        self._memory = PostgresChatMessageHistory(
            connection_string= \
                f"postgresql://postgres:{_postgresql_password}" + \
                f"@{_postgresql_hostname}/" + \
                f"/{_postgresql_database}",
            session_id="foo",  # Arbitrary ID available, I guess.
        )
    
    def add_user_message(self, message):
        self._memory.add_user_message(message)
    
    def add_ai_message(self, message):
        self._memory.add_ai_message(message)
    
    def get_messages(self):
        return self._memory.messages