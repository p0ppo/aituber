import os


class MemoryHandler:
    def __init__(self):
        self._num_max_memory = 50
        self._memory = list()
    
    def __call__(self, comment):
        self._memory.append(comment)
        if len(self._memory) > self._num_max_memory:
            self._memory = self._memory[-self._num_max_memory:]
        return "\n".join(self._memory)