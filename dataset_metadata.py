dataset_metadata = {
    "dataset_name": "commercial_sales_data_usd.csv",

    "grain": "One record per month, region, and product",

    "columns": {
        "month": {
            "type": "string",
            "description": "Month in YYYY-MM format"
        },
        "region": {
            "type": "string",
            "description": "Sales region"
        },
        "product": {
            "type": "string",
            "description": "Product category"
        },
        "actual_sales_usd": {
            "type": "float",
            "description": "Actual sales in USD"
        },
        "sales_target_usd": {
            "type": "float",
            "description": "Sales target in USD"
        },
        "pipeline_value_usd": {
            "type": "float",
            "description": "Pipeline value in USD"
        },
        "units_sold": {
            "type": "integer",
            "description": "Units sold"
        }
    },

    "business_calculations": {
        "sales_attainment_percentage":
            "(Total actual sales / Total sales target) * 100",

        "sales_gap":
            "Total sales target - Total actual sales"
    }
}