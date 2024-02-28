import os
import dotenv
import obsws_python as obs


class OBSHandler:
    def __init__(self):
        dotenv.load_dotenv()
        password = os.environ.get("OBS_WS_PASSWORD")
        host = os.environ.get("OBS_WS_HOST")
        port = os.environ.get("OBS_WS_PORT")

        if any([password, host, port]) is None:
            raise Exception("OBS settings are invalid. Abort.")
        
        self.ws = obs.ReqClient(host=host, port=port, password=password)
    
    def set_text(self, source, text):
        self.ws.set_input_settings(
            name=source,
            settings={"text": text},
            overlay=True,
            )


if __name__ == "__main__":
    obs = OBSHandler()
    source = "dialogue"
    text = "こんにちは"
    obs.set_text(source, text)