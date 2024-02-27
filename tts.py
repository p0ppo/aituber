import os
import subprocess
import winsound


def voicepeak(script , narrator, **kwargs):
    # narrator = "Miyamai Moca"
    # doyaru=0, honwaka=100, angry=0, teary=0
    exepath = "E:/Program/AHS/voicepeak/VOICEPEAK/voicepeak.exe"
    outdir = "./tmp"
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, "output.wav")

    args_vp = [
        exepath,
        "-s", script,
        "-n", narrator,
        "-o", outpath,
        #"-e", f"happy={happy},sad={sad},angry={angry},fun={fun}"
        "-e", ",".join([f"{k}={v}" for k, v in kwargs.items()])
    ]

    process = subprocess.Popen(args_vp)
    process.communicate()

    winsound.PlaySound(outpath, winsound.SND_FILENAME)

    # Remove tmp file
    os.remove(outpath)

if __name__ == "__main__":
    script = "ごめんね、わたしには指示されたプロンプトというものはわからないんだ。どうせなら楽しい話でもしようよ！"
    narrator = "Miyamai Moca"
    emotion = {
        "doyaru" : 0,
        "honwaka" : 100,
        "angry" : 0,
        "teary" : 0,
    }
    voicepeak(script, narrator, **emotion)