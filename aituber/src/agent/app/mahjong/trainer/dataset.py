import os
import glob
from typing import Optional

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, random_split
import pytorch_lightning as pl


class MjxDataset(Dataset):
    def __init__(self, data_dir):
        self._data_dir = data_dir
        feature_dir = os.path.join(self._data_dir, "feature")
        action_dir = os.path.join(self._data_dir, "action")

        self._feature_list = sorted(glob.glob(os.path.join(feature_dir, "*.npy")))
        self._action_list = sorted(glob.glob(os.path.join(action_dir, "*.npy")))
    
    def __len__(self):
        return len(self._feature_list)
    
    def __getitem__(self, idx):
        feature = np.load(self._feature_list[idx])
        action = np.load(self._action_list[idx])
        return feature, action


class MjxDataModule(pl.LightningDataModule):
    def __init__(self, data_dir: str, batch_size: int):
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
    
    def setup(self, stage: Optional[str]=None):
        mjx_dataset = MjxDataset(self.data_dir)

        n_samples = len(mjx_dataset)
        test_size = int(n_samples * 0.2)
        valid_size = int(n_samples * 0.1)
        train_size = n_samples - test_size - valid_size
        self.train_dataset, self.val_dataset, self.test_dataset = random_split(
            mjx_dataset, [train_size, valid_size, test_size]
        )
    
    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, num_workers=11)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.batch_size, num_workers=11)

    def test_dataloader(self):
        return DataLoader(self.test_dataset, batch_size=self.batch_size, num_workers=0)