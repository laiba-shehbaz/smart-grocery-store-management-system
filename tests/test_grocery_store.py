"""
Automated tests for grocery_store.py
Run from the project folder:   python tests/test_grocery_store.py

Each check feeds fake keyboard input to a function, captures what it prints
and verifies the result. No extra libraries are needed.
"""
import builtins
import copy
import io
import os
import sys
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import grocery_store as gs

ORIGINAL_PRODUCTS = copy.deepcopy(gs.products)
passed = 0
failed = 0


def reset():
    """Restore the starting data before every check."""
    gs.products[:] = copy.deepcopy(ORIGINAL_PRODUCTS)
    gs.sales[:] = []


def run_with_result(function, *typed_inputs):
    """Run a function with fake input; return (return value, printed text)."""
    answers = iter(typed_inputs)
    real_input = builtins.input
    builtins.input = lambda prompt="": (print(prompt, end=""), next(answers))[1]
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            result = function()
    finally:
        builtins.input = real_input
    return result, buffer.getvalue()


def run(function, *typed_inputs):
    """Run a function with fake input; return everything it printed."""
    return run_with_result(function, *typed_inputs)[1]


def check(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}")


# ---------------- input helpers ----------------
reset()
value, out = run_with_result(lambda: gs.get_text("x"), "", "   ", "Milk")
check("get_text skips empty input", value == "Milk")
check("get_text prints error for empty input", "cannot be empty" in out)

value, out = run_with_result(lambda: gs.get_whole_number("n", 1), "abc", "0", "7")
check("get_whole_number rejects letters and 0", value == 7)
check("get_whole_number shows error messages", "valid whole number" in out and "1 or more" in out)

value, out = run_with_result(lambda: gs.get_whole_number("n", 0), "0")
check("get_whole_number accepts 0 when minimum is 0", value == 0)
value, out = run_with_result(lambda: gs.get_price("p"), "0", "-3", "abc", "nan", "inf", "99.5")
check("get_price rejects 0, negative, text, nan, inf", value == 99.5)

# ---------------- add product ----------------
reset()
run(gs.add_product, "105", "Oil", "Grocery", "600", "10")
check("add_product appends a new dictionary", len(gs.products) == 5 and gs.products[-1]["name"] == "Oil")
check("add_product stores correct values",
      gs.products[-1] == {"id": 105, "name": "Oil", "category": "Grocery", "price": 600.0, "stock": 10})

reset()
out = run(gs.add_product, "101")
check("add_product blocks duplicate ID", len(gs.products) == 4 and "already exists" in out)

# ---------------- view all ----------------
reset()
out = run(gs.view_all_products)
check("view_all_products lists every product", all(p["name"] in out for p in gs.products))
gs.products.clear()
out = run(gs.view_all_products)
check("view_all_products handles empty store", "No products available" in out)

# ---------------- search ----------------
reset()
out = run(gs.search_product, "102")
check("search by ID finds the product", "Bread" in out and "Milk" not in out)
reset()
out = run(gs.search_product, "rice")
check("search by name ignores letter case", "Rice" in out)
reset()
out = run(gs.search_product, "mil")
check("search works with partial name", "Milk" in out)
reset()
out = run(gs.search_product, "xyz")
check("search shows message when not found", "Product not found" in out)

out = run(gs.search_product, "²")
check("search does not crash on unicode digits like ²", "Product not found" in out)

# ---------------- update stock ----------------
reset()
run(gs.update_stock, "101", "1", "5")
check("update_stock adds to existing stock", gs.products[0]["stock"] == 25)
reset()
run(gs.update_stock, "101", "2", "0")
check("update_stock can set stock to 0", gs.products[0]["stock"] == 0)
reset()
out = run(gs.update_stock, "101", "9")
check("update_stock rejects invalid choice", gs.products[0]["stock"] == 20 and "Invalid choice" in out)
reset()
out = run(gs.update_stock, "999")
check("update_stock handles unknown ID", "not found" in out)

# ---------------- sale ----------------
reset()
out = run(gs.process_sale, "101", "4")
check("sale deducts stock", gs.products[0]["stock"] == 16)
check("sale is saved in sales list",
      gs.sales == [{"product_id": 101, "product_name": "Milk", "quantity_sold": 4, "total_amount": 1000.0}])
check("sale prints correct total", "1000.00" in out)

reset()
out = run(gs.process_sale, "999")
check("sale rejects unknown product", "Product not found" in out and gs.sales == [])
reset()
out = run(gs.process_sale, "103", "10")
check("sale refused when stock is insufficient",
      "in stock. Sale cancelled" in out and gs.products[2]["stock"] == 4 and gs.sales == [])
reset()
run(gs.process_sale, "103", "4")
check("sale of exactly all stock is allowed", gs.products[2]["stock"] == 0 and len(gs.sales) == 1)
out = run(gs.process_sale, "103", "1")
check("out-of-stock product cannot be sold", "in stock. Sale cancelled" in out and len(gs.sales) == 1)

# ---------------- sales records ----------------
reset()
out = run(gs.view_sales_records)
check("sales records empty message", "No sales" in out)
run(gs.process_sale, "102", "2")
out = run(gs.view_sales_records)
check("sales records show a completed sale", "Bread" in out and "240.00" in out)

# ---------------- report ----------------
reset()
out = run(gs.generate_report)
check("report totals (products, stock, revenue)",
      "products : 4" in out and "stock    : 69" in out and "revenue generated  : 0.00" in out)
check("report shows low stock product", "Eggs" in out)
check("report shows highest and lowest price", "Rice" in out and "Bread" in out)
run(gs.process_sale, "101", "4")
out = run(gs.generate_report)
check("report counts sale and revenue", "transactions : 1" in out and "1000.00" in out)
reset()
gs.products.append({"id": 105, "name": "Salt", "category": "Spices", "price": 450, "stock": 9})
out = run(gs.generate_report)
check("report shows both products on a price tie", "Rice" in out and "Salt" in out)
gs.products.clear()
out = run(gs.generate_report)
check("report works for an empty store", "N/A" in out)

# ---------------- main menu ----------------
reset()
out = run(gs.main, "x", "8")
check("main shows error for invalid menu choice", "Invalid choice" in out)
check("main exits cleanly with option 8", "Goodbye" in out)
reset()
out = run(gs.main, "2", "8")
check("main calls the chosen option", "All Products" in out)

reset()
print()
total = passed + failed
if failed == 0:
    print(f"ALL {total} CHECKS PASSED")
else:
    print(f"{failed} of {total} CHECKS FAILED")
    sys.exit(1)
