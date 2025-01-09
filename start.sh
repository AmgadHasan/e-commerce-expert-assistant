docker build . -t e-ecommerce-chatbot:latest
docker run --env-file .env -p 8000:8000  e-ecommerce-chatbot:latest