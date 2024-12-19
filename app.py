from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

# Path to CSV files
sales_file = "sales_data.csv"
product_file = "product_data.csv"
customer_file = "customer_data.csv"

# Load data from CSV files
sales_data = pd.read_csv(sales_file)
product_data = pd.read_csv(product_file)
customer_data = pd.read_csv(customer_file)

@app.route('/', methods=['GET', 'POST'])
def index():
    customer_details = None
    error = None

    if request.method == 'POST':
        customer_name = request.form.get('customer_name')

        # Get customer details
        customer = customer_data[customer_data['CustomerName'] == customer_name]
        if customer.empty:
            error = "Customer not found"
        else:
            customer_details = customer.iloc[0].to_dict()

            # Get sales data for the customer
            customer_sales = sales_data[sales_data['CustomerID'] == customer_details['CustomerID']]
            if customer_sales.empty:
                error = "No sales data found for this customer"
            else:
                # Calculate Total Sales and Products
                customer_sales['TotalSaleValue'] = customer_sales['Quantity'] * customer_sales['PricePerUnit']
                total_sales = customer_sales['TotalSaleValue'].sum()
                total_products = customer_sales['Quantity'].sum()

                # Get product details for the customer's sales
                product_ids = customer_sales['ProductID'].unique()
                purchased_products = product_data[product_data['ProductID'].isin(product_ids)]
                product_details = purchased_products.to_dict(orient='records')

                return render_template(
                    'index.html',
                    customer_details=customer_details,
                    sales_details=customer_sales.to_dict(orient='records'),
                    product_details=product_details,
                    total_sales=total_sales,
                    total_products=total_products,
                )

    return render_template('index.html', customer_details=customer_details, error=error)

@app.route('/sales_chart_data', methods=['GET'])
def sales_chart_data():
    customer_name = request.args.get('customer_name', '')

    # Get customer details
    customer = customer_data[customer_data['CustomerName'] == customer_name]
    if customer.empty:
        return jsonify({'error': 'Customer not found'}), 404

    customer_details = customer.iloc[0].to_dict()

    # Get sales data for the customer
    customer_sales = sales_data[sales_data['CustomerID'] == customer_details['CustomerID']]
    if customer_sales.empty:
        return jsonify({'error': 'No sales data found'}), 404

    # Ensure TotalSaleValue calculation exists
    if 'TotalSaleValue' not in customer_sales.columns:
        customer_sales['TotalSaleValue'] = customer_sales['Quantity'] * customer_sales['PricePerUnit']

    # Prepare data for charts
    sales_over_time = customer_sales.groupby('SaleDate')['TotalSaleValue'].sum().reset_index()
    category_sales = (
        customer_sales.merge(product_data, on='ProductID')
        .groupby('Category')['TotalSaleValue'].sum()
        .reset_index()
    )

    return jsonify({
        'sales_over_time': sales_over_time.to_dict(orient='records'),
        'category_sales': category_sales.to_dict(orient='records'),
    })

@app.route('/customer_suggestions', methods=['GET'])
def customer_suggestions():
    query = request.args.get('query', '').lower()
    suggestions = customer_data[
        customer_data['CustomerName'].str.lower().str.contains(query)
    ]['CustomerName'].tolist()
    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True)
