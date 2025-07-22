# Flask Online Shop

This is a simple online shop application built with Flask and SQLite.  
It includes basic cart functionality, product management, checkout, and receipt generation.

Database is created automatically on first run.

## Features:

- Add/remove products (admin)
- Update product name/prices (admin)
- Add/remove products to/from cart (user)
- Checkout with TVA calculation
- Receipt generated in `bon.txt`
- JSON API for product CRUD

### Technologies:

- Python 3
- Flask
- SQLite3
- HTML + Jinja2 Templates

#### How to Run Locally

1. Clone the repo:
```bash
git clone https://github.com/EmanuelMihai98/online-shop-flask.git
cd online-shop-flask

2.pip install flask

3.Run the app:
  python app.py

Then open your browser at:
------> http://127.0.0.1:5000/

##### Project Structure:
	app.py
	products.db
	templates/
    		index.html
    		cart.html
    		checkout.html
    		thank_you.html
   		add_product.html
	bon.txt
	README.md

###### API Routes:
	
	GET /api/products

	GET /api/products/<name>

	POST /api/products

	PUT /api/products/<name>

	DELETE /api/products/<name>
