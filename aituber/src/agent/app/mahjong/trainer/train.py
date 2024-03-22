import os
import argparse

import pytorch_lightning as pl
from pytorch_lightning import loggers
from pytorch_lightning.callbacks import ModelCheckpoint
import torch
from torch.utils.data import DataLoader, random_split

from dataset import MjxDataModule
from module import Net


def train(args):
    os.makedirs(args.log_dir, exist_ok=True)

    datamodule = MjxDataModule(args.data_dir, args.batch_size)
    model = Net()
    logger = loggers.TensorBoardLogger(args.log_dir)
    model_checkpoint = ModelCheckpoint(
        dirpath=args.log_dir,
        filename="{epoch}-{valid_loss:.4f}",
        monitor="valid_loss",
        save_top_k=1,
        save_last=False,
    )

    pl.seed_everything(42, workers=True)

    if args.gpu and torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    model = model.to(device)
    trainer = pl.Trainer(
        max_epochs=args.max_epochs,
        logger=logger,
        callbacks=[
            model_checkpoint,
        ],
        accelerator=device,
        deterministic=True,
    )
    trainer.fit(
        model=model,
        datamodule=datamodule
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_dir",
        help="Path to data directory",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--log_dir",
        help="Path to log directory",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--batch_size",
        help="Batch size",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--max_epochs",
        help="Maximum number of epochs for training",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--gpu",
        help="Use GPU or not.",
        type=bool,
        default=True,
    )
    args = parser.parse_args()

    train(args)