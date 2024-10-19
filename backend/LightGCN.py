import os
import numpy as np
import pandas as pd
from db import mongodb
from libreco.algorithms import LightGCN  # pure data, algorithm LightGCN
from libreco.data import DatasetPure, DataInfo, DatasetFeat
from libreco.data import split_by_ratio
from libreco.evaluation import evaluate
import tensorflow as tf
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

global model
model = None

path ="model"
model_name = "lightgcn"
path_for_rebuild = "saved_model"

def reset_state(name):
    tf.compat.v1.reset_default_graph()
    print("\n", "=" * 30, name, "=" * 30)

def load_lightgcn_model():
    data_info = DataInfo.load(path, model_name)
    lightgcn = LightGCN.load(path, model_name, data_info=data_info)
    return lightgcn

def rebuild_lightgcn_model():
    # new_df = pd.DataFrame(mongodb.find_all("ratings"))
    new_df = pd.read_csv("dataset/ratings.csv")
    data_info = DataInfo.load(path_for_rebuild, model_name)
    reset_state("retrain")
    train_data, data_info_new = DatasetFeat.merge_trainset(new_df, data_info, merge_behavior=True)
    lightgcn = LightGCN(
    task="ranking",
    data_info=data_info_new,
    loss_type="bpr",
    embed_size=768,
    n_epochs=1,
    lr=0.01,
#     batch_size=128,
    num_neg = 1,
    sampler = 'popular',
    device="cpu",
    )
    lightgcn.rebuild_model(path_for_rebuild, model_name)
    lightgcn.fit(
    train_data,
    neg_sampling=True,  # sample negative items for train and eval data
    verbose=2,
    k=5,
    metrics=["loss", "roc_auc", "precision", "recall", "ndcg"],
    )
    # let's clear the folder
    for file in os.listdir(path_for_rebuild):
        os.remove(os.path.join(path_for_rebuild, file))
    # this should be async
    data_info_new.save(path_for_rebuild, model_name)
    lightgcn.save(path_for_rebuild, model_name, manual=True, inference_only=False)
    return lightgcn
    

# Add this function to initialize your LightGCN model
def initialize_lightgcn_model():
    global model
    if os.path.exists("model/") and any(os.listdir("model/")):
        print("Loading existing LightGCN model...")
        model = load_lightgcn_model()
        data_info = DataInfo.load(path, model_name)
        data_info.save(path_for_rebuild, model_name)
        model.save(path_for_rebuild, model_name,manual=True, inference_only=False)
    else:
        # Load the ratings data (from CSV or database)
        ratings = pd.read_csv("dataset/ratings.csv")
        
        # Build the train dataset and data info
        train_data, data_info = DatasetPure.build_trainset(ratings)
        
        # Initialize the LightGCN model
        lightgcn = LightGCN(
            task="ranking",
            data_info=data_info,
            loss_type="bpr",
            embed_size=768,
            n_epochs=3,
            lr=0.01,
            num_neg=1,
            sampler='popular',
            device="cpu",
        )
        print("training the model")
        # Train the model
        lightgcn.fit(
            train_data,
            neg_sampling=True,  # sample negative items for train and eval data
            verbose=2,
            k=5,
            metrics=["loss", "roc_auc", "precision", "recall", "ndcg"],
        )
        
        # Save the model to use in your views or for predictions
        data_info.save(path, model_name)
        lightgcn.save(path, model_name,inference_only=True)
        for file in os.listdir(path_for_rebuild):
            os.remove(os.path.join(path_for_rebuild, file))
        data_info.save(path_for_rebuild, model_name)
        lightgcn.save(path_for_rebuild, model_name,manual=True, inference_only=False)
        model = lightgcn

        print("Model trained and saved")
    # Set up the scheduler
    scheduler = BackgroundScheduler()
    
    # Schedule the model rebuild task
    
    # For every 30 minutes:
    # scheduler.add_job(rebuild_model_task, 'interval', minutes=1)
    
    # For every 7 days:
    scheduler.add_job(rebuild_model_task, 'interval', days=7)
    
    scheduler.start()

    return model

def rebuild_model_task():
    global model
    print(f"Rebuilding model at {datetime.now()}")
    model = rebuild_lightgcn_model()

# Initialize the model
initialize_lightgcn_model()

# You can access the model through this global variable in other parts of your application
# model is now a global variable
