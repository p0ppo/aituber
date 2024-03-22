import os
import subprocess
import glob
import dotenv
import time
import click

from .agent import Executor, SoundPlayer, VoicePeak
from .network import CommentHandler, OBSHandler


def convert_path_unix2win(path):
    return subprocess.run(
        ["wslpath", "-m", path],
        capture_output=True,
        text=True
    ).stdout


class AITuber:
    def __init__(self):
        dotenv.load_dotenv()

        # Core modules
        self._setup_core()

        # Network modules
        self._setup_network()
    
    def _setup_core(self):
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

        # FIXME: run task specific handler on event, not always
        mahjong_svg_path = sorted(glob.glob(os.path.join(os.environ.get("MAHJONG_LOG_DIR"), "*.svg")), reverse=True)[0]
        mahjong_svg_path_win = convert_path_unix2win(mahjong_svg_path)
        self._obs_handler.set_html("mahjong", mahjong_svg_path_win)

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