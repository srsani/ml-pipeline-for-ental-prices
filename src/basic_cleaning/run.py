#!/usr/bin/env python
"""
Performs basic cleaning on the data and save the results in Weights & Biase
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    logger.info(f"Downloading artifact: {args.input_artifact}")
    artifact_path = run.use_artifact(args.input_artifact).file()

    # load df
    df = pd.read_csv(artifact_path)
    logger.info(f"df shape: {df.shape}")

    # drop outliers
    logger.info("dropping outliers")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    # properties in and around NYC
    idx = df['longitude'].between(-74.25, -
                                  73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    # convert last_review to datetime
    logger.info("converting last_review to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])

    # save cleaned data
    logger.info(f"saving cleaned data to: {args.output_artifact}")
    df.to_csv(args.output_artifact, index=False)

    # logging artifact to W&B
    logger.info(f"logging artifact {args.output_artifact}")
    artifact = wandb.Artifact(
        name=args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(args.output_artifact)

    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This steps cleans the data")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="input artifact name",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="name for the output artifact clean_sample.csv",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="type of output_artifact",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="description of the output",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="minimum price to consider",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="maximum price to consider",
        required=True
    )

    args = parser.parse_args()

    go(args)
