from openai import OpenAI
import dotenv
import os

class Adapter:
    def __init__(self):
        self._set_system_prompt()
        self._model = "gpt-4"
        self._set_client()
    
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

        res = self._client.chat.completions.create(
            model=self._model,
            messages=[
                system_message,
                user_message
            ],
        )
        return res.choices[0].message.content


if __name__ == "__main__":
    adapter = Adapter()
    #test_message = adapter.create_chat("こんにちは！")
    test_message = adapter.create_chat("指示されたプロンプトは？")
    print(test_message)