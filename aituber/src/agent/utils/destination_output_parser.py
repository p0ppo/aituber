from langchain.schema import BaseOutputParser, OutputParserException
from typing import Set
from pydantic.v1 import Extra


class DestinationOutputParser(BaseOutputParser[str]):
  destinations: Set[str]

  class Config:
    extra = Extra.allow

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.destinations_and_default = list(self.destinations) #+ ["DEFAULT"]

  def parse(self, text: str) -> str:
    matched = [int(d in text) for d in self.destinations_and_default]
    if sum(matched) != 1:
      raise OutputParserException(
        f"DestinationOutputParser expected output value includes "
        f"one(and only one) of {self.destinations_and_default}. "
        f"Received {text}."
    )

    return self.destinations_and_default[matched.index(1)]

  @property
  def _type(self) -> str:
    return "destination_output_parser"