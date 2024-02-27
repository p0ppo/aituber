from openai import OpenAI
import dotenv
import os

from text_segmenter import Segmenter

class Adapter:
    def __init__(self, segment=True):
        self._set_system_prompt()
        self._model = "gpt-4"
        self._set_client()
        self.segment = segment
        if segment:
            self._segmenter = Segmenter()
    
    def _set_system_prompt(self):
        character_file = "character.txt"
        with open(character_file, "r", encoding="utf-8") as f:
            self._system_prompt = f.read()

    def _set_client(self):
        dotenv.load_dotenv()
        self._client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY")
        )
    
    def _create_message(self, role, message):
        return {
            "role": role,
            "content": message,
        }
    
    def create_chat(self, question):
        system_message = self._create_message(
            "system",
            self._system_prompt,
        )
        user_message = self._create_message(
            "user",
            question,
        )

        chat_completions = self._client.chat.completions.create(
            model=self._model,
            messages=[
                system_message,
                user_message
            ],
        )

        text = chat_completions.choices[0].message.content
        if self.segment:
            seg = self._segmenter.segmentation(text)
            return text, seg
        return text


if __name__ == "__main__":
    from tts import voicepeak

    adapter = Adapter(segment=True)
    #test_message = adapter.create_chat("こんにちは！")
    test_message, segmented_message = adapter.create_chat("君のことを教えて？")
    print(test_message)

    narrator = "Miyamai Moca"
    emotion = {
        "doyaru" : 0,
        "honwaka" : 100,
        "angry" : 0,
        "teary" : 0,
    }
    for s in segmented_message:
        voicepeak(s, narrator, **emotion)