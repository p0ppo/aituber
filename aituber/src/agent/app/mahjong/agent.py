import os
import dotenv
from typing import List

import torch
from torch import Tensor
import pytorch_lightning as pl
import mjx
from mjx import Agent, Observation, Action
from mjx.visualizer.selector import Selector
from mjx.visualizer.visualizer import MahjongTable
from mjx.visualizer.converter import action_type_en, action_type_ja, get_tile_char
from mjxproto.mjx_pb2 import ActionType
from mjx.open import Open
#from mjxproto import Observation as Observation_proto

from .trainer.module import Net


class NetAgent(Agent):
    def __init__(self):
        super().__init__()
        dotenv.load_dotenv()
        self._setup()
    
    def _setup(self):
        self.model = Net.load_from_checkpoint(
            os.path.join(os.environ.get("PROJECT_PATH"),
                         "aituber/src/agent/app/mahjong/trainer/logs/epoch=0-valid_loss=1.2328.ckpt"
                        )
        )
        self.model.eval()
    
    def act(self, observation: Observation) -> Action:
    #def act(self, feature, mask, legal_actions) -> Action:
        legal_actions = observation.legal_actions()
        if len(legal_actions) == 1:
            return legal_actions[0]
        
        feature = observation.to_features(feature_name="mjx-small-v0")
        with torch.no_grad():
            action_logit = self.model(Tensor(feature.ravel()).to(self.model.device))
        action_proba = torch.sigmoid(action_logit).to("cpu").numpy()
        
        mask = observation.action_mask()
        action_idx = (mask * action_proba).argmax()
        #return action_idx
        return mjx.Action.select_from(action_idx, legal_actions)


class HumanAgent(Agent):  # type: ignore
    def __init__(self, unicode: bool = False, rich: bool = False, ja: bool = False) -> None:
        super().__init__()
        dotenv.load_dotenv()
        self.unicode: bool = unicode
        self.ja: bool = ja
        self.rich: bool = rich

    #def act(self, observation: Observation) -> Action:  # type: ignore
    #    observation.save_svg("test_human.svg")
    #    return Selector.select_from_proto(
    #        observation.to_proto(), unicode=self.unicode, rich=self.rich, ja=self.ja
    #    )

    def make_choice(self, action, i, unicode, ja) -> str:
        if action.type == ActionType.ACTION_TYPE_NO:
            #return (
            #    str(i) + ":" + (action_type_ja[action.type] if ja else action_type_en[action.type])
            #)
            return {(action_type_ja[action.type] if ja else action_type_en[action.type]) : str(i)}

        elif action.type in [
            ActionType.ACTION_TYPE_PON,
            ActionType.ACTION_TYPE_CHI,
            ActionType.ACTION_TYPE_CLOSED_KAN,
            ActionType.ACTION_TYPE_OPEN_KAN,
            ActionType.ACTION_TYPE_ADDED_KAN,
            ActionType.ACTION_TYPE_RON,
        ]:
            open_data = Open(action.open)
            open_tile_ids = [tile.id() for tile in open_data.tiles()]
            #return (
            #    str(i)
            #    + ":"
            #    + (action_type_ja[action.type] if ja else action_type_en[action.type])
            #    + "-"
            #    + " ".join([get_tile_char(id, unicode) for id in open_tile_ids])
            #)
            return {
                (action_type_ja[action.type] if ja else action_type_en[action.type])
                + "-"
                + " ".join([get_tile_char(id, unicode) for id in open_tile_ids]) : str(i)
            }

        else:
            #return (
            #    str(i)
            #    + ":"
            #    + (action_type_ja[action.type] if ja else action_type_en[action.type])
            #    + "-"
            #    + get_tile_char(action.tile, unicode)
            #)
            return {
                (action_type_ja[action.type] if ja else action_type_en[action.type])
                + "-"
                + get_tile_char(action.tile, unicode) : str(i)
            }

    def make_choices(self, legal_actions_proto, unicode, ja) -> List[str]:
        #choices = []
        choices = {}
        for i, action in enumerate(legal_actions_proto):
            #choices.append(self.make_choice(action, i, unicode, ja))
            choices.update(self.make_choice(action, i, unicode, ja))

        return choices

    def get_choices(self, observation: Observation, cnt: int):
        self.table = MahjongTable.from_proto(observation.to_proto())

        legal_actions_proto = []
        for act in self.table.legal_actions:
            legal_actions_proto.append(act.to_proto())

        if (
            legal_actions_proto[0].type == ActionType.ACTION_TYPE_DUMMY
            or len(self.table.legal_actions) == 1
        ):  # 選択肢がダミーだったり一つしかないときは、そのまま返す
            return self.table.legal_actions[0]

        self.choices = self.make_choices(legal_actions_proto, self.unicode, self.ja)
        print(self.choices)
        #output = os.path.join(os.environ.get("MAHJONG_LOG_DIR"), "%06d.svg" % cnt)
        output = os.path.join(os.environ.get("MAHJONG_LOG_DIR"), "%06d.svg" % 0)
        observation.save_svg(output)
        return self.choices, output

    def act(self, action) -> Action:
        #answer = input()
        #idx = int(answer["action"].split(":")[0])
        idx = int(self.choices[action])
        return self.table.legal_actions[idx]