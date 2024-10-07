## Milestone 2 Template

```
The files are empty placeholders only. You may adjust this template as appropriate for your project.
Never commit large data files,trained models, personal API Keys/secrets to GitHub
```

#### Project Milestone 2 Organization

```
├── Readme.md
├── data # DO NOT UPLOAD DATA TO GITHUB, only .gitkeep to keep the directory or a really small sample
├── notebooks
│   └── eda.ipynb
├── references
├── reports
│   └── Statement of Work_Sample.pdf
├── requirements.txt
└── src
    ├── datapipeline
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── dataloader.py
    │   ├── docker-shell.sh
    │   ├── preprocess.py
    │   └── requirements.txt
    ├── docker-compose.yml
    └── models
        ├── Dockerfile
        ├── docker-shell.sh
        ├── infer_model.py
        ├── model_rag.py
        └── train_model.py

```

# AC215 - Milestone2 - Cheesy App

**Team Members**
Pavlos Parmigianopapas, Pavlos Ricottapapas and Pavlos Gouda-papas

**Group Name**
The Grate Cheese Group

**Project**
In this project, we aim to develop an application that can identify various types of cheese by using AI-powered visual recognition technology. Users can simply take a photo of the cheese, and the app will identify it for them, offering a wealth of information about the cheese.

### Milestone2 ###

We gathered a dataset of 100,000 cheese images representing approximately 1,500 different varieties. Our dataset comes from the following sources—(1), (2), (3) — with approximately 100GB in size. We stored our dataset in a private Google Cloud Bucket.

**Data Pipeline container**
- This container reads 100GB of data and resizes the image sizes and stores it back to GCP
- Input to this container is source and destincation GCS location, parameters for resizing, secrets needed - via docker
- Output from this container stored at GCS location

(1) `src/datapipeline/preprocess.py`  - Here we do preprocessing on our dataset of 100GB, we reduce the image sizes (a parameter that can be changed later) to 128x128 for faster iteration with our process. Now we have dataset at 10GB and saved on GCS. 

(2) `src/datapipeline/requirements.txt` - We used following packages to help us preprocess here - `special cheese package` 

(3) `src/preprocessing/Dockerfile` - This dockerfile starts with  `python:3.11-slim-buster`. This <statement> attaches volume to the docker container and also uses secrets (not to be stored on GitHub) to connect to GCS.

To run Dockerfile - `Instructions here`

**Models container**
- This container has scripts for model training, rag pipeline and inference

- Instructions for running the model container - `Instructions here`


**Notebooks/Reports** 
This folder contains code that is not part of container - for e.g: Application mockup, EDA, any 🔍 🕵️‍♀️ 🕵️‍♂️ crucial insights, reports or visualizations. 

----
You may adjust this template as appropriate for your project.