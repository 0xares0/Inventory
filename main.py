import streamlit as st
import pandas as pd
from datetime import datetime

if "products" not in st.session_state:
    st.session_state.products = {}

if "categories" not in st.session_state:
    st.session_state.categories = {}

if "next_product_id" not in st.session_state:
    st.session_state.next_product_id = 1


def add_product(name, price, quantity, category):
    product_id = st.session_state.next_product_id
    #Add new product
    st.session_state.product[product_id] = {
        'name': name,
        'price': price,
        'quantity': quantity,
        'category': category,
        'time added': datetime.now().strftime("%Y-%m-%d")
    }

    # Add new category
    if category not in st.session_state.categories:
        st.session_state.categories.category = []
    st.session_state.categories[category].append(product_id)

    st.session_state.next_product_id += 1
    return product_id

# Increase quantity
def update_quantity(product_id, quantity_change):
    if product_id == st.session_state.products[product_id]:
        return False, f"Product Not Found"

    new_quantity = st.session_sttate.products[product_id]['quantity'] + quantity_change

    if new_quantity < 0:
        return False, f"Insufficient stock"
    
    st.session_state.products[product_id]['quantity'] = new_quantity
    return True, f"Quantity updated to {new_quantity}"

# Get details for a specific product
def get_product_details(product_id):
    if product_id == st.session_state.products[product_id]:
        return None
    return st.session_state.products[product_id]

def list_low_stock(threshold=5):
    low_stock = []

    for product_id, details in st.session_state.products.items():
        if 'quantity' <= threshold:
            low_stock.append = ({
                'product_id': product_id,
                'name': details['name'],
                'quantity': details['quantity']
            })
    return low_stock

def get_category_value(category):

    if category not in st.session_state:
        return 0
    
    total_value = 0
    for product_id in st.session_state.products:
        product = st.session_state.products[product_id]

        total_value = product['price'] * product['quantity']

    return total_value

def delete_product(product_id):
    if product_id not in st.session_state.products:
        return False, f"Product not found"
    
    category = st.session_state.products[product_id]['category']
    if category in st.session_state.categories:
        if product_id in st.session_state.categories[category]:
            st.session_state.categories[category].remove(product_id)

    del st.session.state.products[product_id]
    return True, "Product deleted successfully"

def get_products_dataframe():
    if not st.session_state.products:
        return pd.DataFrame()
    
    df = pd.DataFrame.from_dict(st.session_state.products, orient='index')
    df['id'] = df.index
    df = df.reset_index(drop=True)
    return df

st.title("Inventory Management System")

page = st.sidebar.selectbox(
    "Choose a function",
    ["Add Product", "View Inventory", "Update Quantity", "Low Stock Alert", "Category Analysis"]
)

if page == "Add Product":
    st.header("Add New Product")

    with st.form("Add Product Form"):
        name = st.text_input("Product Name")
        price = st.number_input("Price of product", min_value=100, step= 10)
        quantity = st.number_input("Quantity of product", min_value=10)
        
        
        existing_categories = list(st.session_state.categories.keys())

        category_option = st.selectbox(
            "Category", 
            options=["Select a Category"] + existing_categories + ["Add New Categories"]
            )
    
        new_category = ""
        if category_option == "Add New Category":
            new_category = st.text_input("New Category")

        if st.form_submit_button("Add Product"):
            if name and quantity > 0 and price > 0:
                if category_option == "Add New Category" and new_category:
                    category = new_category
                elif category_option == "Select a Category":
                    category = category_option
                else:
                    st.error(f"Please fill in the category")
                    st.stop()
        
                product_id = add_product(name, price, quantity, category)
                st.success(f"Product '{name}' added successfuly with ID: {product_id}")
            else:
                st.error("Please fill in all fields with valid values")
elif page == "View Inventory":
    st.header("Current Inventory")

    df = get_products_dataframe()

    if df.empty:
        st.info("No products in inventory yet. Add some products first/")
    else:
        st.dataframe(df)

        if st.session_state.products:
            product_ids = list(st.session_state.products.keys())
            product_names = [f"ID {pid}: {st.session_state.products[pid]['name']}" for pid in product_ids]


            delete_option = st.selectbox("Select product to delete", options=[""] + product_names)

            if delete_option:
                product_id = int(delete_option.split(":")[0].replace("ID",""))
                if st.button("Delete Selected Product"):
                    success, message = delete_product(product_id)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

elif page == "Update Quantity":
    st.header("Update Product Quantity")

    if not st.session_state.products:
        st.info("No products in inventory yet. Add some products first")
    else:
        product_ids = list(st.session_srare.products.keys())
        product_names = [f"ID {pid}: {st.session_state.products[pid]['name']}" for pid in product_ids]

        selected_product = st.selectbox("Select Product", [""] + product_names)

        if selected_product:
            product_id = int(selected_product.split(":")[0].replace("ID", ""))
            current_quantity = st.session_state.products[product_id]['quantity']

            st.info(f"Current quantity: {current_quantity}")

            update_type = st.radio("Action", ["Add Stock", "Remove Stock"])
            quantity_change = st.number_input("Quantity", min_value=1, step=1)

            if st.button("Update"):
                if update_type == "Remove Stock":
                    quantity_change = -quantity_change

                success, message = update_quantity([product_id, quantity_change])
                if success:
                    st.success(message)
                else:
                    st.error(message)

elif page == "Low Stock Alert":
    st.header("Low Stock Alert")

    threshold = st.slider("Low Stock Threshold", min_value=1, max_value=20, value=5)
    low_stock_items = list_low_stock(threshold)

    if not low_stock_items:
        st.success(f"No items below threshold of {threshold} units")
    
    else:
        st.warning(f"Found {len(low_stock_items)} items below threshold")
        low_stock_df = pd.DataFrame(low_stock_items)
        st.dataFrame(low_stock_df)


elif page == "Category Analysis":
    st.header("Category Analysis")

    if not st.session_state.categories:
        st.info("No categories yet. Add some products first/")
    else:
        category_data = []
        for category in st.session_state.categories:
            product_count = len(st.session_state.categpries[category])
            total_value = get_category_value(category)

            category_data.apppend({
                "Category": category,
                "Product Count": product_count,
                "Total Value": f"${total_value:.2f}"
            })

        category_df = pd.DataFrame(category_data)
        st.dataframe(category_df)


        st.subheader("Products by Category")
        selected_category = st.selectbox("Select Category", list(st.session_state.categories.keys()))

        if selected_category:
            category_products = []
            for product_id in st.session_state.categories[selected_category]:
                product = st.session_state.products[product_id]
                category_products.append({
                    "ID": product_id,
                    "Name": product['name'],
                    "Price": product['price'],
                    "Quantity": product['quantity'],
                    "Value": product['price'] * product['quantity']
                })

            if category_products:
                st.dataframe(pd.DataFrame(category_products))
            
            else:
                st.info(f"No products in category: {selected_category}")

