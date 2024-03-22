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
    
    def set_html(self, source , path):
        # Assuming there's visible html window on OBS
        # The following command is refreshing the cache of it
        # FIXME: Require scene transition function 
        # from normal chat layout to html embedded layout
        self.ws.press_input_properties_button(
            input_name=source, 
            prop_name="refreshnocache"
            )
        #self.ws.set_input_settings(
        #    name=source,
        #    settings={
        #        "local file": path, 
        #        #"restart_when_active": True
        #    },
        #    overlay=True,
        #)


if __name__ == "__main__":
    obs = OBSHandler()
    source = "dialogue"
    text = "こんにちは"
    obs.set_text(source, text)