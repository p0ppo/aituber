import dotenv
import os

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
from langchain_openai import ChatOpenAI, OpenAI

from .text_segmenter import Segmenter

class ChatBot:
    def __init__(self, segment=True):
        dotenv.load_dotenv()
        self._set_client()
        self.segment = segment
        if segment:
            self._segmenter = Segmenter(max_characters=140)

    def _set_client(self):
        self._client = ChatOpenAI(
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            model_name="gpt-4",
            streaming=True, 
        )
        self._set_memory()
        self._set_prompt()
        self._chain = ConversationChain(
            memory=self._memory_handler,
            prompt=self._prompt,
            llm=self._client,
            verbose=True,
        )

    def _set_memory(self):
        self._memory_handler = ConversationSummaryBufferMemory(
            llm=OpenAI(),
            return_messages=True
            )
    
    def _set_prompt(self):
        character_file = os.environ.get("CHARACTER_PATH")
        with open(character_file, "r", encoding="utf-8") as f:
            self._system_prompt = f.read()
        self._prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(self._system_prompt),
                MessagesPlaceholder(variable_name="history"),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )

    def get_messages(self, message):
        print(self._memory_handler.load_memory_variables({}))
        resp = self._chain.predict(input=message)
        if self.segment:
            seg = self._segmenter.segmentation(resp)
            return resp, seg
        return resp


if __name__ == "__main__":
    from tts import voicepeak

    adapter = OpenAIChatBot(segment=True)
    #test_message = adapter.create_chat("こんにちは！")
    test_message, segmented_message = adapter.create_chat("君のことを教えて？")
    print(test_message)
    print(segmented_message)
    for s in segmented_message:
        print(len(s))

    narrator = "Miyamai Moca"
    emotion = {
        "doyaru" : 0,
        "honwaka" : 100,
        "angry" : 0,
        "teary" : 0,
    }
    for s in segmented_message:
        voicepeak(s, narrator, **emotion)