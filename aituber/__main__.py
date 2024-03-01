from .cli import main
from .src import launch
from .src.rag import vectorize


if __name__ == "__main__":
    main.add_command(launch)
    main.add_command(vectorize)
    main()