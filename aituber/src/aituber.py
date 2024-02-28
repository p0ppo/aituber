import os
import dotenv

from .core.chat.openai_chatbot import OpenAIChatBot
from .core.chat.sound_player import SoundPlayer
from .core.chat.tts import VoicePeak
from .core.memory import make_memory_handler, memory_handler_alias
from .network.comment_handler import CommentHandler
from .network.obs_handler import OBSHandler


class AITuber:
    def __init__(self):
        dotenv.load_dotenv()

        # Core modules
        self._chatbot = OpenAIChatBot(segment=True)
        self._player = SoundPlayer()
        self._tts = VoicePeak(player=self._player)
        self._setup_memory()

        # Network modules
        self._setup_video()
        self._comment_handler = CommentHandler(video_id=self._video_id)
        self._obs_handler = OBSHandler()
    
    def _setup_video(self):
        self._video_id = os.environ.get("YOUTUBE_VIDEO_ID")
    
    def _setup_memory(self):
        handler = os.environ.get("MEMORY_HANDLER")
        if handler not in memory_handler_alias.keys():
            raise Exception(f"Memory handler does not support {handler}")
        self._memory_handler = make_memory_handler(handler=handler)
    
    def __call__(self):
        print("Reading comments...")

        comment = self._comment_handler.get_comment()
        if comment is None:
            print("No comments have arived yet.")
            return False
        
        self._memory_handler.add_user_message(comment)
        comment = self._memory_handler.get_messages()
        
        response, segments = self._chatbot.create_chat(comment)
        self._memory_handler.add_ai_message(response)

        self._obs_handler.set_text("question", comment)
        self._obs_handler.set_text("answer", response)
        self._tts.run(segments)
        self._tts.play()
        return


if __name__ == "__main__":
    import time

    aituber = AITuber()
    while True:
        try:
            aituber()
            time.sleep(5)
        except Exception as e:
            raise(f"Error occured. {e}")