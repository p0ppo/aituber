import click
from .src import broadcast, chat
from .src.rag import vectorize

@click.group()
def main():
    pass

main.add_command(broadcast)
main.add_command(chat)
main.add_command(vectorize)