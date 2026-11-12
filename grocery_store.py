"""
Smart Grocery Store Management System
=====================================
A console application to manage products, stock and sales of a local
grocery store.

Data structures used:
    products -> list of dictionaries {id, name, category, price, stock}
    sales    -> list of dictionaries {product_id, product_name,
                                      quantity_sold, total_amount}
"""

# ---------------------------------------------------------------
# Data storage
# ---------------------------------------------------------------
products = [
    {"id": 101, "name": "Milk", "category": "Dairy", "price": 250.0, "stock": 20},
    {"id": 102, "name": "Bread", "category": "Bakery", "price": 120.0, "stock": 15},
    {"id": 103, "name": "Eggs", "category": "Dairy", "price": 320.0, "stock": 4},
    {"id": 104, "name": "Rice", "category": "Grains", "price": 450.0, "stock": 30},
]

sales = []  # completed sales are stored here

LOW_STOCK_LIMIT = 5  # stock below this number is "low"


# ---------------------------------------------------------------
# Input helper functions (input validation)
# ---------------------------------------------------------------
def get_text(message):
    """Ask until the user enters a non-empty text."""
    while True:
        text = input(message).strip()
        if text:
            return text
        print("Error: This field cannot be empty.")


def get_whole_number(message, minimum):
    """Ask until the user enters a whole number >= minimum."""
    while True:
        text = input(message).strip()
        try:
            number = int(text)
        except ValueError:
            print("Error: Please enter a valid whole number.")
            continue
        if number < minimum:
            print(f"Error: Number must be {minimum} or more.")
            continue
        return number


def get_price(message):
    """Ask until the user enters a valid price greater than 0."""
    while True:
        text = input(message).strip()
        try:
            price = float(text)
        except ValueError:
            print("Error: Please enter a valid price, e.g. 250 or 99.5")
            continue
        # price > 0 is False for 0, negatives and nan; inf is rejected below
        if not (0 < price < float("inf")):
            print("Error: Price must be greater than 0.")
            continue
        return round(price, 2)


# ---------------------------------------------------------------
# Helper functions for products
# ---------------------------------------------------------------
def find_product(product_id):
    """Loop through products and return the matching dictionary (or None)."""
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def show_product(product):
    """Print full details of one product."""
    print(f"  ID       : {product['id']}")
    print(f"  Name     : {product['name']}")
    print(f"  Category : {product['category']}")
    print(f"  Price    : {product['price']:.2f}")
    print(f"  Stock    : {product['stock']}")


# ---------------------------------------------------------------
# Menu option functions
# ---------------------------------------------------------------
def add_product():
    """1. Add a new product; duplicate IDs are not allowed."""
    print("\n--- Add New Product ---")
    product_id = get_whole_number("Enter Product ID: ", 1)

    if find_product(product_id) is not None:
        print("Error: This Product ID already exists. Product not added.")
        return

    name = get_text("Enter Product Name: ")
    category = get_text("Enter Category: ")
    price = get_price("Enter Price: ")
    stock = get_whole_number("Enter Available Stock: ", 0)

    product = {
        "id": product_id,
        "name": name,
        "category": category,
        "price": price,
        "stock": stock,
    }
    products.append(product)  # add the dictionary to the list
    print(f"Success: {name} has been added.")


def view_all_products():
    """2. Show all products in a table."""
    print("\n--- All Products ---")
    if len(products) == 0:
        print("No products available.")
        return

    print(f"{'ID':<8}{'Name':<22}{'Category':<16}{'Price':>10}{'Stock':>8}")
    print("-" * 64)
    for product in products:
        print(f"{product['id']:<8}{product['name']:<22}{product['category']:<16}"
              f"{product['price']:>10.2f}{product['stock']:>8}")


def search_product():
    """3. Search by ID or by name (full or partial, any letter case)."""
    print("\n--- Search Product ---")
    text = get_text("Enter Product ID or Name: ")
    found = 0

    # isascii() is needed because isdigit() is also True for characters
    # such as "²", which int() cannot convert (that would crash the program)
    is_number = text.isascii() and text.isdigit()

    for product in products:
        # match by ID (only when the text is a number) or by name
        same_id = is_number and product["id"] == int(text)
        same_name = text.lower() in product["name"].lower()
        if same_id or same_name:
            found += 1
            print(f"\nProduct found ({found}):")
            show_product(product)

    if found == 0:
        print("Product not found.")


