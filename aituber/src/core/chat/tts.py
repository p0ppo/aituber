import os
import dotenv
import subprocess
#import winsound


class VoicePeak:
    def __init__(self, player):
    # narrator = "Miyamai Moca"
    # doyaru=0, honwaka=100, angry=0, teary=0
        dotenv.load_dotenv()

        self._exepath = os.environ.get("VOICEPEAK_EXE")
        self._outdir = "./tmp"
        os.makedirs(self._outdir, exist_ok=True)
        self._outpath = os.path.join(self._outdir, "output.wav")

        print(os.environ.get("VOICEPEAK_EMOTION"))
        self._player = player
        self._narrator = os.environ.get("VOICEPEAK_NARRATOR")
        self._emotion = os.environ.get("VOICEPEAK_EMOTION")
        print(self._player)
        print(self._narrator)
        print(self._emotion)
    
    #def _set_emotion(self, **kwargs):
    #    return ",".join([f"{k}={v}" for k, v in kwargs.items()])
    
    def run(self, script: tuple):
        for s in script:
            self._run_core(s)
    
    def _run_core(self, script):
        args_vp = [
            self._exepath,
            "-s", script,
            "-n", self._narrator,
            "-o", self._outpath,
            "-e", self._emotion
        ]
        process = subprocess.Popen(args_vp)
        process.communicate()
        return
    
    def play(self, outpath=None):
        if outpath is None:
            outpath = self._outpath
        if not os.path.isfile(outpath):
            Exception("Output file does not exist. Abort.")

        # Simple soundplayer
        #winsound.PlaySound(outpath, winsound.SND_FILENAME)

        # Sound player using sounddevice
        self._player.play_from_file(outpath)

        # Remove tmp file
        if False:
            self._remove_file(outpath)

    def _remove_file(self, filename):
        os.remove(filename)


if __name__ == "__main__":
    from sound_player import SoundPlayer

    script = "こんにちは"
    #narrator = "Miyamai Moca"
    #emotion = {
    #    "doyaru" : 0,
    #    "honwaka" : 100,
    #    "angry" : 0,
    #    "teary" : 0,
    #}
    #voicepeak(script, narrator, **emotion)
    player = SoundPlayer()
    voicepeak = VoicePeak(player=player)
    voicepeak.run(script)
    voicepeak.play()