## Milestone 2: CS-CrimsonChat

# Table of Contents
1. [Project Milestone 2 Organization](#project-milestone-2-organization)
2. [AC215 - Milestone2 - CS-CrimsonChat App](#ac215---milestone2---cs-crimsonchat-app)
   - [Team Members](#team-members)
   - [Group Name](#group-name)
   - [Project](#project)
   - [Milestone2](#milestone2)
3. [Setup](#setup)
4. [Static Data Pipeline: src/data-pipeline](#static-data-pipeline-srcdata-pipeline)
   - [1. Edit `.env.dev` file](#1-edit-envdev-file)
   - [2. Inside your GCP Create a Bucket and a folder `static-data`](#2-inside-your-gcp-create-a-bucket-and-a-folder-static-data)
   - [3. Run Docker Container](#3-run-docker-container)
   - [4. Set up DVC](#4-set-up-dvc)
     - [Initialize Data Registry](#initialize-data-registry)
     - [Add Remote Registry to GCS Bucket (For Data)](#add-remote-registry-to-gcs-bucket-for-data)
   - [5. Run Docker Container](#5-run-docker-container)
   - [6. Run Codes Inside Container](#6-run-codes-inside-container)
     - [Push the new data to GCP Bucket](#push-the-new-data-to-gcp-bucket)
   - [7. Outside of Container](#7-outside-of-container)
     - [Update Git to track DVC](#update-git-to-track-dvc)
     - [When to Use Git Tags](#when-to-use-git-tags)
     - [When Not to Use Git Tags](#when-not-to-use-git-tags)
5. [Dynamic Data Pipeline: src/data-pipeline-dynamic](#dynamic-data-pipeline-srcdata-pipeline-dynamic)
   - [1. Edit `.env.dev` file](#1-edit-envdev-file-1)
   - [2. Inside your GCP Bucket create a folder `dynamic-data`](#2-inside-your-gcp-bucket-create-a-folder-dynamic-data)
   - [3. Run Docker Container](#3-run-docker-container-1)
   - [4. Set up DVC](#4-set-up-dvc-1)
     - [Initialize Data Registry](#initialize-data-registry-1)
     - [Add Remote Registry to GCS Bucket (For Data)](#add-remote-registry-to-gcs-bucket-for-data-1)
   - [5. Run Codes Inside Container](#5-run-codes-inside-container-1)
     - [Push the new data to GCP Bucket](#push-the-new-data-to-gcp-bucket-1)
   - [6. Outside of Container](#6-outside-of-container-1)
     - [Update Git to track DVC](#update-git-to-track-dvc-1)
     - [When to Use Git Tags](#when-to-use-git-tags-1)
     - [When Not to Use Git Tags](#when-not-to-use-git-tags-1)
6. [Embedding and Inserting into Vector Database: src/vector_database](#embedding-and-inserting-into-vector-database-srcvector_database)
   - [Requirements](#requirements)
   - [How It Works](#how-it-works)
   - [Input JSON Schema](#input-json-schema)
   - [Configuration](#configuration)
     - [Configuration Arguments](#configuration-arguments)
   - [Running the Container](#running-the-container)
   - [Using the CLI](#using-the-cli)
   - [Secrets Management: env.dev & secrets folder](#secrets-management-envdev--secrets-folder)
7. [Model Training Pipeline: src/model_training](#model-training-pipeline-srcmodel_training)
   - [Overview](#overview)
   - [Dependencies](#dependencies)
   - [Usage](#usage)
   - [Secrets and Environment Variables](#secrets-and-environment-variables)
     - [Setting Up Environment Variables](#setting-up-environment-variables)
8. [RAG Pipeline: src/rag_pipeline](#rag-pipeline-srcrag_pipeline)
   - [Overview](#overview-1)
   - [Dependencies](#dependencies-1)
   - [Configuration](#configuration-1)
   - [Usage](#usage-1)
   - [Secrets and Environment Variables](#secrets-and-environment-variables-1)
     - [Setting Up Environment Variables](#setting-up-environment-variables-1)

#### Project Milestone 2 Organization

```
.
├── LICENSE
├── README.md
├── notebooks
│   └── embed_and_insert_vectordb_crimsonchat_1008.ipynb
├── references
├── reports
└── src
    ├── data-pipeline
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── cli.py
    │   ├── data
    │   │   ├── harvard_cs_filtered_links.json
    │   │   ├── harvard_cs_links_by_depth_0.json
    │   │   ├── harvard_cs_links_by_depth_1.json
    │   │   └── scraped_data_harvard_test.json
    │   ├── docker-entrypoint.sh
    │   ├── docker-shell.sh
    │   ├── filter_links.py
    │   ├── gcp_static_data
    │   ├── gcp_static_data.dvc
    │   ├── scrape_content_scrapy.py
    │   └── scrape_links.py
    ├── data-pipeline-dynamic
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── data
    │   │   ├── dynamic_events_1.json
    │   │   ├── processed_dynamic_events_1.json
    │   │   └── processed_google_doc_content.json
    │   ├── docker-entrypoint.sh
    │   ├── docker-shell.sh
    │   ├── dynamic_1.py
    │   ├── dynamic_google_doc.py
    │   ├── gcp_dynamic_data
    │   └── gcp_dynamic_data.dvc
    ├── model_training
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── cli.py
    │   ├── docker-entrypoint.sh
    │   ├── docker-shell.sh
    │   ├── env.dev
    │   ├── kaggle_mental_dataset.json
    │   ├── mental_dataset_TEST.jsonl
    │   ├── mental_dataset_TRAIN.jsonl
    │   └── mental_dataset_VAL.jsonl
    ├── rag_pipeline
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── cli.py
    │   ├── config.txt
    │   ├── docker-entrypoint.sh
    │   ├── docker-shell.sh
    │   ├── env.dev
    │   ├── sample.json
    │   ├── test_gcp_locally.py
    │   └── utils
    │       ├── chunker_utils.py
    │       ├── config_utils.py
    │       ├── embedding_utils.py
    │       ├── json_utils.py
    │       ├── qdrant_utils.py
    │       ├── semantic_splitter.py
    │       └── simple_text_splitter.py
    └── vector_database
        ├── Dockerfile
        ├── Pipfile
        ├── Pipfile.lock
        ├── cli.py
        ├── config.txt
        ├── docker-entrypoint.sh
        ├── docker-shell.sh
        ├── env.dev
        ├── requirements.txt
        └── utils
            ├── chunker_utils.py
            ├── config_utils.py
            ├── embedding_utils.py
            ├── json_utils.py
            ├── qdrant_utils.py
            ├── semantic_splitter.py
            └── simple_text_splitter.py
```

This is 15 directories containing 72 files. (Generated using the `tree` command.)

# AC215 - Milestone2 - CS-CrimsonChat App

**Team Members**
Artem Dinh, Sukanya Krishna, Riley Li, Matthew Retchin

**Group Name**
CS-CrimsonChat

**Project**
This project aims to develop an AI chatbot for Harvard CS students, designed to answer questions about academic and extracurricular activities using data from Harvard websites. The system will employ a RAG+LLM architecture with a vector database, featuring a continuous data pipeline from Harvard CS sources, cloud-based storage and processing, and a user-friendly interface with authentication. The chatbot will provide information on courses, events, degree requirements, and faculty. 

### Milestone2 ###
In this milestone, we have the components for data management, including versioning, as well as the Retrieval Augmented Generation and fine-tuned language model.

## Setup

1. Clone the repository.
2. Set up your environment variables.
3. Ensure you have the necessary credentials for Google Cloud services (e.g., `llm-service-account.json`).

Each individual pipeline documentation section will contain more detailed instructions.

## Static Data Pipeline: src/data-pipeline

### 1. Edit `.env.dev` file

### 2. Inside your GCP Create a Bucket and a folder `static-data`

### 3. Run Docker Container

Go to a terminal inside `data-pipeline`

Run docker container by using:

```bash
sh docker-shell.sh
```

### 4. Set up DVC

#### Initialize Data Registry

In this step we create a data registry using DVC

```bash
dvc init
```

If it says "cannot run without git", run `git init` then run `dvc init` again

#### Add Remote Registry to GCS Bucket (For Data)

```bash
dvc remote add -d <RAMDOM REMOTE NAME> gs://<GCP_BUCKET_NAME>/<FOLDER_NAME>
dvc pull
```

### 5. Run Docker Container

Go to a terminal inside `data-pipeline`

Run docker container by using:

```bash
sh docker-shell.sh
```

### 6. Run Codes Inside Container

1. Scrape all the links under the domain `seas.harvard.edu`

   ```bash
   python cli.py --scrape_links
   ```

2. Filter links

   ```bash
   python cli.py --filter_links
   ```

3. Scrape the text content with scrapy

   ```bash
   python cli.py --scrape_content
   ```

The processed scraped data will be saved to `/data` for viewing locally and `/gcp_static_data` ready to be pushed to GCP bucket.

#### Push the new data to GCP Bucket

```bash
dvc add gcp_static_data
dvc push
```

### 7. Outside of Container

#### Update Git to track DVC

Run this outside the container.

- First run git status `git status`
- Add changes `git add .`
- Commit changes `git commit -m 'dataset updates...'`
- Add a dataset tag `git tag -a 'dataset_v20' -m 'tag dataset'`
- Push changes `git push --atomic origin main dataset_v20`
  It's not mandatory to tag every time before you `dvc add` and `dvc push`, but **tagging is helpful** when you want to mark specific data versions for easy access later.

### When to Use Git Tags:

1. **Major Milestones:**
   You should use **Git tags** for major milestones, like when you have reached a significant version of your data that you might want to retrieve later.

   For example:

   - After completing a major scraping session or data update.
   - After pre-processing or cleaning a dataset.
   - Before conducting a large analysis or model training run.

   **Example:**

   ##### Update Git to track DVC changes (again remember this should be done outside the container)

   - First run git status `git status`
   - Add changes `git add .`
   - Commit changes `git commit -m 'dataset updates...'`
   - Add a dataset tag `git tag -a 'dataset_v21' -m 'tag dataset'`
   - Push changes `git push --atomic origin main dataset_v21`

   By doing this, you'll have a clear marker (tag) to reference that specific version.

#### When Not to Use Git Tags:

**Every Minor Update:**
You don't need to tag **every minor update** unless it's a major milestone in your project. For smaller changes, you can simply commit them to Git and continue versioning with `dvc add`, `git commit`, and `dvc push` as usual. The Git commit history itself will track changes without needing a tag for each.

**Example (minor updates):**

```bash
# Add new data or changes

git commit -m "Updated dataset with recent scraping"

# Push data and commit to remote
git push
```

In summary:

- **Tag** before significant or major updates to easily reference important versions.
- For regular updates, just use **Git commits** without tagging.
- When ready to share or finalize a version of your data, consider using `git tag` to mark that point.

## Dynamic Data Pipeline: src/data-pipeline-dynamic

### 1. Edit `.env.dev` file

### 2. Inside your GCP Bucket create a folder `dynamic-data`

### 3. Run Docker Container

Go to a terminal inside `data-pipeline`

Run docker container by using:

```bash
sh docker-shell.sh
```

### 4. Set up DVC

#### Initialize Data Registry

In this step we create a data registry using DVC

```bash
dvc init
```

If it says "cannot run without git", run `git init` then run `dvc init` again

#### Add Remote Registry to GCS Bucket (For Data)

```bash
dvc remote add -d <RAMDOM REMOTE NAME> gs://<GCP_BUCKET_NAME>/<FOLDER_NAME>
dvc pull
```

### 5. Run Codes Inside Container

Scrape events from [Harvard SEAS
Events](https://events.seas.harvard.edu/calendar)

```bash
python dynamic_1.py
```

Scrape events from [Harvard Theory of Computing Seminar](https://docs.google.com/document/d/1qBfsiK-NNe_dMIsShMSiJe5_Qsc2tmYJMSVzbsMw0RI/edit#heading=h.6c0r0a61enx8)

```bash
python dynamic_google_doc.py
```

The proccessed scraped data will be saved to `/data` for viewing locally and `/gcp_dynamic_data` ready to be pushed to GCP bucket

#### Push the new data to GCP Bucket

```bash
dvc add gcp_dynamic_data
dvc push
```

### 6. Outside of Container

#### Update Git to track DVC

Run this outside the container.

- First run git status `git status`
- Add changes `git add .`
- Commit changes `git commit -m 'dataset updates...'`
- Add a dataset tag `git tag -a 'dataset_v20' -m 'tag dataset'`
- Push changes `git push --atomic origin main dataset_v20`
  It's not mandatory to tag every time before you `dvc add` and `dvc push`, but **tagging is helpful** when you want to mark specific data versions for easy access later.

### When to Use Git Tags:

1. **Major Milestones:**
   You should use **Git tags** for major milestones, like when you have reached a significant version of your data that you might want to retrieve later.

   For example:

   - After completing a major scraping session or data update.
   - After pre-processing or cleaning a dataset.
   - Before conducting a large analysis or model training run.

   **Example:**

   ##### Update Git to track DVC changes (again remember this should be done outside the container)

   - First run git status `git status`
   - Add changes `git add .`
   - Commit changes `git commit -m 'dataset updates...'`
   - Add a dataset tag `git tag -a 'dataset_v21' -m 'tag dataset'`
   - Push changes `git push --atomic origin main dataset_v21`

   By doing this, you'll have a clear marker (tag) to reference that specific version.

#### When Not to Use Git Tags:

**Every Minor Update:**
You don't need to tag **every minor update** unless it's a major milestone in your project. For smaller changes, you can simply commit them to Git and continue versioning with `dvc add`, `git commit`, and `dvc push` as usual. The Git commit history itself will track changes without needing a tag for each.

**Example (minor updates):**

```bash
# Add new data or changes

git commit -m "Updated dataset with recent scraping"

# Push data and commit to remote
git push
```

#### When Not to Use Tags:

You don't need to tag every single minor data update unless you need to quickly reference a particular version later. Use regular Git commits for small changes or incremental updates. Tags are for **important points** in your project when you want to remember a particular version of the data.

#### Tag Summary

- **Tag** before significant or major updates to easily reference important versions.
- For regular updates, just use **Git commits** without tagging.
- When ready to share or finalize a version of your data, consider using `git tag` to mark that point.

## Embedding and Inserting into Vector Database: src/vector_database
**Container Purpose**
This container specifically handles the embedding of plaintext documents. It processes JSON-formatted text data, chunks the documents, generates embeddings for these chunks using Vertex AI, and uploads the embedded chunks along with their metadata to a Qdrant vector database.

### Requirements
1. Qdrant Cloud vector storage
2. Google Cloud Platform access key with permissions for:
   a. GCP storage - buckeet (containing JSON dataset in required format)
   b. GCP Vertex AI - with API enabled

### How It Works
1. Configuration Loading\
2. Document Loading from GCP bucket\
3. Batch Document Processing\
a. Document Chunking (simple or semantic)\
b. Embedding Generation using Vertex AI\
c. Vector Storage in Qdrant database

### Input JSON Schema
We process plaintext documents stored in JSON format. The JSON file must be hosted on a Google Cloud Platform (GCP) bucket and follow this structure:

```json
{
  "URL1": {
    "text_content": "string",
    "metadata": {
      "last_modified": "ISO 8601 datetime string or null",
      "scraped_at": "ISO 8601 datetime string or null",
      "word_count": integer or null
    }
  },
  // ... more key-value pairs with url as key and dictionary as value
}
```

### Configuration
The container supports configuration through:
1. Command-line arguments
2. Configuration file (`config.txt`)

**Configuration Arguments**
The container supports the following configuration arguments:\\
`--config: Path to the configuration file`\
`--testing_json: Path to JSON file for testing`\
`--embedding_model: Model name for Vertex AI embedder`\
`--chunking_method: Chunking method (choices: "simple" or "semantic")`\
`--qdrant_collection: Name of the Qdrant collection`\
`--vector_dim: Vector dimension`\
`--bucket_file_path: Path for JSON file in bucket`\
For semantic chunking:\
`--breakpoint_threshold_type: Breakpoint threshold type for semantic chunking`\
`--buffer_size: Buffer size for semantic chunking`
`--breakpoint_threshold_amount: Breakpoint threshold amount for semantic chunking`\
For simple chunking:\
`--chunk_size: Chunk size for simple chunking`\
`--chunk_overlap: Chunk overlap for simple chunking`\
Note: The `--query` argument is parsed but not applicable for this container's embedding and vector storage operations.


### Running the Container
**Before running the Docker container:**
1. Update the env.dev file in the src/vector_database directory with your specific configurations.
2. Double-check that the path to the secrets folder is correct in your env.dev file. The typical path looks like this:
`GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/../../secrets/crimsonchat.json`
Ensure this path correctly points to your crimsonchat.json file.

**To build and run the Docker container:**
1. Navigate to the `vector_database` directory
2. Run the following command:
`sh docker-shell.sh`

This script will build the Docker image and start the container.
Note: Before running the script, make sure to check if the container is already running. If so, stop container before running `docker-shell.sh`

### Using the CLI

Basic usage:
```
python cli.py --config config.txt
```
Example without config.txt file
```
python cli.py --testing_json /path/to/test.json --embedding_model textembedding-gecko@001 --chunking_method simple --qdrant_collection milestone_2 --chunk_size 1000 --chunk_overlap 200
```

### Secrets Management: env.dev & secrets folder
The container uses environment variables for managing secrets and sensitive configuration. These are stored in a `env.dev` file. 
The following environment variables must be set in the env.dev file:
```
export BASE_DIR=$(pwd) # your current directory
export SECRETS_DIR=$(pwd)/../../../secrets/ # secrets folder location with respect to your current directory
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/my_gcp_key.json
export GCP_PROJECT=YOUR_GCP_PROJECT_ID
export LOCATION=YOUR_GCP_REGION
export BUCKET_NAME=YOUR_GCS_BUCKET_NAME
export QDRANT_URL=YOUR_QDRANT_URL
export QDRANT_API_KEY=YOUR_QDRANT_API_KEY
```
Ensure you replace the placeholder values (YOUR_GCP_PROJECT_ID, YOUR_GCP_REGION, etc.) with your actual configuration details.
The GOOGLE_APPLICATION_CREDENTIALS variable should point to the location of your GCP service account key file. The path shown assumes the variable is being accessed from within container.

**Models container**
- This container has scripts for model training and inference.
- Instructions for running the model container - `Instructions here`
**Notebooks/Reports**
This folder contains code that is not part of container.

## Model Training Pipeline: src/model_training

This container implements a Retrieval-Augmented Generation (RAG) pipeline for processing a single query, performing retrieval, and generating responses using a language model.

### Overview

The Model Pipeline provides a framework for:
1. Finetuning the Google Gemini Flash-1.5 model on a small but sufficient mental health dataset from Kaggle.
2. Generating responses using the language model (LLM) to test that the finetuning was successful.

### Dependencies

To run a container that will automatically install all dependencies required for the project, you can run `docker-shell.sh`, which will automatically build the Docker image under the name rag_pipeline and run the container:

```
./docker-shell.sh
```

### Usage

Run the main script for training:

```
python cli.py --train
```

1. After finetuning, go to the Model Registry: https://console.cloud.google.com/vertex-ai/models?project=YOUR-PROJECT-NAME-HERE (substitute in your actual project name, see below at the environmental variables) and validate that the job has succeeded.
2. Click the successful model, named `crimson-chat-v1`, and then click `Deploy & Test` and `Deploy to Endpoint`.
3. Now copy your model's ID and place it in your env.dev file. Execute env.dev to make sure the environment has access to the endpoint: `source env.dev`.

For an inference test after training:

```
python cli.py --chat
```

A screenshot of the finetuned model instance running at an endpoint is included in src/model_training

### Secrets and Environment Variables

The Model Training pipeline uses environment variables to manage secrets and global configuration. This approach keeps sensitive information out of the codebase and allows for easy configuration across different environments.

#### Setting Up Environment Variables

1. Create a `env.dev` file in the src/model_training directory.
2. Add your environment-specific variables to this file. For example:

```
#!/bin/bash

export BASE_DIR=$(pwd) # your current directory
export SECRETS_DIR=$(pwd)/../../../secrets/ # secrets folder location with respect to your current directory

export LOCATION=YOUR_GCP_REGION

export GCP_PROJECT=YOUR_GCP_PROJECT_ID
export GOOGLE_APPLICATION_CREDENTIALS=/secrets/my_gcp_key.json
export GCP_SERVICE_ACCOUNT=YOUR_GCP_SERVICE_ACCOUNT
export BUCKET_NAME=YOUR_GCS_BUCKET_NAME

export MODEL_ENDPOINT="YOUR_MODEL_ID"
```

Using your specific service account key and project name for the credentials.

## RAG Pipeline: src/rag_pipeline

This container implements a Retrieval-Augmented Generation (RAG) pipeline for processing a single query, performing retrieval, and generating responses using a language model.

### Overview

The RAG Pipeline provides a flexible framework for:
1. Receiving user queries
2. Performing document retrieval from a Qdrant vector database
3. Generating responses using a language model (LLM)

It supports different chunking methods, embedding models, and is designed for various RAG experiments.

### Dependencies

This pipeline relies on several Python libraries. The dependencies are managed through a 'Pipfile' to ensure consistency across environments. The 'Pipfile' includes both essential and development packages that are installed when running the container or the project locally.

To run a container that will automatically install all dependencies required for the project, you can run 'docker-shell.sh' which will automatically build the Docker image under the name rag_pipeline and run the container:

```
./docker-shell.sh
```

### Configuration

The project uses a combination of configuration files and command-line arguments. You can specify configuration options in a `config.txt` file or override them using command-line arguments.

Example `config.txt`:
```
testing_json = ./sample.json
embedding_model = text-embedding-004
vector_dim = 256
chunking_method = simple
qdrant_collection = ms2-production_v256_te004
chunk_size = 200
chunk_overlap = 20
breakpoint_threshold_type = percentile
buffer_size = 1
breakpoint_threshold_amount = 95
```

### Usage

Run the main script with various options:

1. Using a config file:
   ```
   python cli.py --config config.txt
   ```

2. Overriding config values:
   ```
   python cli.py --config config.txt --embedding_model textembedding-gecko@002
   ```

3. Using semantic chunking:
   ```
   python cli.py --config config.txt --chunking_method semantic --breakpoint_threshold_type cosine --buffer_size 5 --breakpoint_threshold_amount 0.3
   ```

4. Using all command-line arguments:
   ```
   python cli.py --testing_json /path/to/test.json --embedding_model textembedding-gecko@001 --chunking_method simple --qdrant_collection milestone_2 --chunk_size 1000 --chunk_overlap 200
   ```

### Secrets and Environment Variables

The RAG Pipeline uses environment variables to manage secrets and global configuration. This approach keeps sensitive information out of the codebase and allows for easy configuration across different environments.

#### Setting Up Environment Variables

1. Create a `env.dev` file in the src/rag_pipeline folder.
2. Add your environment-specific variables to this file, including the endpoint for the model we finetuned. For example:

   ```
   export GCP_PROJECT=your_gcp_project
   export LOCATION=your_location
   export QDRANT_URL=your_qdrant_url
   export QDRANT_API_KEY=your_qdrant_api_key
   export GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
   export MODEL_ENDPOINT="YOUR_MODEL_ID"
   ```
