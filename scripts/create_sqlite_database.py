'''
A script to convert dataset files into SQLite databases.
This is useful for leveraging the LLM's proficiency in writing SQL code.
'''
import sqlite3
import polars as pl

def create_database_and_table(db_name: str, table_name: str):
    """
    Create a SQLite database and a table if it doesn't already exist.
    
    Parameters:
    - db_name: The name of the SQLite database file.
    - table_name: The name of the table to create within the database.
    """
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        main_category TEXT,
        title TEXT,
        average_rating FLOAT,
        rating_number BIGINT,
        features TEXT,
        description TEXT,
        price TEXT,
        store TEXT,
        categories TEXT,
        details TEXT,
        parent_asin TEXT
    );
    """
    cursor.execute(create_table_sql)
    connection.commit()
    connection.close()
    print(f"Database '{db_name}' and table '{table_name}' created successfully.")

def insert_data_into_table(db_name: str, table_name: str, df: pl.DataFrame):
    """
    Insert data from a Polars DataFrame into a specified SQLite table.

    Parameters:
    - db_name: The name of the SQLite database file.
    - table_name: The name of the table to insert data into.
    - df: A Polars DataFrame containing the data to be inserted.
    """
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    
    # Convert the DataFrame rows into a list of tuples for insertion
    data = df.rows()
    
    # SQL command to insert data rows into the table
    insert_sql = f"""
    INSERT INTO {table_name} (
        main_category,
        title,
        average_rating,
        rating_number,
        features,
        description,
        price,
        store,
        categories,
        details,
        parent_asin
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    
    cursor.executemany(insert_sql, data)
    connection.commit()
    connection.close()
    print(f"Data inserted into table '{table_name}' successfully.")

def main(args: dict):
    """
    Main function to create a database and populate it with data from a parquet file.

    Parameters:
    - args: A dictionary containing configurations for file paths and database details.
    """
    create_database_and_table(args['sqlite_db'], args['table_name'])
    # Read the data from the specified Parquet file into a Polars DataFrame
    df = pl.read_parquet(args['dataset_file_path'])
    insert_data_into_table(args['sqlite_db'], args['table_name'], df)

if __name__ == "__main__":
    args = {
        "dataset_file_path": "data/product_information.parquet",
        "sqlite_db": "data/products_information.db",
        "table_name": "products",
    }
    main(args)