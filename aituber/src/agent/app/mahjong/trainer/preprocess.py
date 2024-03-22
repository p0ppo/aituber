import os
import glob
from tqdm import tqdm

import numpy as np
from mjx import Observation, State, Action 


def convert_mjlog(mjlog_files, feature_path, action_path):
    cnt = 0
    for mjlog in tqdm(mjlog_files):
        with open(mjlog) as f:
            lines = f.readlines()

        for line in lines:
            state = State(line)
            for cpp_obs, cpp_act in state._cpp_obj.past_decisions():
                obs = Observation._from_cpp_obj(cpp_obs)
                feature = obs.to_features(feature_name="mjx-small-v0")

                action = Action._from_cpp_obj(cpp_act)
                action_idx = action.to_idx()

                np.save(os.path.join(feature_path, "%06d.npy" % cnt), feature.ravel())
                np.save(os.path.join(action_path, "%06d.npy" % cnt), action_idx)
                cnt += 1


if __name__ == "__main__":
    mjlog_path = "/mnt/d/Streaming/dev/tenhou/mjx_out"
    feature_path = "/mnt/d/Streaming/dev/tenhou/data/feature"
    action_path = "/mnt/d/Streaming/dev/tenhou/data/action"
    os.makedirs(feature_path, exist_ok=True)
    os.makedirs(action_path, exist_ok=True)

    mjlog_files = sorted(glob.glob(os.path.join(mjlog_path, "*.json")))
    convert_mjlog(mjlog_files, feature_path, action_path)