def update_stock():
    """4. Add stock to a product or set a new stock quantity."""
    print("\n--- Update Product Stock ---")
    product_id = get_whole_number("Enter Product ID: ", 1)
    product = find_product(product_id)

    if product is None:
        print("Error: Product not found.")
        return

    print(f"Current stock of {product['name']}: {product['stock']}")
    print("1. Add stock")
    print("2. Set new stock quantity")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        amount = get_whole_number("Enter quantity to add: ", 1)
        product["stock"] += amount
    elif choice == "2":
        product["stock"] = get_whole_number("Enter new stock quantity: ", 0)
    else:
        print("Error: Invalid choice. Stock not changed.")
        return

    print("Stock updated successfully.")
    print(f"Updated stock of {product['name']}: {product['stock']}")


def process_sale():
    """5. Sell a product: check ID, check stock, deduct stock, save sale."""
    print("\n--- Process Customer Sale ---")
    product_id = get_whole_number("Enter Product ID: ", 1)
    product = find_product(product_id)

    if product is None:
        print("Error: Product not found. Sale cancelled.")
        return

    quantity = get_whole_number("Enter purchase quantity: ", 1)

    # sale is not allowed if quantity is more than the stock
    if quantity > product["stock"]:
        print(f"Error: Only {product['stock']} unit(s) of {product['name']} "
              "in stock. Sale cancelled.")
        return

    total = round(product["price"] * quantity, 2)
    product["stock"] -= quantity

    sale = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity_sold": quantity,
        "total_amount": total,
    }
    sales.append(sale)

    print("\n--- Purchase Summary ---")
    print(f"Product         : {product['name']} (ID {product['id']})")
    print(f"Unit Price      : {product['price']:.2f}")
    print(f"Quantity        : {quantity}")
    print(f"Total Price     : {total:.2f}")
    print(f"Remaining Stock : {product['stock']}")


def view_sales_records():
    """6. Show all completed sales."""
    print("\n--- Sales Records ---")
    if len(sales) == 0:
        print("No sales recorded yet.")
        return

    print(f"{'No.':<6}{'Product ID':<12}{'Product Name':<22}{'Qty':>6}{'Total':>14}")
    print("-" * 60)
    number = 1
    for sale in sales:
        print(f"{number:<6}{sale['product_id']:<12}{sale['product_name']:<22}"
              f"{sale['quantity_sold']:>6}{sale['total_amount']:>14.2f}")
        number += 1


def generate_report():
    """7. Final store report."""
    print("\n====================================")
    print("          STORE REPORT")
    print("====================================")

    total_stock = 0
    for product in products:
        total_stock += product["stock"]

    revenue = 0
    for sale in sales:
        revenue += sale["total_amount"]

    print(f"Total number of products : {len(products)}")
    print(f"Total available stock    : {total_stock}")
    print(f"Total sales transactions : {len(sales)}")
    print(f"Total revenue generated  : {revenue:.2f}")

    print(f"\nProducts with stock below {LOW_STOCK_LIMIT} units:")
    low_found = False
    for product in products:
        if product["stock"] < LOW_STOCK_LIMIT:
            print(f"  - {product['name']} (ID {product['id']}): "
                  f"{product['stock']} left")
            low_found = True
    if not low_found:
        print("  None")

    print()
    if len(products) == 0:
        print("Highest priced product : N/A")
        print("Lowest priced product  : N/A")
        return

    # find highest and lowest price using a loop
    highest = products[0]["price"]
    lowest = products[0]["price"]
    for product in products:
        if product["price"] > highest:
            highest = product["price"]
        if product["price"] < lowest:
            lowest = product["price"]

    # print every product with that price (handles ties)
    for product in products:
        if product["price"] == highest:
            print(f"Highest priced product : {product['name']} "
                  f"(ID {product['id']}) - {highest:.2f}")
    for product in products:
        if product["price"] == lowest:
            print(f"Lowest priced product  : {product['name']} "
                  f"(ID {product['id']}) - {lowest:.2f}")


# ---------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------
def show_menu():
    """Print the main menu."""
    print("\n====================================")
    print("SMART GROCERY STORE SYSTEM")
    print("====================================\n")
    print("1. Add New Product")
    print("2. View All Products")
    print("3. Search Product")
    print("4. Update Product Stock")
    print("5. Process Customer Sale")
    print("6. View Sales Records")
    print("7. Generate Store Report")
    print("8. Exit\n")


def main():
    """Run the menu until the user chooses Exit."""
    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_product()
        elif choice == "2":
            view_all_products()
        elif choice == "3":
            search_product()
        elif choice == "4":
            update_stock()
        elif choice == "5":
            process_sale()
        elif choice == "6":
            view_sales_records()
        elif choice == "7":
            generate_report()
        elif choice == "8":
            print("\nThank you for using the Smart Grocery Store System. Goodbye!")
            break
        else:
            print("Error: Invalid choice. Please enter a number from 1 to 8.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram closed. Goodbye!")
