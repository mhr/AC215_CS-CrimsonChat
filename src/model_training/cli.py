import os
import argparse
import pandas as pd
import json
import time
import glob
from google.cloud import storage
import vertexai
from vertexai.preview.tuning import sft
from vertexai.generative_models import GenerativeModel, GenerationConfig
from pprint import pprint
from sklearn.model_selection import train_test_split
import random

from google.cloud import aiplatform

GCP_PROJECT = os.environ.get("GCP_PROJECT")
LOCATION = os.environ.get("LOCATION")
MODEL_ENDPOINT = os.environ.get("MODEL_ENDPOINT")
vertexai.init(project=GCP_PROJECT, location=LOCATION)
bucket_name = os.environ.get("BUCKET_NAME")
TRAIN_DATASET = f"gs://{bucket_name}/mental_dataset_TRAIN.jsonl"
VAL_DATASET = f"gs://{bucket_name}/mental_dataset_VAL.jsonl"
TEST_DATASET = f"gs://{bucket_name}/mental_dataset_TEST.jsonl"
GENERATIVE_SOURCE_MODEL = "gemini-1.5-flash-002" # gemini-1.5-pro-002

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../secrets/llm-service-account.json"

generation_config = {
    "max_output_tokens": 3000,  # Maximum number of tokens for output
    "temperature": 0.75,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}

def upload_to_bucket(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def clean():
    # Download and unzip https://www.kaggle.com/datasets/jiscecseaiml/mental-health-dataset
    """
    {'contents': [{'parts': [{'text': 'Can you explain the difference between AI '
                                      'and machine learning?'}],
                   'role': 'user'}],
     'systemInstruction': {'parts': [{'text': 'Welcome to the chat, how can I '
                                              'assist you today?'}],
                           'role': 'system'}}
    """
    new_dataset = []
    systemInstruction = {"parts": [{"text": "Welcome to CrimsonChat, a chat service for stressed out Harvard CS students."}], "role": "system"}
    with open("kaggle_mental_dataset.json", "r") as f:
        dataset = json.loads(f.read())
        for intent in dataset["intents"]:
            for pattern, response in zip(intent["patterns"], intent["responses"]):
                example = {
                    "systemInstruction": systemInstruction,
                    "contents": [{"role": "user", "parts": [{"text": pattern}]},
                                 {"role": "model", "parts": [{"text": response}]}]
                }
                new_dataset.append(example)

    # Split out exactly 256 rows for validation and then use the rest of the data for training and testing
    random.shuffle(new_dataset)
    val = new_dataset[:256]
    remaining_dataset = new_dataset[256:]
    train, test = train_test_split(remaining_dataset, test_size=0.2, random_state=0)  # 80% train, 20% test
    with open("mental_dataset_TRAIN.jsonl", "w") as f:
        for example in train:
            f.write(json.dumps(example) + "\n")
    with open("mental_dataset_VAL.jsonl", "w") as f:
        for example in val:
            f.write(json.dumps(example) + "\n")
    with open("mental_dataset_TEST.jsonl", "w") as f:
        for example in test:
            f.write(json.dumps(example) + "\n")
    upload_to_bucket(bucket_name, "mental_dataset_TRAIN.jsonl", "mental_dataset_TRAIN.jsonl")
    upload_to_bucket(bucket_name, "mental_dataset_VAL.jsonl", "mental_dataset_VAL.jsonl")
    upload_to_bucket(bucket_name, "mental_dataset_TEST.jsonl", "mental_dataset_TEST.jsonl")

# Task 2: finetune on it
def train(wait_for_job=False):
    # Supervised Fine Tuning
    sft_tuning_job = sft.train(
        source_model=GENERATIVE_SOURCE_MODEL,
        train_dataset=TRAIN_DATASET,
        validation_dataset=VAL_DATASET,
        epochs=2, # should be 2-3
        adapter_size=4,
        learning_rate_multiplier=1.0,
        tuned_model_display_name="crimson-chat-v1",
    )
    print("Training job started. Monitoring progress...\n\n")

    # Wait and refresh
    time.sleep(60)
    sft_tuning_job.refresh()
    
    if wait_for_job:
        print("Check status of tuning job:")
        print(sft_tuning_job)
        while not sft_tuning_job.has_ended:
            time.sleep(60)
            sft_tuning_job.refresh()
            print(sft_tuning_job.state)
            print("Job in progress...")

    print(f"Tuned model name: {sft_tuning_job.tuned_model_name}")
    print(f"Tuned model endpoint name: {sft_tuning_job.tuned_model_endpoint_name}")
    print(f"Experiment: {sft_tuning_job.experiment}")

def chat():
    print("chat()")
    # Get the model endpoint from Vertex AI: https://console.cloud.google.com/vertex-ai/studio/tuning?project=ac2215-project
    generative_model = GenerativeModel(f"projects/{GCP_PROJECT}/locations/{LOCATION}/endpoints/{MODEL_ENDPOINT}")

    query = "I'm feeling so sad about my stressful homework. What should I do?"
    print("query: ", query)
    response = generative_model.generate_content(
        [query],  # Input prompt
        generation_config=generation_config,  # Configuration settings
        stream=False,  # Enable streaming for responses
    )
    generated_text = response.text
    print("Fine-tuned LLM Response:", generated_text)

def main(args=None):
    print("CLI Arguments:", args)

    if args.train:
        clean()
        train(wait_for_job=True)

    if args.chat:
        chat()

if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal '--help', it will provide the description
    parser = argparse.ArgumentParser(description="CLI")

    parser.add_argument(
        "--train",
        action="store_true",
        help="Train model",
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Chat with model",
    )

    args = parser.parse_args()

    main(args)
