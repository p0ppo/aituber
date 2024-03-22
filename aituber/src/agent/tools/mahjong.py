import os
import shutil
import dotenv
from typing import Any, Type
from langchain.chains.llm import LLMChain
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate,
    PromptTemplate
)
from langchain.agents import tool
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic.v1 import BaseModel, Field
from ..app.mahjong import (
    MahjongRunner,
    HUMAN_COMPLETION,
    REQUIRE_CHOICE,
    ANSWER_SET,
    ILLEGAL_COMPLETION
)
from ..templates import (
    CHARACTER_PROMPT, 
    MAHJONG_TEMPLATE, 
    MAHJONG_SUFFIX_PROMPT, 
    MAHJONG_LOOKUP_TABLE
)


dotenv.load_dotenv()

class MahjongAgentInput(BaseModel):
    action_type: str = Field(description="""プレイヤーが取る行動です。分からない場合は"***"としてください。""") 
    tile: str = Field(description="""操作する麻雀牌の名称です。分からない場合は"***"としてください。""") 
    is_start: bool = Field(description="""ゲームを開始するかどうかです。開始する場合はTrue、それ以外の場合はFalseとなります。""")
    is_answer: bool = Field(description="""プレイヤーの行動を示しているかどうかです。行動を示している場合はTrue、そうでない場合はFalseとしてください。""")
    canceled: bool = Field(description="""ゲームを終了するかどうかです。終了する場合はTrue、そうでない場合はFalseとしてください。""")

    #is_running: bool = False
    #is_answer_set: bool = False
    #choices: dict = {}
    #answer: str = ""
    #status: int = 0

    #runner: Any = Field(exclude=True, title="runner")
    #runner: Any = Field()

    #def __init__(self, **data):
    #    super().__init__(**data)
    #    print("Loading Mahjong runner...")
    #    self.runner = MahjongRunner()
    #    print("Mahjong runner loaded.")
    
    #class Config:
    #    arbitrary_types_allowed = True

mahjong_agent_input_parser = PydanticOutputParser(
    pydantic_object=MahjongAgentInput
)
mahjong_agent_input_fixing_parser = OutputFixingParser.from_llm(
    parser=mahjong_agent_input_parser, 
    llm=ChatOpenAI()
)

def run_mahjong_agent(args):
    return mahjong_agent.run(tool_input=dict(args))


