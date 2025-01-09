# E-Commerce Expert Assistant Chatbot

A smart e-commerce assistant chatbot that leverages Retrieval-Augmented Generation (RAG) to provide accurate responses about product details and order information. The chatbot integrates with product and order datasets to deliver contextually relevant answers to customer queries.

## Project Overview

This chatbot serves as an intelligent e-commerce assistant capable of:
- Answering detailed product queries from a database of 5000+ musical instruments and related products
- Retrieving and processing order information through a mock API
- Utilizing RAG techniques to enhance response accuracy and relevance
- Balancing performance with cost-efficiency through thoughtful model selection

## Features

### Core Functionality
- Product information retrieval and recommendations
- Order history and status tracking
- RAG-enhanced response generation
- Cost-efficient model implementation
- Mock API integration for order data

### Bonus Features
- Cloud-based hosting interface
- Basic UI for testing
- Model comparison analysis (closed vs open-source)

## Dataset Information

### Product Dataset
- 5000 rows of musical instrument data
- Fields include:
  - Product title
  - Description
  - Features
  - Ratings
  - Price
  - Categories

### Order Dataset
- Customer order history
- Fields include:
  - Order date
  - Customer ID
  - Product category
  - Sales amount
  - Shipping cost
  - Payment method

## Technical Implementation

### Architecture
[Work in progress]
The core part of the project is implemented as a backend API server that handles the user chat.
It consists of the following components:
- LLM for interacting with the user
- Order Data API
- Product Data Index
- Embedding Model for semantic search
- Vector DB to store, search and retrieve vector embeddings

### Requirements
- Python 3.8+
- Preferred: UV for dependency management

## Usage

### Environment Variables
Make sure to setup your `.env` file with the following fields:
```
OPENAI_BASE_URL=
OPENAI_API_KEY=
CHAT_MODEL=llama-3.3-70b-versatile
EMBEDDING_URL=
EMBEDDING_API_KEY=dummy_key
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_BATCH_SIZE=
QDRANT_URL=
QDRANT_API_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_HOST="https://cloud.langfuse.com"
```
### Docker
The best way to use the published docker [images](https://github.com/AmgadHasan/e-commerce-expert-assistant/pkgs/container/e-commerce-expert-assistant)

To start the backend API server at [http://0.0.0.0:3000/](http://0.0.0.0:3000/), simply run:
```sh
docker pull ghcr.io/amgadhasan/e-commerce-expert-assistant:main
docker run -d --env-file .env -p 3000:8000 ghcr.io/amgadhasan/e-commerce-expert-assistant:main
```

### Local UI
To chat with the LLM using a GUI locally, run the `ui.html` file in a browser.
Make sure to modify the API url before running it:
```
const API_URL = 'http://20.121.120.6:3000/chat'
```

### Development

1. Clone the repository
```sh
git clone https://github.com/AmgadHasan/e-commerce-expert-assistant.git
```
2. Create and activate a virtual environment:
```sh
# Using uv
uv sync
```


## Project Structure

```
e-commerce-expert-assistant/
├── data/
│   ├── order_data.parquet
│   └── product_information.parquet
├── src/
├── scripts/
├── Dockerfile
├── Time Estimates.csv
└── README.md
```

## Model Selection and Trade-offs

TBD


## Sample Interactions

TBD


## Contact
LinkedIn:<br>
https://www.linkedin.com/in/amgad-hasan/