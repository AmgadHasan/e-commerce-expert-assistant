
import src.mock_api as mock_api
from src.utils import DirectReturnException, query_product_database
from src.vectorstore import retrieve_relevant_products


def get_customer_id():
    data = {"role": "assistant", "content": "Please provider your Customer ID"}
    raise DirectReturnException(message=data)
    

# def handle_product_query(user_query: str):
#     print(f"Printing from `handle_product_query`.\t {user_query = }")

# query_router_tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "handle_order_query",
#             "description": "Handles user queries related to their orders or purchase hitory.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "user_query": {
#                         "type": "string",
#                         "description": "The user query relating to an order or their purchase history.",
#                     }
#                 },
#                 "required": ["user_query"],
#                 "additionalProperties": False,
#             },
#         },
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "handle_product_query",
#             "description": "Handles user queries related related to product specifics and/or recommending or suggesting products based on user needs and preferences.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "user_query": {
#                         "type": "string",
#                         "description": "The user query relating to a product specifics or recommendation.",
#                     }
#                 },
#                 "required": ["user_query"],
#                 "additionalProperties": False,
#             },
#         },
#     },
# ]

order_dataset_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_shipping_cost_summary",
            "description": 'Retrieve the average, minimum, and maximum shipping cost.\n\n Returns a json objet with keys  ["average_shipping_cost","min_shipping_cost","max_shipping_cost"]',
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_high_profit_products",
            "description": "Retrieve products with profit greater than the specified value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_profit": {
                        "type": "number",
                        "description": "The minimum profit value to filter products by",
                    }
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_profit_by_gender",
            "description": "Calculate total profit by customer gender.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_total_sales_by_category",
            "description": "Calculate total sales by Product Category.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_orders_by_priority",
            "description": "Retrieve all orders with the given priority.",
            "parameters": {
                "type": "object",
                "properties": {
                    "priority": {
                        "type": "string",
                        "description": "The priority of the orders to retrieve. Must be one of 'Medium', 'High', 'Critical', 'Low', or '' (none).",
                        "enum": ["Medium", "High", "Critical", "Low", ""],
                    },
                    "sort_by_date": {
                        "type": "boolean",
                        "description": "A flag to sort the data by order date. Optional",
                    },
                    "sort_descendingly": {
                        "type": "boolean",
                        "description": "A flag to sort the data descendingly. Requires `sort_by_date` to be True. Optional",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Only retrieve the first `limit` rows. Similar to the `LIMIT` clause in SQL. Optional",
                    },
                },
                "required": ["priority"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_category_data",
            "description": "Retrieve all orders for a specific Product Category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "The product category for which to retrieve orders.",
                        "enum": [
                            "Home & Furniture",
                            "Auto & Accessories",
                            "Fashion",
                            "Electronic",
                        ],
                    }
                },
                "required": ["category"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_data",
            "description": "Retrieve all orders for a specific Customer ID. Requires the `customer_id` argument which must be a valid integer value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The ID of the customer whose data needs to be retrieved. Must be an integer",
                    },
                },
                "required": ["customer_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_data",
            "description": "Retrieve all records in the dataset.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_id",
            "description": 'Obtains the Customer ID by asking the user "Please provide your Customer ID"',
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
]

product_dataset_tools = [
    {
        "type": "function",
        "function": {
            "name": "query_product_database",
            "description": "Quries the product database using SQL. The database has the following table:```sql\nCREATE TABLE products (\n\tmain_category TEXT, \n\ttitle TEXT, \n\taverage_rating FLOAT, \n\trating_number BIGINT, \n\tfeatures TEXT, \n\tdescription TEXT, \n\tprice TEXT, \n\tstore TEXT, \n\tcategories TEXT, \n\tdetails TEXT, \n\tparent_asin TEXT\n)```",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "The sql query to run against the SQLite database. Must be in the SQLite format.",
                    }
                },
                "required": ["user_query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_relevant_products",
            "description": "Performs semantic search across a database of product description using the provided query. Use this to search for products using their description or their features.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query that will be fed into the semantic search engine. Should be a description of the product, its name or its features.",
                    }
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
]

llm_tools_map = {
    "get_all_data": mock_api.get_all_data,
    "get_customer_data": mock_api.get_customer_data,
    "get_product_category_data": mock_api.get_product_category_data,
    "get_orders_by_priority": mock_api.get_orders_by_priority,
    "get_total_sales_by_category": mock_api.get_total_sales_by_category,
    "get_high_profit_products": mock_api.get_high_profit_products,
    "get_shipping_cost_summary": mock_api.get_shipping_cost_summary,
    "get_profit_by_gender": mock_api.get_profit_by_gender,
    "get_customer_id": get_customer_id,
    "query_product_database": query_product_database,
    "retrieve_relevant_products": retrieve_relevant_products
    # "handle_order_query": handle_order_query,
    # "handle_product_query": handle_product_query,
}
