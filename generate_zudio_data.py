import pandas as pd
import numpy as np
import random
import datetime
import os

# 1. Load Stores Data (Jo humne pehle scrape kiya tha)
try:
    stores_df = pd.read_csv('Final_Zudio_Stores.csv')
    # Limit to 50 stores for manageable dataset size but realistic metrics
    stores_df = stores_df.head(50).copy()
    stores_df['store_id'] = ['S' + str(i).zfill(3) for i in range(1, len(stores_df)+1)]
    stores_df['store_manager'] = ['Manager_' + str(i) for i in range(1, len(stores_df)+1)]
    stores_df['store_type'] = np.random.choice(['Mall', 'Standalone', 'High Street'], size=len(stores_df))
    store_ids = stores_df['store_id'].tolist()
except:
    store_ids = ['S' + str(i).zfill(3) for i in range(1, 51)]
    stores_df = pd.DataFrame({'store_id': store_ids, 'city': 'Pune', 'store_type': 'Mall'})

# 2. Generate Products Data
categories = {
    'Women': [399, 499, 699, 899, 999],
    'Men': [299, 499, 699, 799, 999],
    'Kids': [199, 299, 399, 499],
    'Beauty': [99, 149, 199, 299],
    'Accessories': [149, 199, 299],
    'Footwear': [299, 499, 699],
    'Home': [199, 299, 399]
}

products = []
p_id = 1
for cat, prices in categories.items():
    for i in range(20): # 20 products per category
        price = random.choice(prices)
        products.append({
            'product_id': f'P{str(p_id).zfill(4)}',
            'category': cat,
            'sub_category': f'{cat}_Item_{i}',
            'mrp': price,
            'cost_price': round(price * random.uniform(0.5, 0.7))
        })
        p_id += 1
products_df = pd.DataFrame(products)

# 3. Generate Customers Data
customers_df = pd.DataFrame({
    'customer_id': ['C' + str(i).zfill(4) for i in range(1, 10001)],
    'customer_name': ['Customer_' + str(i) for i in range(1, 10001)],
    'membership_tier': np.random.choice(['Silver', 'Gold', 'Platinum', 'None'], size=10000, p=[0.4, 0.3, 0.1, 0.2]),
    'age': np.random.randint(16, 50, size=10000)
})
customer_ids = customers_df['customer_id'].tolist()

# 4. Generate Sales Data to match target metrics (~40,000+ orders, ~1.18 Lakh items, ~8 Crore Sales)
# Generating data for 6 months (Apr 2026 to Sep 2026)
start_date = datetime.date(2026, 4, 1)
end_date = datetime.date(2026, 9, 30)
days = (end_date - start_date).days

sales = []
transaction_id = 1

# We need around 42000 orders total.
total_orders = 43000
dates = [start_date + datetime.timedelta(days=random.randint(0, days)) for _ in range(total_orders)]
dates.sort()

# Pre-calculate probabilities for categories to match the dashboard mix (Women 38%, Men 34%, Kids 18%, Beauty 10%)
cat_weights = {'Women': 0.38, 'Men': 0.34, 'Kids': 0.18, 'Beauty': 0.05, 'Accessories': 0.02, 'Footwear': 0.02, 'Home': 0.01}
prod_ids = products_df['product_id'].tolist()
prod_cats = products_df.set_index('product_id')['category'].to_dict()

# Creating a weighted list of product IDs
weighted_prods = []
for p in prod_ids:
    c = prod_cats[p]
    weight = int(cat_weights[c] * 100)
    weighted_prods.extend([p] * weight)

print("Generating 43,000 Orders... Please wait.")
for i in range(total_orders):
    t_date = dates[i]
    c_id = random.choice(customer_ids)
    s_id = random.choice(store_ids)
    pay_mode = random.choice(['Cash', 'Credit Card', 'UPI', 'Debit Card'])
    
    # 1 to 5 items per order (average ~2.7 items per order to hit ~1.18L items)
    num_items = random.choices([1, 2, 3, 4, 5, 6], weights=[10, 30, 30, 15, 10, 5])[0]
    
    for _ in range(num_items):
        p_id = random.choice(weighted_prods)
        qty = random.choices([1, 2, 3], weights=[80, 15, 5])[0]
        
        sales.append({
            'transaction_id': f'T{str(transaction_id).zfill(6)}',
            'date': t_date.strftime('%Y-%m-%d'),
            'store_id': s_id,
            'customer_id': c_id,
            'product_id': p_id,
            'quantity': qty,
            'payment_mode': pay_mode
        })
    transaction_id += 1

sales_df = pd.DataFrame(sales)

# Merge MRP into sales to verify totals
sales_df = sales_df.merge(products_df[['product_id', 'mrp']], on='product_id', how='left')
sales_df['Total Amount'] = sales_df['quantity'] * sales_df['mrp']

print(f"Total Net Sales generated: ₹{sales_df['Total Amount'].sum():,.0f}")
print(f"Total Orders: {sales_df['transaction_id'].nunique():,}")
print(f"Total Items Sold: {sales_df['quantity'].sum():,}")

# Save the final CSVs
stores_df.to_csv('New_Zudio_Stores.csv', index=False)
products_df.to_csv('New_Zudio_Products.csv', index=False)
customers_df.to_csv('New_Zudio_Customers.csv', index=False)
sales_df.drop(columns=['mrp', 'Total Amount']).to_csv('New_Zudio_Sales.csv', index=False)

print("\nSuccess! Saari CSV files generate ho gayi hain.")