class MahjongAgent(BaseTool):
    name: str = "mahjong_agent"
    description: str = """
    麻雀アプリの起動、およびそのゲーム進行を担当します。
    """
    args_schema: Type[BaseModel] = MahjongAgentInput

    is_running: bool = False
    is_answer_set: bool = False
    choices: dict = {}
    answer: str = ""
    output: str = ""
    status: int = 0
    runner: Any
    cnt: int = 0

    def __init__(self):
        super().__init__()
        print("Loading Mahjong runner...")
        self.runner = MahjongRunner()
        print("Mahjong runner loaded.")
        if os.path.exists(os.environ.get("MAHJONG_LOG_DIR")):
            shutil.rmtree(os.environ.get("MAHJONG_LOG_DIR"))
        os.makedirs(os.environ.get("MAHJONG_LOG_DIR"))
    
    def reset_agent(self):
        self.is_running = False
        self.is_answer_set = False
        self.choices = {}
        self.answer = ""
        self.output = ""
        self.status = 0
        self.runner = MahjongRunner()
        self.cnt = 0
    
    def error_message(self):
        print(self.choices)
        print(self.output)
        return "すみません、何をすればいいのか分かりませんでした。もう一度別の言い方で試してみてください"
    
    def normalize_tile(self, tile):
        kansuji2num = {
            "一": "1",
            "二": "2",
            "三": "3",
            "四": "4",
            "五": "5",
            "六": "6",
            "七": "7",
            "八": "8",
            "九": "9"
        }
        zenkaku2num = {
            "１": "1",
            "２": "2",
            "３": "3",
            "４": "4",
            "５": "5",
            "６": "6",
            "７": "7",
            "８": "8",
            "９": "9"
        }
        ktile2alpha = {
            "萬": "m",
            "筒": "p",
            "索": "s",
        }
        characters2tile = {
            "東": "ew",
            "南": "sw",
            "西": "ww",
            "北": "nw",
            "白": "wd",
            "發": "gd",
            "中": "rd"
        }
        
        # Convert chinese number to roman
        chinese = False
        if tile[0] in kansuji2num.keys():
            digit = kansuji2num[tile[0]]
            chinese = True
        elif tile[1] in kansuji2num.keys():
            digit = kansuji2num[tile[1]]
            chinese = True
        # Convert zenkaku number to hankaku
        elif tile[0] in zenkaku2num.keys():
            digit = zenkaku2num[tile[0]]
            chinese = True
        elif tile[1] in zenkaku2num.keys():
            digit = zenkaku2num[tile[1]]
            chinese = True
        # Substitute original roman
        elif tile[0].isdigit():
            digit = tile[0]
        elif tile[1].isdigit():
            digit = tile[1]

        # Check if suit is written in chinese character
        if tile[0] in ktile2alpha.keys():
            suit = ktile2alpha[tile[0]]
            chinese = True
        elif tile[1] in ktile2alpha.keys():
            suit = ktile2alpha[tile[1]]
            chinese = True
        
        # Merge
        if chinese:
            tile = suit + digit
        
        # Convert characters tile into mjx notation
        print("Convert enter")
        if tile[0] in characters2tile.keys():
            print("Convert in")
            tile = characters2tile[tile[0]]
            print(tile)

        # Swap if necessary
        # ex. 5m -> m5, 4p -> p4
        if tile[0].isdigit() and tile[1] in ['m', 'p', 's']:
            tile = tile[1] + tile[0]
        return tile

    def _run(
        self,
        action_type: str,
        tile: str,
        is_start: bool,
        is_answer: bool,
        canceled: bool,
        #runner: MahjongRunner,
        #runner: Any,
        #is_running: bool,
        #is_answer_set: bool,
        #choices: dict,
        #answer: str,
        #status: int,
    ) -> str:
        """
        麻雀アプリの起動、およびそのゲーム進行を担当します。
        """
        print(action_type)
        print(tile)
        print(is_start)
        print(is_answer)
        print(canceled)
        if not self.is_running:
            is_start = True
            self.is_answer_set = False
            self.cnt = 0

        # Check if both 'is_start' and 'canceled' are true
        if is_start and canceled:
            if self.is_running:
                canceled = False
            else:
                is_start = False

        if canceled:
            self.reset_agent()
            return "はい。ここでゲームを終了します。"
        
        # Start sequence. Continue until the status become 'REQUIRE_CHOICE'
        if is_start and not self.is_running:
            self.runner.reset()
            self.is_running = True
        
        if self.is_running:
            if self.status == REQUIRE_CHOICE and len(self.choices) != 0:
                #import pdb; pdb.set_trace()
                if is_answer:
                    try:
                        tile = self.normalize_tile(tile)
                    except:
                        return self.error_message()
                    tmp_answer = action_type + "-" + tile
                    candidates = [c for c in self.choices if tmp_answer in c]
                    if len(candidates) != 0:
                        self.answer = candidates[0]
                    elif action_type == "DISCARD":
                        candidates = [c for c in self.choices if "TSUMOGIRI-"+tile in c]
                        if len(candidates) != 0:
                            self.answer = candidates[0]
                        else:
                            return self.error_message()
                    elif action_type == "TSUMOGIRI":
                        candidates = [c for c in self.choices if "DISCARD-"+tile in c]
                        if len(candidates) != 0:
                            self.answer = candidates[0]
                        else:
                            return self.error_message()
                    else:
                        return self.error_message()

                elif action_type != "***" and tile == "***":
                    candidates = [c for c in self.choices if action_type in c]
                    if len(candidates) != 0:
                        self.answer = candidates[0]  # Always choose the first action
                    else:
                        return self.error_message()
                    print(action_type)
                    print(tile)
                    print(candidates)
                elif action_type == "***" and tile != "***":
                    try:
                        tile = self.normalize_tile(tile)
                    except:
                        return self.error_message()
                    candidates = [c for c in self.choices if tile in c]
                    if len(candidates) != 0:
                        self.answer = candidates[0]  # Always choose the first action
                    else:
                        return self.error_message()
                    print(action_type)
                    print(tile)
                    print(candidates)
                elif action_type == "***" and tile == "***":
                    return self.error_message()
                self.status, res = self.runner.set_answer(self.answer)
                if self.status != ANSWER_SET:
                    return self.error_message()
                self.is_answer_set = True

            if self.status == ANSWER_SET:
                self.status, res = self.runner.step(self.cnt)
                print(self.status)
                print(res)
                if self.status == HUMAN_COMPLETION:
                    # Running successfully. Continue.
                    pass
                elif self.status == REQUIRE_CHOICE:
                    # Due to some error, run for human player failed. Back to choosing phase.
                    return self.error_message()
                else:
                    # Unrecognized error
                    raise ValueError("Could not resolve the error in mahjong agent. Exit.")
                self.is_answer_set = False

            if not self.is_answer_set:
                self.status, res = self.runner.step(self.cnt)
                self.cnt += 1
                print(self.status)
                print(res)
                self.choices = res["choices"]
                self.output = res["output"]
                return "あなたの番です。行動を選択してください"
            
            elif self.status == ILLEGAL_COMPLETION:
                return "エラー発生。"
        
        else:
            return "まだ麻雀は始めていません。対局しますか？"


