import sqlite3
import requests

# Define variables
API_URL = "https://api.hyperbolic.xyz/v1/chat/completions"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlbmcuYW1naGFzYW5AZ21haWwuY29tIn0.fiWTAmsXl2y4BnWtCL5QK4Yq2SYvv-ZE_LTVoIE7Rp8"

MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct"

DATABASE_PATH = "data/products_information.db"
TABLE_NAME = "products"
TITLE_COLUMN = 'title'
FEATURES_COLUMN = "features"
LONG_DESCRIPTION_COLUMN = "description"
SHORT_DESCRIPTION_COLUMN = "rewritten_description"

SYSTEM_MESSAGE = \
"""\
You are an expert writer who can write good and concise product descriptions given the title, long description and the features of the product.
The short description you generate should never exceed 1000 words in length.\
"""

USER_MESSAGE_TEMPLATE = \
'''\
Write a concise but comprehensive description for the product below. The description will be embedded and stored in a vector database, and will be later used in retrieval-augmented generation.
The description should be free flowing text written as a paragraph. Focus on writing a description rather than promoting the product.

TITLE:
"""
{title}
"""
FEATURES:
"""
{features}
"""
LONG DESCRIPTION:
"""
{long_description}
"""

Return the description directly without any introductions.
'''



def generate_short_description(title: str, features: str, long_description: str):
    """
    Generate a short description using the API.
    """
    API_HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_MESSAGE
            },
            {
                "role": "user",
                "content": USER_MESSAGE_TEMPLATE.format(title=title, features=features, long_description=long_description)
            }
        ],
        "model": MODEL,
        "max_tokens": 2048,
        "temperature": 0.1,
        "top_p": 0.9
    }
    response = requests.post(API_URL, headers=API_HEADERS, json=data)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()["choices"][0]["message"]["content"]

def process_database():
    """
    Load data from the SQLite database, generate short descriptions, and save the updated data back to the database.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Ensure the output column exists
    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    columns = [column[1] for column in cursor.fetchall()]
    if SHORT_DESCRIPTION_COLUMN not in columns:
        cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN {SHORT_DESCRIPTION_COLUMN} TEXT")
        conn.commit()

    # Fetch all rows from the table where rewritten_description is NULL or empty
    cursor.execute(
        f"SELECT parent_asin, {TITLE_COLUMN}, {FEATURES_COLUMN}, {LONG_DESCRIPTION_COLUMN} "
        f"FROM {TABLE_NAME} "
        f"WHERE {SHORT_DESCRIPTION_COLUMN} IS NULL OR {SHORT_DESCRIPTION_COLUMN} = ''"
    )
    rows = cursor.fetchall()

    print(f"{len(rows)} rows remaining")

    # Loop over each row to generate and store the short description
    for idx, (parent_asin, title, features, long_description) in enumerate(rows):
        short_description = generate_short_description(title, features, long_description)
        
        # Update the row with the new short description
        cursor.execute(
            f"UPDATE {TABLE_NAME} SET {SHORT_DESCRIPTION_COLUMN} = ? WHERE parent_asin = ?",
            (short_description, parent_asin)
        )
        conn.commit()

        print(f"Processed row {idx + 1}: {short_description[:50]}...")

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    process_database()