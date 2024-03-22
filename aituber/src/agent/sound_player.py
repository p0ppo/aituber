import sounddevice as sd
import soundfile as sf


class SoundPlayer:
    def __init__(self):

        # Do not change
        self._output_device = "CABLE Input"

        #self._output_device_id = self._search_id(self._output_device)
        self._output_device_id = 1
        self._input_device_id = 0

        sd.default.device = [
            self._input_device_id,
            self._output_device_id,
        ]
    
    def _search_id(self, device, host_api=0):
        devices_list = sd.query_devices()
        device_id = None

        for d in devices_list:
            is_device = device in d["name"]
            is_host_api = host_api == d["hostapi"]

            if is_device and is_host_api:
                device_id = d["index"]
                break
        
        if device_id is None:
            Exception(f"Could not find device: {device}. Abort.")
        
        return device_id
        
    def play(self, data, samplerate):
        sd.play(data, samplerate)
        sd.wait()
        return True
    
    def play_from_file(self, filename):
        data, samplerate = sf.read(filename)
        return self.play(data, samplerate)