sum_template = PromptTemplate(
    input_variables=["input"],
    template=MAHJONG_TEMPLATE,
    partial_variables={
        "mahjong_lookup_table": MAHJONG_LOOKUP_TABLE, 
        "format_instructions": mahjong_agent_input_parser
    }
)
llm = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo"
)
replace_words_prompt = PromptTemplate(
    input_variables=["input"],
    template=MAHJONG_SUFFIX_PROMPT,
    partial_variables={"character": CHARACTER_PROMPT}
)
llm_chain = LLMChain(
    llm=llm,
    prompt=replace_words_prompt,
)

mahjong_agent = MahjongAgent()
chain = (
    sum_template 
    | llm 
    | mahjong_agent_input_fixing_parser
    | (lambda x: dict(x))
    | mahjong_agent
    | llm_chain
    | (lambda x: x["text"])
)

@tool(return_direct=True)
def run_mahjong_chain(message):
    """Invoke mahjong chain"""
    return chain.invoke({"input": message})


if __name__ == "__main__":
    from langchain.prompts import PromptTemplate

    template = """
    与えた情報から以下を出力してください。
    ただしaction_typeとtileについては情報だけから推測が困難な場合は、
    "***"としてください。
    {info}
    - action_type: ユーザーが取る行動（ツモ切り、手出し、ポン、チー、リーチ、ロン、ツモなど）
    - tile: 行動の対象となる麻雀牌の種類
    - is_start: ゲームを開始する内容のメッセージの場合True、それ以外はFalseとなります。
                「麻雀やりたい」「麻雀始めて」「麻雀スタート」などが開始メッセージの例です。これらはTrueとなります。
    - is_answer: action_typeとtileが両方"***"ではない場合にTrueとなり、それ以外はFalseです。
    - canceled: ゲームを終了する内容のメッセージの場合True、それ以外はFalseとなります。

    action_typeとtileは以下の文字列のみ使用可能です。それ以外の文字列は出力しないでください。
    使用可能な文字列とその文字列に対応するユーザーの入力例を示します。

    action_type:
        - "DRAW"
        例：引き分け
        - "CHI"
        例：チー
        - "PON"
        例：ポン
        - "RIICHI
        例：リーチ
        - "DISCARD"
        例：手出し、切り、捨てるなど
        - "TSUMOGIRI"
        例：ツモ切り、切り、捨てるなど
        - "CLOSED_KAN"
        例：カン、槓、暗槓など
        - "ADDED_KAN"
        例：カン、槓、加槓など
        - "TSUMO"
        例：ツモ
        - "ABORTIVE_DRAW_NINE_TERMINALS"
        例：九種九牌
        - "OPEN_KAN"
        例：カン、槓、明槓など
        - "RON"
        例：ロン
        - "***"
        上記に該当しない入力で推測が困難な場合に使用してください。
    
    以下、"〇"は1~9の任意の数字を表します。
    tile:
        - "m〇"
        例：m〇、〇マン、〇萬、〇萬子など
        - "p〇"
        例：p〇、〇ピン、〇筒、〇筒子など
        - "s〇"
        例：s〇、〇ソー、〇索、〇索子など
        - "ew"
        例：東、トン
        - "sw"
        例：南、ナン
        - "ww"
        例：西、シャー
        - "nw"
        例：北、ペー
        - "wd"
        例：白、ハク
        - "gd"
        例：發、ハツ
        - "rd"
        例：中、チュン
    
    注意事項
    ------------------------
    tileのみが入力として与えられた場合、action_typeは"***"としてください。
    action_typeのみが入力として与えられた場合、tileは"***"としてください。
    tileのうち萬子、筒子、索子は必ずm、p、sが先頭です。
    m1, p4, s8などは正しいですが、3m, 9p, 5sとしてはいけません。
    action_typeとtileは指定の文字列以外は使ってはいけません。
    \n{format_instructions}
    """

    sum_template = PromptTemplate(
        input_variables=["info"],
        template=template,
        partial_variables={"format_instructions": mahjong_agent_input_parser}
    )

    llm = ChatOpenAI(
        temperature=0,
        model="gpt-3.5-turbo"
    )

    from langchain.agents import Tool

    mahjong_agent = MahjongAgent()
    mahjong_tool = [
        Tool.from_function(
            name="mahjong",
            func=mahjong_agent.run,
            description="Mahjong agent"
        )
    ]

    from langchain_core.runnables import RunnableParallel, RunnableLambda

    #chain = LLMChain(llm=llm, prompt=sum_template) | mahjong_agent_input_parser #| mahjong_agent
    chain = (
        sum_template 
        | llm 
        | mahjong_agent_input_fixing_parser
        #| RunnableLambda(lambda x: dict(x))
        | (lambda x: dict(x))
        | mahjong_agent
        #| run_mahjong_agent
        #| mahjong_agent
    ) #| mahjong_agent #| mahjong_agent

    @tool
    def run_mahjong_chain(message):
        """Invoke mahjong chain"""
        return chain.invoke({"info": message})


    from langchain.agents import AgentExecutor, AgentType, initialize_agent
    tool = [run_mahjong_chain]
    #mahjong_executor = AgentExecutor(
    #    agent=AgentType.OPENAI_FUNCTIONS,
    #    tools=tool,
    #    #args_schema=MahjongAgentInput,
    #    verbose=True
    #)
    mahjong_executor = initialize_agent(
        tool,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
    )
    result = mahjong_executor.run("麻雀やりたい")
    #result = chain.invoke({"info": "麻雀やりたい"})
    print(result)
    import pdb; pdb.set_trace()


    #output = chain.run(info="4萬をツモ切り")
    result = chain.invoke({"info": "麻雀やりたい"})
    #resp = mahjong_agent.run(tool_input=dict(result))
    print(result)
    #print(resp)

    import pdb; pdb.set_trace()

    #print(mahjong_agent_input_parser.parse(output))

    #chain = 

