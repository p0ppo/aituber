import os
import sys
#import dotenv
import subprocess
import click

import chainlit as cl
#from langchain.schema.runnable.config import RunnableConfig
#from langchain.schema import StrOutputParser

sys.path.append(os.path.join(os.getcwd(), "aituber/src"))
#sys.path.append("/mnt/d/Streaming/dev/aituber/aituber/src")
from agent import Executor


@cl.on_chat_start
async def on_chat_start():
    #model = ChatOpenAI(streaming=True)
    #prompt = ChatPromptTemplate.from_messages(
    #    [
    #        (
    #            "system",
    #            "You're a very knowledgeable historian who provides accurate and eloquent answers to historical questions.",
    #        ),
    #        ("human", "{question}"),
    #    ]
    #)
    executor = Executor(segment=True, verbose=True)
    cl.user_session.set("executor", executor)


@cl.on_message
async def on_message(message: cl.Message):
    executor = cl.user_session.get("executor")  # type: Runnable
    agent = executor.get_agent()
    #output_parser = StrOutputParser()

    res = await agent.arun(
        message.content,
        callbacks=[cl.LangchainCallbackHandler()],
    )
    print(res)
    await cl.Message(content=res).send()

    #async for chunk in agent.astream(
    #    {"input": message.content},
    #    config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    #    ):
    #    print(chunk)
    #    await msg.stream_token(chunk["messages"][-1].content)
    #    #await msg.stream_token(chunk)

    #await msg.send()


@click.command(name="chat")
def chat():
    project_path = os.environ.get("PROJECT_PATH")
    filename = project_path + "/aituber/src/chat.py"
    cmd = f"chainlit run {filename}".split(" ")
    subprocess.run(cmd)