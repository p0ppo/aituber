import os
import dotenv
import time
import click

#from .core.agent import Agent, SoundPlayer, VoicePeak
from .core.agent import Executor, SoundPlayer, VoicePeak
#from .core.agent import ChiefAgent, SoundPlayer, VoicePeak
from .network import CommentHandler, OBSHandler


class AITuber:
    def __init__(self):
        dotenv.load_dotenv()

        # Core modules
        self._setup_core()

        # Network modules
        self._setup_network()
    
    def _setup_core(self):
        #self._agent = Agent(segment=True)
        #self._agent = ChiefAgent(segment=True)
        self._agent = Executor(segment=True, verbose=True)
        self._player = SoundPlayer()
        self._tts = VoicePeak(player=self._player)
    
    def _setup_network(self):
        self._video_id = os.environ.get("YOUTUBE_VIDEO_ID")
        self._comment_handler = CommentHandler(video_id=self._video_id)
        self._obs_handler = OBSHandler()
    
    def __call__(self):
        print("Reading comments...")

        comment = self._comment_handler.get_comment()
        if comment is None:
            print("No comments have arived yet.")
            return False
        
        response, segments = self._agent.get_messages(comment)
        print(response)

        self._obs_handler.set_text("question", comment)
        self._obs_handler.set_text("answer", response)
        self._tts.run(segments)
        self._tts.play()
        return


@click.command(name="broadcast")
def broadcast():
    aituber = AITuber()
    while True:
        try:
            aituber()
            time.sleep(5)
        except Exception as e:
            raise(f"Error occured. {e}")


if __name__ == "__main__":
    import time

    aituber = AITuber()
    while True:
        try:
            aituber()
            time.sleep(5)
        except Exception as e:
            raise(f"Error occured. {e}")