#@tool("mahjong_agent", return_direct=True, args_schema=MahjongAgentInput)
#def mahjong_agent(

#class MahjongAgentArgsInput(BaseModel):
#    args: MahjongAgentInput


#@tool("mahjong_agent", return_direct=True, args_schema=MahjongAgentInput)
#def mahjong_agent(
#    canceled: bool,
#) -> str:

#class MahjongAgent(BaseTool):
#    args_schema: Type[BaseModel] = MahjongAgentInput
#    name: str = "mahjong_agent"
#    description: str = """
#    麻雀アプリの起動、およびそのゲーム進行を担当します。
#    """
#    runner: MahjongRunner = None
#    is_answer_set: bool = False
#    choices: dict = {}
#    answer: str = ""
#    status: int = 0
#
#    def __init__(self):
#        super().__init__()
#        print("Loading Mahjong runner...")
#        self.runner = MahjongRunner()
#        #self.is_answer_set = False
#        #self.choices = {}
#        print("Mahjong runner loaded.")
#
#    def _run(self, 
#             action_type: str = "", 
#             tile: str = "", 
#             is_answer: bool = False, 
#             canceled: bool = False
#             ) -> str:
#        print(action_type)
#    #def _run(self, args):
#        #canceled = args["canceled"]
#        #tile = args["tile"]
#        #action_type = args["action_type"]
#        #is_answer = args["is_answer"]
#        if canceled:
#            return "はーい。ここでゲームを終了するよ"
#
#        if is_answer and self.status == REQUIRE_CHOICE and len(self.choices) != 0:
#            self.answer = action_type + "-" + tile
#            self.runner.set_answer(self.answer)
#            self.is_answer_set = True
#
#        # Run step
#        self.status, res = self.runner.step()
#
#        if not self.is_answer_set:
#            self.choices = res["choices"]
#            self.output = res["output_svg"]
#            return "きみの番だよ！さあ、どうする？"
#        
#        elif self.status == ILLEGAL_COMPLETION:
#            return "エラーが起きちゃったみたい。"