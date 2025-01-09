import sqlite3
import polars as pl

def create_database_and_table(db_name: str, table_name: str):
    """Create a SQLite database and a table if it doesn't exist."""
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
    """Insert data from a Polars DataFrame into a SQLite table."""
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    
    # Convert the Polars DataFrame to a list of tuples
    data = df.rows()
    
    # Define the SQL command to insert data into the table
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
    
    # Insert the data into the table
    cursor.executemany(insert_sql, data)
    
    connection.commit()
    connection.close()
    print(f"Data inserted into table '{table_name}' successfully.")

def main(args: dict):
    create_database_and_table(args['sqlite_db'], args['table_name'])
    df = pl.read_parquet(args['dataset_file_path'])
    insert_data_into_table(args['sqlite_db'],  args['table_name'], df)

if __name__ == "__main__":
    args = {
        "dataset_file_path": "data/product_information.parquet",
        "sqlite_db": "data/products_information.db",
        "table_name": "products",

    }
    main(args)