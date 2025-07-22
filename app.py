from flask import Flask,jsonify,render_template,request,redirect, url_for
import sqlite3

app = Flask(__name__)

cart = {}

def get_products():
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT exists products (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT UNIQUE,
                   price INTEGER)""")
    cursor.execute("SELECT name, price FROM products")
    products = dict(cursor.fetchall())
    conn.close()
    return dict(products)

def insert_sample_products():
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        price INTEGER)""")
    
    sample = [("pork", 10), ("bacon", 5), ("water", 12), ("cola", 11)]
    for name, price in sample:
        try:
            cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        except sqlite3.IntegrityError:
            continue
    conn.commit()
    conn.close()

insert_sample_products()
@app.route("/add", methods=["GET", "POST"])
def add_product_to_db():
    if request.method == "POST":
        name = request.form["name"].lower()
        price = int(request.form["price"])

        conn = sqlite3.connect("products.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()

        return redirect(url_for("main"))
    return render_template("add_product.html")

@app.route("/delete/<name>")
def delete_product(name):
    conn =sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    return redirect(url_for("main"))


@app.route("/update/<name>", methods=["POST"])
def update_price(name):
    new_price = request.form["new_price"]

    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET price = ? WHERE LOWER(name) = ?", (int(new_price), name.lower()))
    conn.commit()
    conn.close()

    return redirect(url_for("main"))


@app.route("/")
def main():
    products = get_products()
    return render_template("index.html", products=products, is_admin=True)

@app.route("/add-to-cart", methods=["POST"])
def add_product():
    product=request.form["product"].lower()
    products = get_products()
    if product in products:
        if product in cart:
            cart[product] += 1
        else:
            cart[product] = 1
    return redirect(url_for("show_cart"))

@app.route("/show-cart")
def show_cart():
    return render_template("cart.html", cart=cart)

@app.route("/remove/<product>")
def remove(product):
    if product in cart:
        if cart[product] > 1:
            cart[product] -= 1
        else:
            del cart[product]

    return redirect(url_for("show_cart"))

@app.route("/check-out")
def checkout():
    products = get_products()
    total_general= 0
    receipt_lines= []
    if not cart:
        return redirect(url_for("main"))
    for product, amount in cart.items():
        unit_price= products[product]
        subtotal=unit_price * amount
        tva= subtotal * 19 / 100
        total= subtotal + tva
        total_general += total
        print(f"{product} x{amount}= {subtotal:.2f} $, with TVA 19%={total:.2f} $")
        receipt_lines.append({
            "product": product,
            "amount": amount,
            "unit_price":unit_price,
            "subtotal":subtotal,
            "tva":tva,
            "total":total
        })
    return render_template("checkout.html", total_general=total_general, receipt_lines=receipt_lines)
    

@app.route("/payment")
def pay():
    print("\n ### RECEIPT ###")
    products = get_products()
    total_general=0
    with open("bon.txt", "w") as f:
        for product, amount in cart.items():
            unit_price= products[product]
            subtotal=unit_price * amount
            tva= subtotal * 19 / 100
            total= subtotal + tva
            total_general += total
            f.write(f"{product} x{amount}= {subtotal:.2f} $, with TVA 19%={total:.2f} $")
        f.write(f"\nReceipt with TVA 19%={total_general:.2f} $") 
    
    cart.clear()
    return redirect(url_for("thank_you"))

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

@app.route("/api/products", methods=["GET"])
def api_get_products():
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("Select name, price FROM products")
    products = cursor.fetchall()
    conn.close()
    return jsonify(dict(products))

@app.route("/api/products/<name>", methods=["GET"])
def api_get_product(name):
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM products WHERE name = ?", (name.lower(),))
    result = cursor.fetchone()
    conn.close()
    if result:
        return jsonify({name: result[0]})
    else:
        return jsonify({"error": "Product not found"}), 404


@app.route("/api/products", methods=["POST"])
def api_add_products():
    data = request.get_json()
    name = data.get("name", "").strip().lower()
    price = data.get("price")
    if not name or not isinstance(price, int):
        return jsonify({"error": "Invalid product"}), 400
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        return jsonify({"message": "Product added"}), 201 
    except sqlite3.IntegrityError:
        return jsonify({"error": "Product already exists"}), 409
    finally:
        conn.close()

@app.route("/api/products/<name>", methods=["PUT"])
def api_update_product(name):
    data = request.get_json()
    new_name = data.get("new_name", "").strip().lower()
    new_price = data.get("new_price")

    if not new_name or not isinstance(new_price, int):
        return jsonify({"error": "Invalid input"}), 400
    
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE LOWER(name) = ?", (name.lower(),))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return jsonify({"error": "Product not found"}), 404
    
    try:
        cursor.execute("UPDATE products SET name = ?, price = ? WHERE LOWER(name) = ?", (new_name, new_price, name.lower()))
        conn.commit()
        return jsonify({"message": "Product updated"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "New name already exists"}), 409
    finally:
        conn.close()

@app.route("/api/products/<name>", methods=["DELETE"])
def api_delete_product(name):
    conn = sqlite3.connect("products.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE LOWER(name) = ?", (name.lower(),))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({"error": "Product not found"}), 404
    
    cursor.execute("DELETE FROM products WHERE LOWER(name) = ?", (name.lower(),))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Product deleted"}), 200


if __name__ == "__main__":
    app.run(debug=True)