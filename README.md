# Milestone 4: CS-CrimsonChat

## Project Milestone 4 Organization

```
├── Readme.md
├── data # DO NOT UPLOAD DATA TO GITHUB, only .gitkeep to keep the directory or a really small sample
├── notebooks
│   └── eda.ipynb
├── references
├── reports
│   ├── CheesyAppMidterm.pdf
│   └── Statement of Work_Sample.pdf  #This is Milestone1 proposal
└── src
    ├── api-service
    ├── datapipeline
    │   ├── Dockerfile
    │   ├── Pipfile
    │   ├── Pipfile.lock
    │   ├── dataloader.py
    │   ├── docker-shell.sh
    │   ├── preprocess_cv.py
    │   └── preprocess_rag.py
    ├── docker-compose.yml
    ├── frontend
    ├── models
    │   ├── Dockerfile
    │   ├── docker-shell.sh
    │   ├── infer_model.py
    │   ├── model_rag.py
    │   └── train_model.py
    └── workflow
```

# AC215 - Milestone3 - Cheesy App

## Team Members
- Pavlos Parmigianopapas
- Pavlos Ricottapapas 
- Pavlos Gouda-papas

## Group Name
The CrimsonChat Group

## Project
This project aims to develop an AI chatbot for Harvard CS students, designed to answer questions about academic and extracurricular activities using data from Harvard websites. The system will employ a RAG+LLM architecture with a vector database, featuring a continuous data pipeline from Harvard CS sources, cloud-based storage and processing, and a user-friendly interface with authentication. The chatbot will provide information on courses, events, degree requirements, and faculty.

## Milestone4
In this milestone, we have the components for frontend, API service, also components from previous milestones for data scraping, embedding and storing in Qdrant Cloud vector database with versioning, and fine-tuning of VertexAI LLM model.

We integrated LLM and RAG pipeline to answer user queries from Frontend with conversation memory for continous and natural conversation. Frontend also integrated notes feature, which enables users to highlight text or reference urls and store them as notes.

## Application Design
Before we start implementing the app we built a detailed design document outlining the application's architecture. We built a Solution Architecture and Technical Architecture to ensure all our components work together.

### Solution Architecture:
![This solution architecture diagram illustrates the end-to-end workflow of CrimsonChat, encompassing AI/ML tasks, embedding pipelines, and interaction through a frontend application](images/sol_arch.png)

### Technical Architecture:
![The technical architecture diagram outlines the deployment and operational setup of CrimsonChat, leveraging GCP services, containerized components, and Vertex AI for data processing, model training, and deployment](images/tech_arch.png)

## Backend API
This backend serves as an API framework for a chatbot and note-management system, leveraging FastAPI. It integrates with a generative AI model for chat responses, a Qdrant vector database for document retrieval, and a JSON-based storage for notes. The chatbot endpoint processes user queries independent of user session (session management is handled by frontend), retrieves relevant documents, and generates responses with fine-tuned LLM model using structured prompts with user query, history context, retrieved documents.

### Logic for Key Backend Features:

1. **Conversation History**:
   - Handles list of user queries and responses per session passed by Frontend.
   - Updates the history with each interaction, appending both user input and AI-generated responses.

2. **Separation of Query and Context Enrichment**:
   - An LLM call is used to separate user query into retrieval and instruction component with context from history.
   - **Retrieval Component**: Extracts key details from the query to identify relevant documents using Qdrant, enriched with context from conversation chain.
   - **LLM Instruction Component**: Structures the query for the AI model, focusing on intent, context, and additional instructions for nuanced response generation. Retains memory of prior formatting request within chat session.

## Frontend
A user friendly React app was built to identify various species of mushrooms in the wild using computer vision models from the backend. Using the app a user can take a picture of a mushroom and upload it. The app will send the image to the backend api to get prediction results on weather the mushroom is poisonous or not.

### Screenshots
`Add screenshots here`

## Running Dockerfile
Instructions for running the Dockerfile can be added here.
To run Dockerfile - `Instructions here`

## Notebooks/Reports
This folder contains code that is not part of container - for e.g: Application mockup, EDA, any 🔍 🕵️‍♀️ 🕵️‍♂️ crucial insights, reports or visualizations.

*You may adjust this template as appropriate for your project.*
