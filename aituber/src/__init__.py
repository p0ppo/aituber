import time
import click

from .aituber import AITuber


@click.command(name="launch")
def launch():
    aituber = AITuber()
    while True:
        try:
            aituber()
            time.sleep(5)
        except Exception as e:
            raise(f"Error occured. {e}")
