from enum import Enum

import polars as pl
from fastapi import FastAPI, HTTPException

# Load dataset with Polars
DATASET_PATH = "data/Order_Data_Dataset.csv"
df = pl.read_csv(DATASET_PATH)


# Data Models
class ProductCategory(str, Enum):
    home_furniture = "Home & Furniture"
    auto_accessories = "Auto & Accessories"
    fashion = "Fashion"
    electronic = "Electronic"


class OrderPriority(str, Enum):
    medium = "Medium"
    high = "High"
    none = ""
    critical = "Critical"
    low = "Low"


# Clean data (e.g., handle NaN values) at the start
df = df.fill_null("")

# Initialize FastAPI app
app = FastAPI(
    title="E-commerce Dataset API", description="API for querying e-commerce sales data"
)


# Endpoint to get all data
@app.get("/data")
def get_all_data():
    """Retrieve all records in the dataset."""
    return df.to_dicts()


# Endpoint to filter data by Customer ID
@app.get("/data/customer/{customer_id}")
def get_customer_data(customer_id: int):
    """Retrieve all orders for a specific Customer ID."""
    filtered_data = df.filter(pl.col("Customer_Id") == customer_id)
    if filtered_data.is_empty():
        return {"error": f"No data found for Customer ID {customer_id}"}
    return filtered_data.to_dicts()


@app.get("/data/product-category/{category}")
def get_product_category_data(category: ProductCategory):
    """Retrieve all orders for a specific Product Category."""
    filtered_data = df.filter(pl.col("Product_Category") == category.value)
    if filtered_data.is_empty():
        raise HTTPException(
            status_code=404,
            detail=f"No data found for Product Category '{category.value}'",
        )
    return filtered_data.to_dicts()


@app.get("/data/order-priority/{priority}")
def get_orders_by_priority(priority: OrderPriority):
    """Retrieve all orders with the given priority."""
    filtered_data = df.filter(pl.col("Order_Priority") == priority.value)
    if filtered_data.is_empty():
        raise HTTPException(
            status_code=404,
            detail=f"No data found for Order Priority '{priority.value}'",
        )
    return filtered_data.to_dicts()


# Endpoint to calculate total sales by Product Category
@app.get("/data/total-sales-by-category")
def total_sales_by_category():
    """Calculate total sales by Product Category."""
    sales_summary = df.group_by("Product_Category").agg(pl.col("Sales").sum())
    return sales_summary.to_dicts()


# Endpoint to get high-profit products
@app.get("/data/high-profit-products")
def high_profit_products(min_profit: float = 100.0):
    """Retrieve products with profit greater than the specified value."""
    filtered_data = df.filter(pl.col("Profit") > min_profit)
    if filtered_data.is_empty():
        return {"error": f"No products found with profit greater than {min_profit}"}
    return filtered_data.to_dicts()


# Endpoint to get shipping cost summary
@app.get("/data/shipping-cost-summary")
def shipping_cost_summary():
    """Retrieve the average, minimum, and maximum shipping cost."""
    summary = {
        "average_shipping_cost": df["Shipping_Cost"].mean(),
        "min_shipping_cost": df["Shipping_Cost"].min(),
        "max_shipping_cost": df["Shipping_Cost"].max(),
    }
    return summary


# Endpoint to calculate total profit by Gender
@app.get("/data/profit-by-gender")
def profit_by_gender():
    """Calculate total profit by customer gender."""
    profit_summary = df.group_by("Gender").agg(pl.col("Profit").sum())
    return profit_summary.to_dicts()
