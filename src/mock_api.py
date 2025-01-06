from enum import Enum

import polars as pl
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Literal

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
# Decide for each data type what a sensible default would be
# For strings, empty. For numbers, 0, where applicable.
df = df.fill_null("")

# Initialize FastAPI app
app = FastAPI(
    title="E-commerce Dataset API", description="API for querying e-commerce sales data"
)


@app.get("/data", response_class=JSONResponse)
def get_all_data() -> list[dict]:
    """Retrieve all records in the dataset."""
    data = df.to_dicts()
    return data


@app.get("/data/customer/{customer_id}")
def get_customer_data(customer_id: int) -> list[dict]:
    """Retrieve all orders for a specific Customer ID."""
    filtered_data = df.filter(pl.col("Customer_Id") == customer_id)
    if filtered_data.is_empty():
        raise HTTPException(
            status_code=404, detail=f"No data found for Customer ID {customer_id}"
        )
    return filtered_data.to_dicts()


@app.get("/data/product-category/{category}")
def get_product_category_data(category: ProductCategory) -> list[dict]:
    """Retrieve all orders for a specific Product Category."""
    filtered_data = df.filter(pl.col("Product_Category") == category.value)
    if filtered_data.is_empty():
        raise HTTPException(
            status_code=404,
            detail=f"No data found for Product Category '{category.value}'",
        )
    return filtered_data.to_dicts()


@app.get("/data/order-priority/{priority}")
def get_orders_by_priority(
    priority: Literal["Medium", "High", "", "Critical", "Low"] ,#OrderPriority,
    sort_by_date: bool | None = None,
    sort_descendingly: bool = False,
    limit: int | None = Query(None, ge=1),
) -> list[dict]:
    """
    Retrieve all orders with the given priority.

    Parameters:
    - sort_by_date: Whether to sort results by date and time.
    - sort_descendingly: Whether to sort in descending order.
    - limit: Maximum number of records to return.
    """
    filtered_data = df.filter(pl.col("Order_Priority") == priority)
    if filtered_data.is_empty():
        raise HTTPException(
            status_code=404,
            detail=f"No data found for Order Priority '{priority}'",
        )
    if sort_by_date:
        filtered_data = filtered_data.sort(
            by=["Order_Date", "Time"], descending=sort_descendingly
        )
    if limit:
        filtered_data = filtered_data[:limit]
    return filtered_data.to_dicts()


@app.get("/data/total-sales-by-category")
def get_total_sales_by_category() -> list[dict]:
    """Calculate total sales by Product Category."""
    sales_summary = df.group_by("Product_Category").agg(pl.col("Sales").sum())
    return sales_summary.to_dicts()


# Endpoint to get high-profit products
@app.get("/data/high-profit-products")
def get_high_profit_products(min_profit: float = 100.0) -> list[dict]:
    """Retrieve products with profit greater than the specified value."""
    filtered_data = df.filter(pl.col("Profit") > min_profit)
    if filtered_data.is_empty():
        raise HTTPException(
            status_code=404,
            detail=f"No products found with profit greater than {min_profit}",
        )
    return filtered_data.to_dicts()


# Endpoint to get shipping cost summary
@app.get("/data/shipping-cost-summary")
def get_shipping_cost_summary() -> dict:
    """Retrieve the average, minimum, and maximum shipping cost."""
    summary = {
        "average_shipping_cost": df["Shipping_Cost"].mean(),
        "min_shipping_cost": df["Shipping_Cost"].min(),
        "max_shipping_cost": df["Shipping_Cost"].max(),
    }
    return summary


@app.get("/data/profit-by-gender")
def get_profit_by_gender() -> list[dict]:
    """Calculate total profit by customer gender."""
    profit_summary = df.group_by("Gender").agg(pl.col("Profit").sum())
    return profit_summary.to_dicts()
