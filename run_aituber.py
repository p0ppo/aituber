import os
import dotenv

from adapter import Adapter
from sound_player import SoundPlayer
from tts import VoicePeak
from comment_handler import CommentHandler
from obs_handler import OBSHandler


class AITuber:
    def __init__(self):
        self._setup_video()
        self._adapter = Adapter(segment=True)
        self._player = SoundPlayer()
        self._tts = VoicePeak(player=self._player)
        self._comment_handler = CommentHandler(video_id=self._video_id)
        self._obs_handler = OBSHandler()
    
    def _setup_video(self):
        dotenv.load_dotenv()
        self._video_id = os.environ.get("YOUTUBE_VIDEO_ID")
    
    def __call__(self):
        print("Reading comments...")

        comment = self._comment_handler.get_comment()
        if comment is None:
            print("No comments arived yet.")
            return False
        
        response, segments = self._adapter.create_chat(comment)
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