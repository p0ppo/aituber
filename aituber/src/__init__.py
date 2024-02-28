import time
from .aituber import AITuber


def launch():
    aituber = AITuber()
    while True:
        try:
            aituber()
            time.sleep(5)
        except Exception as e:
            raise(f"Error occured. {e}")
