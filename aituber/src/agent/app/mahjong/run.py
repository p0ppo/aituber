import mjx
from .agent import NetAgent, HumanAgent


HUMAN_COMPLETION = 100
REQUIRE_CHOICE = 101
ANSWER_SET = 102
ILLEGAL_COMPLETION = 103


class MahjongRunner():
    def __init__(self):
        self.env = mjx.MjxEnv()
        self.human_agent = HumanAgent()
        self.net_agent = NetAgent()
        self.agents = {
            "player_0": self.human_agent,
            "player_1": self.net_agent,
            "player_2": self.net_agent,
            "player_3": self.net_agent,
        }
        self.done = False
        #self.reset()

        self.is_answer_obtained = False
        self.answer = None
    
    def reset(self):
        self.obs_dict = self.env.reset()
        return self.obs_dict
    
    def set_answer(self, answer):
        if answer is None:
            return REQUIRE_CHOICE, {"choices": self.choices}
        print(f"Answer set as {answer}")
        self.answer = answer
        self.is_answer_obtained = True
        return ANSWER_SET, {}
    
    def step(self, cnt):
        self.actions = dict()
        #import pdb; pdb.set_trace()
        if not self.done:
            while list(self.obs_dict.keys())[0] != "player_0":
                # Other
                player_id, obs = list(self.obs_dict.items())[0]
                #self.actions[player_id] = self.agents[player_id].act(obs)
                self.obs_dict = self.env.step(
                    {player_id: self.agents[player_id].act(obs)}
                )

            # Player
            player_id, obs = list(self.obs_dict.items())[0]
            if self.is_answer_obtained and self.answer is not None:
                #self.actions[player_id] = self.agents[player_id].act(self.answer)
                #self.obs_dict = self.env.step(self.actions)
                self.obs_dict = self.env.step(
                    {player_id: self.agents[player_id].act(self.answer)}
                )
                self.is_answer_obtained = False
                self.answer = None
                return HUMAN_COMPLETION, {}
            else:
                self.choices, self.output_svg = self.human_agent.get_choices(obs, cnt)
                return REQUIRE_CHOICE, {"choices": self.choices, "output": self.output_svg}