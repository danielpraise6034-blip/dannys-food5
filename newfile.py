from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import sqlite3
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Secret key for user sessions
app.secret_key = os.environ.get("SECRET_KEY")

DATABASE = "danny_food.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            items TEXT NOT NULL,
            total INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================
# FOOD MENU
# =========================

MENU = [
    {
        "id": 1,
        "name": "Jollof Rice",
        "category": "Rice",
        "price": 2500,
        "image": "https://loremflickr.com/600/400/jollof,rice"
    },
    {
        "id": 2,
        "name": "Fried Rice",
        "category": "Rice",
        "price": 2800,
        "image": "https://loremflickr.com/600/400/fried,rice,nigeria"
    },
    {
        "id": 3,
        "name": "White Rice & Stew",
        "category": "Rice",
        "price": 2500,
        "image": "https://loremflickr.com/600/400/rice,stew,nigeria"
    },
    {
        "id": 4,
        "name": "Pounded Yam",
        "category": "Swallow",
        "price": 1500,
        "image": "https://loremflickr.com/600/400/pounded,yam,nigeria"
    },
    {
        "id": 5,
        "name": "Eba",
        "category": "Swallow",
        "price": 1000,
        "image": "https://loremflickr.com/600/400/eba,nigeria"
    },
    {
        "id": 6,
        "name": "Amala",
        "category": "Swallow",
        "price": 1200,
        "image": "https://loremflickr.com/600/400/amala,nigeria"
    },
    {
        "id": 7,
        "name": "Egusi Soup",
        "category": "Soups",
        "price": 2500,
        "image": "https://loremflickr.com/600/400/egusi,soup,nigeria"
    },
    {
        "id": 8,
        "name": "Ogbono Soup",
        "category": "Soups",
        "price": 2500,
        "image": "https://loremflickr.com/600/400/ogbono,soup,nigeria"
    },
    {
        "id": 9,
        "name": "Okra Soup",
        "category": "Soups",
        "price": 2200,
        "image": "https://loremflickr.com/600/400/okra,soup,nigeria"
    },
    {
        "id": 10,
        "name": "Fried Chicken",
        "category": "Protein",
        "price": 2500,
        "image": "https://loremflickr.com/600/400/fried,chicken,nigeria"
    },
    {
        "id": 11,
        "name": "Goat Meat",
        "category": "Protein",
        "price": 2000,
        "image": "https://loremflickr.com/600/400/goat,meat,nigeria"
    },
    {
        "id": 12,
        "name": "Fried Fish",
        "category": "Protein",
        "price": 3000,
        "image": "https://loremflickr.com/600/400/fried,fish,nigeria"
    }
]
# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():
    logged_in = "user_id" in session
    name = session.get("name")

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Danny's Food</title>

    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: Arial, sans-serif;
            background: #f5f7fb;
            color: #222;
        }

        .hero {
            min-height: 100vh;
            background: linear-gradient(135deg, #0756a8, #0b82d8);
            position: relative;
            overflow: hidden;
            padding: 25px;
        }

        nav {
            max-width: 1100px;
            margin: auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
        }

        .logo {
            font-size: 25px;
            font-weight: bold;
        }

        .nav-links {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .nav-links a {
            color: white;
            text-decoration: none;
            padding: 10px 15px;
            border-radius: 8px;
            background: rgba(255,255,255,0.15);
        }

        .content {
            max-width: 900px;
            margin: 100px auto 0;
            text-align: center;
            color: white;
            position: relative;
            z-index: 2;
        }

        .content h1 {
            font-size: 55px;
            margin-bottom: 15px;
        }

        .content p {
            font-size: 20px;
            margin-bottom: 30px;
        }

        .buttons {
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }

        .btn {
            display: inline-block;
            text-decoration: none;
            padding: 14px 25px;
            border-radius: 10px;
            font-weight: bold;
            background: white;
            color: #0756a8;
        }

        .btn.orange {
            background: #ff8c00;
            color: white;
        }

        .welcome {
            background: rgba(255,255,255,0.15);
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 25px;
        }

        .food {
            position: absolute;
            font-size: 55px;
            opacity: 0.25;
            animation: float 4s ease-in-out infinite;
        }

        .food1 { top: 20%; left: 5%; }
        .food2 { top: 65%; left: 10%; }
        .food3 { top: 25%; right: 7%; }
        .food4 { top: 70%; right: 10%; }
        .food5 { top: 45%; left: 3%; }
        .food6 { top: 50%; right: 3%; }

        @keyframes float {
            0%, 100% {
                transform: translateY(0);
            }

            50% {
                transform: translateY(-20px);
            }
        }

        @media (max-width: 600px) {
            .content h1 {
                font-size: 40px;
            }

            nav {
                align-items: flex-start;
                gap: 15px;
                flex-direction: column;
            }
        }
    </style>
</head>

<body>

<div class="hero">

    <nav>
        <div class="logo">🍴 Danny's Food</div>

        <div class="nav-links">

            {% if logged_in %}
                <a href="{{ url_for('menu') }}">Menu</a>
                <a href="{{ url_for('my_orders') }}">My Orders</a>
                <a href="{{ url_for('logout') }}">Logout</a>
            {% else %}
                <a href="{{ url_for('login') }}">Login</a>
                <a href="{{ url_for('register') }}">Create Account</a>
            {% endif %}

        </div>
    </nav>


    <div class="content">

        {% if logged_in %}

            <div class="welcome">
                Welcome back, {{ name }} 👋
            </div>

        {% endif %}

        <h1>Good Food.<br>Great Taste.</h1>

        <p>
            Delicious Nigerian meals delivered to you.
        </p>

        <div class="buttons">

            <a class="btn orange"
               href="{{ url_for('menu') }}">
                🍽️ Order Food
            </a>

            {% if not logged_in %}

                <a class="btn"
                   href="{{ url_for('register') }}">
                    Create Account
                </a>

            {% endif %}

        </div>

    </div>


    <div class="food food1">🍔</div>
    <div class="food food2">🍕</div>
    <div class="food food3">🍗</div>
    <div class="food food4">🍟</div>
    <div class="food food5">🍛</div>
    <div class="food food6">🥤</div>

</div>

</body>
</html>
""", logged_in=logged_in, name=name)


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return render_template_string("""
                <h2>All fields are required.</h2>
                <a href="/register">Go back</a>
            """)

        if len(password) < 6:
            return render_template_string("""
                <h2>Password must be at least 6 characters.</h2>
                <a href="/register">Go back</a>
            """)

        conn = get_db()

        try:
            hashed_password = generate_password_hash(password)

            conn.execute(
                """
                INSERT INTO users (name, email, password)
                VALUES (?, ?, ?)
                """,
                (name, email, hashed_password)
            )

            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()

            return render_template_string("""
                <h2>Email already exists.</h2>
                <a href="/login">Login instead</a>
            """)

        conn.close()

        return redirect(url_for("login"))


    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Create Account - Danny's Food</title>

    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #0756a8, #0b82d8);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .box {
            background: white;
            width: 100%;
            max-width: 420px;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        h1 {
            text-align: center;
            margin-bottom: 25px;
        }

        input {
            width: 100%;
            padding: 13px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }

        button {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 8px;
            background: #0756a8;
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }

        p {
            text-align: center;
            margin-top: 20px;
        }

        a {
            color: #0756a8;
        }
    </style>
</head>

<body>

<div class="box">

    <h1>🍴 Create Account</h1>

    <form method="POST">

        <input
            type="text"
            name="name"
            placeholder="Your name"
            required
        >

        <input
            type="email"
            name="email"
            placeholder="Email address"
            required
        >

        <input
            type="password"
            name="password"
            placeholder="Password"
            minlength="6"
            required
        >

        <button type="submit">
            Create Account
        </button>

    </form>

    <p>
        Already have an account?
        <a href="{{ url_for('login') }}">Login</a>
    </p>

    <p>
        <a href="{{ url_for('home') }}">← Back Home</a>
    </p>

</div>

</body>
</html>
""")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["name"] = user["name"]

            return redirect(url_for("home"))

        return render_template_string("""
            <h2>Invalid email or password.</h2>
            <a href="/login">Try again</a>
        """)


    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Login - Danny's Food</title>

    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #0756a8, #0b82d8);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .box {
            background: white;
            width: 100%;
            max-width: 420px;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        h1 {
            text-align: center;
            margin-bottom: 25px;
        }

        input {
            width: 100%;
            padding: 13px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }

        button {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 8px;
            background: #0756a8;
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }

        p {
            text-align: center;
            margin-top: 20px;
        }

        a {
            color: #0756a8;
        }
    </style>
</head>

<body>

<div class="box">

    <h1>🍴 Login</h1>

    <form method="POST">

        <input
            type="email"
            name="email"
            placeholder="Email address"
            required
        >

        <input
            type="password"
            name="password"
            placeholder="Password"
            required
        >

        <button type="submit">
            Login
        </button>

    </form>

    <p>
        Don't have an account?
        <a href="{{ url_for('register') }}">Create Account</a>
    </p>

    <p>
        <a href="{{ url_for('home') }}">← Back Home</a>
    </p>

</div>

</body>
</html>
""")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.pop("user_id", None)
    session.pop("name", None)

    return redirect(url_for("home"))
    # =========================
# MENU PAGE
# =========================

@app.route("/menu")
def menu():

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>

    <title>Menu - Danny's Food</title>

    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f5f7fb;
            color: #222;
        }

        nav {
            background: #0756a8;
            color: white;
            padding: 15px 20px;

            display: flex;
            justify-content: space-between;
            align-items: center;

            position: sticky;
            top: 0;
            z-index: 100;
        }

        .logo {
            font-size: 22px;
            font-weight: bold;
        }

        .nav-links {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .nav-links a {
            color: white;
            text-decoration: none;
            padding: 8px 12px;
            border-radius: 7px;
            background: rgba(255,255,255,0.15);
        }

        .cart-button {
            background: #ff8c00;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
        }

        .container {
            max-width: 1200px;
            margin: auto;
            padding: 30px 20px;
        }

        h1 {
            text-align: center;
            margin-bottom: 10px;
        }

        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 25px;
        }

        .search-box {
            max-width: 600px;
            margin: 0 auto 20px;
        }

        .search-box input {
            width: 100%;
            padding: 14px;
            border: 1px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
        }

        .categories {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }

        .category-btn {
            border: none;
            background: white;
            padding: 10px 16px;
            border-radius: 20px;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        .category-btn.active {
            background: #0756a8;
            color: white;
        }

        .food-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
        }

        .food-card {
            background: white;
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: transform 0.2s;
        }

        .food-card:hover {
            transform: translateY(-4px);
        }

        .food-card img {
            width: 100%;
            height: 180px;
            object-fit: cover;
        }

        .food-info {
            padding: 18px;
        }

        .food-info h3 {
            margin: 0 0 8px;
        }

        .category {
            color: #777;
            font-size: 14px;
            margin-bottom: 10px;
        }

        .price {
            color: #0756a8;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 15px;
        }

        .add-btn {
            width: 100%;
            border: none;
            background: #ff8c00;
            color: white;
            padding: 12px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }

        .add-btn:hover {
            background: #e67d00;
        }

        .cart-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.55);
            z-index: 200;
        }

        .cart {
            position: absolute;
            right: 0;
            top: 0;
            height: 100%;
            width: min(420px, 100%);
            background: white;
            padding: 25px;
            overflow-y: auto;
        }

        .cart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .close-cart {
            border: none;
            background: #eee;
            border-radius: 50%;
            width: 35px;
            height: 35px;
            cursor: pointer;
            font-size: 18px;
        }

        .cart-item {
            border-bottom: 1px solid #eee;
            padding: 15px 0;
        }

        .cart-item-top {
            display: flex;
            justify-content: space-between;
            gap: 10px;
        }

        .quantity-controls {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 10px;
        }

        .quantity-controls button {
            border: none;
            background: #0756a8;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 6px;
            cursor: pointer;
        }

        .remove-btn {
            border: none;
            background: #eee;
            color: #d00;
            padding: 5px 8px;
            border-radius: 5px;
            cursor: pointer;
        }

        .cart-total {
            font-size: 22px;
            font-weight: bold;
            margin: 20px 0;
        }

        .checkout-btn {
            width: 100%;
            padding: 14px;
            background: #0756a8;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            font-size: 16px;
        }

        .clear-btn {
            width: 100%;
            padding: 12px;
            margin-top: 10px;
            background: #eee;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }

        .empty-cart {
            text-align: center;
            color: #777;
            padding: 40px 10px;
        }

    </style>

</head>

<body>


<nav>

    <div class="logo">
        🍴 Danny's Food
    </div>

    <div class="nav-links">

        <a href="{{ url_for('home') }}">
            Home
        </a>

        {% if session.get("user_id") %}
            <a href="{{ url_for('my_orders') }}">
                My Orders
            </a>
        {% endif %}

        <button class="cart-button" onclick="showCart()">
            🛒 Cart (<span id="cartCount">0</span>)
        </button>

    </div>

</nav>


<div class="container">

    <h1>🍽️ Our Menu</h1>

    <p class="subtitle">
        Choose your favourite meal.
    </p>


    <div class="search-box">

        <input
            type="text"
            id="searchInput"
            placeholder="🔎 Search for food..."
            oninput="filterFoods()"
        >

    </div>


    <div class="categories">

        <button
            class="category-btn active"
            onclick="selectCategory('All', this)"
        >
            All
        </button>

        <button
            class="category-btn"
            onclick="selectCategory('Rice', this)"
        >
            Rice
        </button>

        <button
            class="category-btn"
            onclick="selectCategory('Swallow', this)"
        >
            Swallow
        </button>

        <button
            class="category-btn"
            onclick="selectCategory('Soups', this)"
        >
            Soups
        </button>

        <button
            class="category-btn"
            onclick="selectCategory('Protein', this)"
        >
            Protein
        </button>

    </div>


    <div class="food-grid" id="foodGrid">

        {% for food in menu %}

        <div
            class="food-card"
            data-name="{{ food.name|lower }}"
            data-category="{{ food.category }}"
        >

            <img
                src="{{ food.image }}"
                alt="{{ food.name }}"
                onerror="this.src='https://placehold.co/600x400?text=Food+Image'"
            >

            <div class="food-info">

                <h3>
                    {{ food.name }}
                </h3>

                <div class="category">
                    {{ food.category }}
                </div>

                <div class="price">
                    ₦{{ "{:,}".format(food.price) }}
                </div>

                <button
                    class="add-btn"
                    onclick='addToCart({{ food|tojson }})'
                >
                    Add to Cart
                </button>

            </div>

        </div>

        {% endfor %}

    </div>

</div>


<!-- CART -->

<div
    class="cart-overlay"
    id="cartOverlay"
    onclick="closeCartOutside(event)"
>

    <div
        class="cart"
        onclick="event.stopPropagation()"
    >

        <div class="cart-header">

            <h2>🛒 Your Cart</h2>

            <button
                class="close-cart"
                onclick="closeCart()"
            >
                ×
            </button>

        </div>


        <div id="cartItems"></div>


        <div class="cart-total">

            Total:
            ₦<span id="cartTotal">0</span>

        </div>


        <button
            class="checkout-btn"
            onclick="checkout()"
        >
            Proceed to Checkout
        </button>


        <button
            class="clear-btn"
            onclick="clearCart()"
        >
            Clear Cart
        </button>

    </div>

</div>


<script>

let cart = JSON.parse(
    localStorage.getItem("danny_cart") || "[]"
);

let selectedCategory = "All";


function saveCart() {

    localStorage.setItem(
        "danny_cart",
        JSON.stringify(cart)
    );

    updateCartCount();

}


function updateCartCount() {

    let count = cart.reduce(
        (total, item) => total + item.quantity,
        0
    );

    document.getElementById("cartCount").textContent = count;

}


function addToCart(food) {

    let existingItem = cart.find(
        item => item.id === food.id
    );

    if (existingItem) {

        existingItem.quantity += 1;

    } else {

        cart.push({
            id: food.id,
            name: food.name,
            category: food.category,
            price: food.price,
            quantity: 1
        });

    }

    saveCart();

    alert(food.name + " added to cart!");

}


function increaseQuantity(id) {

    let item = cart.find(
        item => item.id === id
    );

    if (item) {

        item.quantity += 1;

    }

    saveCart();

    showCart();

}


function decreaseQuantity(id) {

    let item = cart.find(
        item => item.id === id
    );

    if (!item) {
        return;
    }

    item.quantity -= 1;

    if (item.quantity <= 0) {

        cart = cart.filter(
            item => item.id !== id
        );

    }

    saveCart();

    showCart();

}


function removeItem(id) {

    cart = cart.filter(
        item => item.id !== id
    );

    saveCart();

    showCart();

}


function clearCart() {

    if (cart.length === 0) {
        return;
    }

    cart = [];

    saveCart();

    showCart();

}


function showCart() {

    document.getElementById(
        "cartOverlay"
    ).style.display = "block";


    let container =
        document.getElementById("cartItems");


    if (cart.length === 0) {

        container.innerHTML = `
            <div class="empty-cart">
                Your cart is empty 🛒
            </div>
        `;

        document.getElementById(
            "cartTotal"
        ).textContent = "0";

        return;
    }


    let total = 0;


    container.innerHTML = cart.map(item => {

        let itemTotal =
            item.price * item.quantity;

        total += itemTotal;


        return `
            <div class="cart-item">

                <div class="cart-item-top">

                    <div>

                        <strong>
                            ${item.name}
                        </strong>

                        <div>
                            ₦${item.price.toLocaleString()}
                        </div>

                    </div>

                    <button
                        class="remove-btn"
                        onclick="removeItem(${item.id})"
                    >
                        Remove
                    </button>

                </div>


                <div class="quantity-controls">

                    <button
                        onclick="decreaseQuantity(${item.id})"
                    >
                        -
                    </button>

                    <strong>
                        ${item.quantity}
                    </strong>

                    <button
                        onclick="increaseQuantity(${item.id})"
                    >
                        +
                    </button>

                    <strong>
                        ₦${itemTotal.toLocaleString()}
                    </strong>

                </div>

            </div>
        `;

    }).join("");


    document.getElementById(
        "cartTotal"
    ).textContent = total.toLocaleString();

}


function closeCart() {

    document.getElementById(
        "cartOverlay"
    ).style.display = "none";

}


function closeCartOutside(event) {

    if (
        event.target.id === "cartOverlay"
    ) {

        closeCart();

    }

}


function selectCategory(category, button) {

    selectedCategory = category;


    document.querySelectorAll(
        ".category-btn"
    ).forEach(btn => {

        btn.classList.remove("active");

    });


    button.classList.add("active");


    filterFoods();

}


function filterFoods() {

    let search =
        document.getElementById(
            "searchInput"
        ).value.toLowerCase().trim();


    document.querySelectorAll(
        ".food-card"
    ).forEach(card => {

        let name =
            card.dataset.name;

        let category =
            card.dataset.category;


        let matchesSearch =
            name.includes(search);


        let matchesCategory =
            selectedCategory === "All"
            ||
            category === selectedCategory;


        if (
            matchesSearch &&
            matchesCategory
        ) {

            card.style.display = "";

        } else {

            card.style.display = "none";

        }

    });

}


function checkout() {

    if (cart.length === 0) {

        alert("Your cart is empty.");

        return;

    }


    window.location.href =
        "{{ url_for('checkout') }}";

}


updateCartCount();

</script>

</body>
</html>
""", menu=MENU)
# =========================
# CHECKOUT
# =========================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        items_json = request.form.get("items", "")

        if not phone or not address or not items_json:
            return render_template_string("""
                <h2>Please fill in all the required information.</h2>
                <a href="/checkout">Go back</a>
            """)

        try:
            cart = json.loads(items_json)
        except (json.JSONDecodeError, TypeError):
            return render_template_string("""
                <h2>Invalid cart.</h2>
                <a href="/menu">Return to Menu</a>
            """)

        if not isinstance(cart, list) or len(cart) == 0:
            return render_template_string("""
                <h2>Your cart is empty.</h2>
                <a href="/menu">Return to Menu</a>
            """)

        # Calculate the total from our trusted MENU.
        # We do NOT trust the price sent by the browser.
        menu_lookup = {
            food["id"]: food
            for food in MENU
        }

        order_items = []
        total = 0

        for item in cart:

            try:
                food_id = int(item.get("id"))
                quantity = int(item.get("quantity"))
            except (TypeError, ValueError):
                continue

            if food_id not in menu_lookup:
                continue

            if quantity < 1 or quantity > 50:
                continue

            food = menu_lookup[food_id]

            item_total = food["price"] * quantity
            total += item_total

            order_items.append({
                "id": food["id"],
                "name": food["name"],
                "quantity": quantity,
                "price": food["price"]
            })

        if not order_items:
            return render_template_string("""
                <h2>Your cart contains invalid items.</h2>
                <a href="/menu">Return to Menu</a>
            """)

        conn = get_db()

        cursor = conn.execute(
            """
            INSERT INTO orders
            (user_id, phone, address, items, total, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                phone,
                address,
                json.dumps(order_items),
                total,
                "Pending"
            )
        )

        order_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "order_success",
                order_id=order_id
            )
        )


    return render_template_string("""
<!DOCTYPE html>
<html>

<head>

    <title>Checkout - Danny's Food</title>

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f5f7fb;
            color: #222;
        }

        nav {
            background: #0756a8;
            color: white;
            padding: 15px 20px;

            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        nav a {
            color: white;
            text-decoration: none;
        }

        .logo {
            font-size: 22px;
            font-weight: bold;
        }

        .container {
            max-width: 900px;
            margin: 30px auto;
            padding: 20px;
        }

        .box {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.07);
        }

        h1 {
            text-align: center;
            margin-bottom: 25px;
        }

        h2 {
            margin-top: 0;
        }

        .order-item {
            display: flex;
            justify-content: space-between;
            gap: 15px;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }

        .total {
            display: flex;
            justify-content: space-between;
            font-size: 22px;
            font-weight: bold;
            margin-top: 20px;
        }

        label {
            display: block;
            margin-bottom: 7px;
            font-weight: bold;
        }

        input,
        textarea {
            width: 100%;
            padding: 13px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 18px;
        }

        textarea {
            min-height: 100px;
            resize: vertical;
        }

        button {
            width: 100%;
            padding: 14px;
            background: #ff8c00;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }

        .back {
            display: block;
            text-align: center;
            margin-top: 15px;
            color: #0756a8;
            text-decoration: none;
        }

        .empty {
            text-align: center;
            padding: 40px;
        }

    </style>

</head>

<body>

<nav>

    <div class="logo">
        🍴 Danny's Food
    </div>

    <a href="{{ url_for('menu') }}">
        ← Menu
    </a>

</nav>


<div class="container">

    <h1>🧾 Checkout</h1>


    <div class="box">

        <h2>Your Order</h2>

        <div id="orderItems"></div>

        <div class="total">

            <span>Total</span>

            <span>
                ₦<span id="orderTotal">0</span>
            </span>

        </div>

    </div>


    <div class="box">

        <h2>Delivery Information</h2>

        <form method="POST" id="checkoutForm">

            <label>
                Phone Number
            </label>

            <input
                type="tel"
                name="phone"
                placeholder="e.g. 08012345678"
                required
            >


            <label>
                Delivery Address
            </label>

            <textarea
                name="address"
                placeholder="Enter the address where you want your food delivered"
                required
            ></textarea>


            <input
                type="hidden"
                name="items"
                id="itemsInput"
            >


            <button type="submit">
                Place Order
            </button>

        </form>


        <a
            class="back"
            href="{{ url_for('menu') }}"
        >
            ← Back to Menu
        </a>

    </div>

</div>


<script>

const cart = JSON.parse(
    localStorage.getItem("danny_cart") || "[]"
);


const orderItems =
    document.getElementById("orderItems");

const orderTotal =
    document.getElementById("orderTotal");

const itemsInput =
    document.getElementById("itemsInput");


if (cart.length === 0) {

    orderItems.innerHTML = `
        <div class="empty">
            Your cart is empty.
            <br><br>
            <a href="/menu">
                Return to Menu
            </a>
        </div>
    `;

} else {

    let total = 0;


    cart.forEach(item => {

        const itemTotal =
            item.price * item.quantity;

        total += itemTotal;


        const div =
            document.createElement("div");

        div.className = "order-item";


        div.innerHTML = `
            <div>
                <strong>
                    ${item.name}
                </strong>

                <br>

                ${item.quantity} ×
                ₦${item.price.toLocaleString()}
            </div>

            <strong>
                ₦${itemTotal.toLocaleString()}
            </strong>
        `;


        orderItems.appendChild(div);

    });


    orderTotal.textContent =
        total.toLocaleString();


    itemsInput.value =
        JSON.stringify(cart);

}


document.getElementById(
    "checkoutForm"
).addEventListener(
    "submit",
    function(event) {

        if (cart.length === 0) {

            event.preventDefault();

            alert(
                "Your cart is empty."
            );

        }

    }
);

</script>

</body>

</html>
""")
# =========================
# ORDER SUCCESS
# =========================

@app.route("/order-success/<int:order_id>")
def order_success(order_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    order = conn.execute(
        """
        SELECT *
        FROM orders
        WHERE id = ? AND user_id = ?
        """,
        (order_id, session["user_id"])
    ).fetchone()

    conn.close()

    if not order:
        return render_template_string("""
            <h2>Order not found.</h2>
            <a href="/menu">Return to Menu</a>
        """)

    return render_template_string("""
<!DOCTYPE html>
<html>

<head>

    <title>Order Confirmed - Danny's Food</title>

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <style>

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f5f7fb;

            display: flex;
            justify-content: center;
            align-items: center;

            min-height: 100vh;
            padding: 20px;
        }

        .box {
            background: white;
            width: 100%;
            max-width: 500px;

            padding: 35px;
            border-radius: 16px;

            text-align: center;

            box-shadow:
                0 5px 20px rgba(0,0,0,0.08);
        }

        .check {
            font-size: 60px;
            margin-bottom: 15px;
        }

        h1 {
            color: #0756a8;
            margin-bottom: 10px;
        }

        .order-number {
            background: #f0f6ff;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }

        .status {
            display: inline-block;

            background: #fff3cd;
            color: #856404;

            padding: 8px 15px;

            border-radius: 20px;

            font-weight: bold;
        }

        .total {
            font-size: 24px;
            font-weight: bold;

            margin: 20px 0;
        }

        .buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .btn {
            flex: 1;

            min-width: 150px;

            padding: 13px;

            border-radius: 8px;

            text-decoration: none;

            font-weight: bold;
        }

        .primary {
            background: #0756a8;
            color: white;
        }

        .secondary {
            background: #eee;
            color: #222;
        }

    </style>

</head>

<body>

<div class="box">

    <div class="check">
        ✅
    </div>

    <h1>
        Order Placed!
    </h1>

    <p>
        Thank you for ordering from
        <strong>Danny's Food</strong>.
    </p>


    <div class="order-number">

        <strong>
            Order Number
        </strong>

        <br><br>

        #{{ order["id"] }}

    </div>


    <div>

        Status:

        <span class="status">
            {{ order["status"] }}
        </span>

    </div>


    <div class="total">

        ₦{{ "{:,}".format(order["total"]) }}

    </div>


    <div class="buttons">

        <a
            class="btn primary"
            href="{{ url_for('my_orders') }}"
        >
            📦 My Orders
        </a>

        <a
            class="btn secondary"
            href="{{ url_for('menu') }}"
        >
            🍽️ Order More
        </a>

    </div>

</div>


<script>

localStorage.removeItem("danny_cart");

</script>

</body>

</html>
""", order=order)


# =========================
# MY ORDERS
# =========================

@app.route("/my-orders")
def my_orders():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    orders = conn.execute(
        """
        SELECT *
        FROM orders
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()


    prepared_orders = []

    for order in orders:

        try:
            items = json.loads(order["items"])
        except (json.JSONDecodeError, TypeError):
            items = []

        prepared_orders.append({
            "id": order["id"],
            "phone": order["phone"],
            "address": order["address"],
            "items": items,
            "total": order["total"],
            "status": order["status"]
        })


    return render_template_string("""
<!DOCTYPE html>
<html>

<head>

    <title>My Orders - Danny's Food</title>

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f5f7fb;
            color: #222;
        }

        nav {
            background: #0756a8;
            color: white;

            padding: 15px 20px;

            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        nav a {
            color: white;
            text-decoration: none;
        }

        .logo {
            font-size: 22px;
            font-weight: bold;
        }

        .container {
            max-width: 900px;
            margin: auto;
            padding: 30px 20px;
        }

        h1 {
            text-align: center;
            margin-bottom: 25px;
        }

        .order {
            background: white;

            padding: 20px;
            margin-bottom: 20px;

            border-radius: 14px;

            box-shadow:
                0 4px 15px rgba(0,0,0,0.07);
        }

        .order-header {
            display: flex;
            justify-content: space-between;
            align-items: center;

            gap: 10px;

            border-bottom: 1px solid #eee;

            padding-bottom: 15px;
            margin-bottom: 15px;
        }

        .order-number {
            font-size: 18px;
            font-weight: bold;
        }

        .status {
            padding: 7px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
        }

        .pending {
            background: #fff3cd;
            color: #856404;
        }

        .preparing {
            background: #cfe2ff;
            color: #084298;
        }

        .delivery {
            background: #d1e7dd;
            color: #0f5132;
        }

        .delivered {
            background: #d1e7dd;
            color: #0f5132;
        }

        .cancelled {
            background: #f8d7da;
            color: #842029;
        }

        .food-row {
            display: flex;
            justify-content: space-between;

            padding: 8px 0;
        }

        .total {
            border-top: 1px solid #eee;

            margin-top: 15px;
            padding-top: 15px;

            display: flex;
            justify-content: space-between;

            font-size: 20px;
            font-weight: bold;
        }

        .details {
            margin-top: 15px;
            color: #666;
            line-height: 1.6;
        }

        .empty {
            background: white;
            padding: 40px;
            border-radius: 14px;
            text-align: center;
        }

        .btn {
            display: inline-block;

            background: #ff8c00;
            color: white;

            padding: 12px 20px;

            border-radius: 8px;

            text-decoration: none;
            font-weight: bold;

            margin-top: 15px;
        }

        @media (max-width: 600px) {

            .order-header {
                align-items: flex-start;
                flex-direction: column;
            }

        }

    </style>

</head>

<body>

<nav>

    <div class="logo">
        🍴 Danny's Food
    </div>

    <a href="{{ url_for('menu') }}">
        🍽️ Menu
    </a>

</nav>


<div class="container">

    <h1>
        📦 My Orders
    </h1>


    {% if orders %}

        {% for order in orders %}

        <div class="order">

            <div class="order-header">

                <div class="order-number">

                    Order #{{ order.id }}

                </div>


                <div
                    class="status
                    {% if order.status == 'Pending' %}
                        pending
                    {% elif order.status == 'Preparing' %}
                        preparing
                    {% elif order.status == 'Out for Delivery' %}
                        delivery
                    {% elif order.status == 'Delivered' %}
                        delivered
                    {% elif order.status == 'Cancelled' %}
                        cancelled
                    {% endif %}
                    "
                >

                    {{ order.status }}

                </div>

            </div>


            <h3>
                Food Ordered
            </h3>


            {% for item in order.items %}

            <div class="food-row">

                <span>

                    {{ item.name }}

                    × {{ item.quantity }}

                </span>

                <strong>

                    ₦{{ "{:,}".format(
                        item.price * item.quantity
                    ) }}

                </strong>

            </div>

            {% endfor %}


            <div class="total">

                <span>
                    Total
                </span>

                <span>
                    ₦{{ "{:,}".format(order.total) }}
                </span>

            </div>


            <div class="details">

                📞 {{ order.phone }}

                <br>

                📍 {{ order.address }}

            </div>

        </div>

        {% endfor %}

    {% else %}

        <div class="empty">

            <h2>
                You haven't placed any orders yet.
            </h2>

            <p>
                Your orders will appear here.
            </p>

            <a
                class="btn"
                href="{{ url_for('menu') }}"
            >
                🍽️ Browse Menu
            </a>

        </div>

    {% endif %}

</div>

</body>

</html>
""", orders=prepared_orders)
# =========================
# ADMIN SETTINGS
# =========================

ADMIN_EMAIL = os.environ.get(
    "ADMIN_EMAIL",
    "admin@dannysfood.com"
)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


# =========================
# ADMIN LOGIN
# =========================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        if (
            email == ADMIN_EMAIL.lower()
            and password == ADMIN_PASSWORD
        ):

            session["admin"] = True

            return redirect(
                url_for("admin")
            )

        return render_template_string("""
            <h2>Invalid admin login.</h2>
            <a href="/admin-login">
                Try again
            </a>
        """)


    return render_template_string("""
<!DOCTYPE html>
<html>

<head>

    <title>Admin Login - Danny's Food</title>

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <style>

        body {
            margin: 0;
            font-family: Arial, sans-serif;

            background:
                linear-gradient(
                    135deg,
                    #0756a8,
                    #0b82d8
                );

            min-height: 100vh;

            display: flex;
            justify-content: center;
            align-items: center;

            padding: 20px;
        }

        .box {
            background: white;

            width: 100%;
            max-width: 420px;

            padding: 30px;

            border-radius: 15px;

            box-shadow:
                0 10px 30px rgba(0,0,0,0.2);
        }

        h1 {
            text-align: center;
            margin-bottom: 25px;
        }

        input {
            width: 100%;

            padding: 13px;

            margin-bottom: 15px;

            border: 1px solid #ddd;
            border-radius: 8px;

            font-size: 16px;

            box-sizing: border-box;
        }

        button {
            width: 100%;

            padding: 14px;

            border: none;
            border-radius: 8px;

            background: #0756a8;
            color: white;

            font-size: 16px;
            font-weight: bold;

            cursor: pointer;
        }

        .back {
            text-align: center;
            margin-top: 20px;
        }

        .back a {
            color: #0756a8;
        }

    </style>

</head>

<body>

<div class="box">

    <h1>
        🔐 Admin Login
    </h1>


    <form method="POST">

        <input
            type="email"
            name="email"
            placeholder="Admin email"
            required
        >


        <input
            type="password"
            name="password"
            placeholder="Admin password"
            required
        >


        <button type="submit">
            Login
        </button>

    </form>


    <div class="back">

        <a href="{{ url_for('home') }}">
            ← Back Home
        </a>

    </div>

</div>

</body>

</html>
""")


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect(
            url_for("admin_login")
        )


    conn = get_db()


    total_orders = conn.execute(
        """
        SELECT COUNT(*)
        FROM orders
        """
    ).fetchone()[0]


    pending_orders = conn.execute(
        """
        SELECT COUNT(*)
        FROM orders
        WHERE status = 'Pending'
        """
    ).fetchone()[0]


    total_revenue = conn.execute(
        """
        SELECT COALESCE(SUM(total), 0)
        FROM orders
        WHERE status != 'Cancelled'
        """
    ).fetchone()[0]


    orders = conn.execute(
        """
        SELECT
            orders.*,
            users.name AS customer_name,
            users.email AS customer_email

        FROM orders

        JOIN users
        ON orders.user_id = users.id

        ORDER BY orders.id DESC
        """
    ).fetchall()


    conn.close()


    prepared_orders = []


    for order in orders:

        try:
            items = json.loads(
                order["items"]
            )

        except (
            json.JSONDecodeError,
            TypeError
        ):
            items = []


        prepared_orders.append({
            "id": order["id"],
            "customer_name": order["customer_name"],
            "customer_email": order["customer_email"],
            "phone": order["phone"],
            "address": order["address"],
            "items": items,
            "total": order["total"],
            "status": order["status"]
        })


    return render_template_string("""
<!DOCTYPE html>
<html>

<head>

    <title>Admin Dashboard - Danny's Food</title>

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;

            font-family: Arial, sans-serif;

            background: #f5f7fb;

            color: #222;
        }


        nav {
            background: #0756a8;

            color: white;

            padding: 15px 20px;

            display: flex;

            justify-content: space-between;

            align-items: center;
        }


        .logo {
            font-size: 22px;

            font-weight: bold;
        }


        nav a {
            color: white;

            text-decoration: none;

            background:
                rgba(255,255,255,0.15);

            padding: 9px 13px;

            border-radius: 7px;

            margin-left: 5px;
        }


        .container {
            max-width: 1200px;

            margin: auto;

            padding: 30px 20px;
        }


        h1 {
            margin-bottom: 25px;
        }


        .stats {
            display: grid;

            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(200px, 1fr)
                );

            gap: 20px;

            margin-bottom: 30px;
        }


        .stat {
            background: white;

            padding: 22px;

            border-radius: 12px;

            box-shadow:
                0 4px 15px
                rgba(0,0,0,0.07);
        }


        .stat h3 {
            color: #666;

            font-size: 15px;

            margin-top: 0;
        }


        .stat p {
            font-size: 28px;

            font-weight: bold;

            color: #0756a8;

            margin-bottom: 0;
        }


        .order {
            background: white;

            padding: 20px;

            border-radius: 14px;

            margin-bottom: 20px;

            box-shadow:
                0 4px 15px
                rgba(0,0,0,0.07);
        }


        .order-header {
            display: flex;

            justify-content: space-between;

            gap: 15px;

            align-items: center;

            padding-bottom: 15px;

            border-bottom:
                1px solid #eee;

            margin-bottom: 15px;
        }


        .order-number {
            font-size: 18px;

            font-weight: bold;
        }


        .customer {
            line-height: 1.6;

            color: #555;

            margin-bottom: 15px;
        }


        .food-row {
            display: flex;

            justify-content: space-between;

            gap: 10px;

            padding: 7px 0;
        }


        .total {
            display: flex;

            justify-content: space-between;

            border-top:
                1px solid #eee;

            padding-top: 15px;

            margin-top: 15px;

            font-size: 20px;

            font-weight: bold;
        }


        .status {
            padding: 7px 12px;

            border-radius: 20px;

            font-size: 13px;

            font-weight: bold;
        }


        .pending {
            background: #fff3cd;

            color: #856404;
        }


        .preparing {
            background: #cfe2ff;

            color: #084298;
        }


        .delivery {
            background: #d1e7dd;

            color: #0f5132;
        }


        .delivered {
            background: #d1e7dd;

            color: #0f5132;
        }


        .cancelled {
            background: #f8d7da;

            color: #842029;
        }


        select {
            padding: 10px;

            border:
                1px solid #ddd;

            border-radius: 7px;

            margin-top: 15px;

            width: 100%;
        }


        .update-btn {
            width: 100%;

            padding: 11px;

            margin-top: 10px;

            border: none;

            border-radius: 7px;

            background: #0756a8;

            color: white;

            font-weight: bold;

            cursor: pointer;
        }


        @media (max-width: 600px) {

            .order-header {
                align-items: flex-start;

                flex-direction: column;
            }

        }

    </style>

</head>


<body>


<nav>

    <div class="logo">
        🍴 Danny's Food — Admin
    </div>


    <div>

        <a href="{{ url_for('home') }}">
            Website
        </a>

        <a href="{{ url_for('admin_logout') }}">
            Logout
        </a>

    </div>

</nav>


<div class="container">

    <h1>
        📊 Dashboard
    </h1>


    <div class="stats">


        <div class="stat">

            <h3>
                Total Orders
            </h3>

            <p>
                {{ total_orders }}
            </p>

        </div>


        <div class="stat">

            <h3>
                Pending Orders
            </h3>

            <p>
                {{ pending_orders }}
            </p>

        </div>


        <div class="stat">

            <h3>
                Total Revenue
            </h3>

            <p>
                ₦{{ "{:,}".format(total_revenue) }}
            </p>

        </div>


    </div>


    <h2>
        Customer Orders
    </h2>


    {% if orders %}


        {% for order in orders %}


        <div class="order">


            <div class="order-header">

                <div class="order-number">

                    Order #{{ order.id }}

                </div>


                <div
                    class="status

                    {% if order.status == 'Pending' %}
                        pending

                    {% elif order.status == 'Preparing' %}
                        preparing

                    {% elif order.status == 'Out for Delivery' %}
                        delivery

                    {% elif order.status == 'Delivered' %}
                        delivered

                    {% elif order.status == 'Cancelled' %}
                        cancelled

                    {% endif %}
                    "
                >

                    {{ order.status }}

                </div>

            </div>


            <div class="customer">

                <strong>
                    Customer:
                </strong>

                {{ order.customer_name }}

                <br>


                <strong>
                    Email:
                </strong>

                {{ order.customer_email }}

                <br>


                <strong>
                    Phone:
                </strong>

                {{ order.phone }}

                <br>


                <strong>
                    Address:
                </strong>

                {{ order.address }}

            </div>


            <h3>
                Food Ordered
            </h3>


            {% for item in order.items %}

            <div class="food-row">

                <span>

                    {{ item.name }}

                    × {{ item.quantity }}

                </span>


                <strong>

                    ₦{{ "{:,}".format(
                        item.price * item.quantity
                    ) }}

                </strong>

            </div>

            {% endfor %}


            <div class="total">

                <span>
                    Total
                </span>

                <span>
                    ₦{{ "{:,}".format(order.total) }}
                </span>

            </div>


            <form
                method="POST"
                action="{{ url_for(
                    'update_order',
                    order_id=order.id
                ) }}"
            >

                <select name="status">

                    <option
                        value="Pending"
                        {% if order.status == "Pending" %}
                            selected
                        {% endif %}
                    >
                        Pending
                    </option>


                    <option
                        value="Preparing"
                        {% if order.status == "Preparing" %}
                            selected
                        {% endif %}
                    >
                        Preparing
                    </option>


                    <option
                        value="Out for Delivery"
                        {% if order.status == "Out for Delivery" %}
                            selected
                        {% endif %}
                    >
                        Out for Delivery
                    </option>


                    <option
                        value="Delivered"
                        {% if order.status == "Delivered" %}
                            selected
                        {% endif %}
                    >
                        Delivered
                    </option>


                    <option
                        value="Cancelled"
                        {% if order.status == "Cancelled" %}
                            selected
                        {% endif %}
                    >
                        Cancelled
                    </option>

                </select>


                <button
                    class="update-btn"
                    type="submit"
                >
                    Update Order
                </button>

            </form>


        </div>


        {% endfor %}


    {% else %}

        <div class="order">

            <p>
                No orders yet.
            </p>

        </div>

    {% endif %}


</div>

</body>

</html>
""",
        total_orders=total_orders,
        pending_orders=pending_orders,
        total_revenue=total_revenue,
        orders=prepared_orders
    )


# =========================
# UPDATE ORDER STATUS
# =========================

@app.route(
    "/admin/update-order/<int:order_id>",
    methods=["POST"]
)
def update_order(order_id):

    if not session.get("admin"):
        return redirect(
            url_for("admin_login")
        )


    status = request.form.get(
        "status",
        "Pending"
    )


    allowed_statuses = {
        "Pending",
        "Preparing",
        "Out for Delivery",
        "Delivered",
        "Cancelled"
    }


    if status not in allowed_statuses:
        return redirect(
            url_for("admin")
        )


    conn = get_db()


    conn.execute(
        """
        UPDATE orders
        SET status = ?
        WHERE id = ?
        """,
        (status, order_id)
    )


    conn.commit()
    conn.close()


    return redirect(
        url_for("admin")
    )


# =========================
# ADMIN LOGOUT
# =========================

@app.route("/admin-logout")
def admin_logout():

    session.pop("admin", None)

    return redirect(
        url_for("admin_login")
    )
    # =========================
# START THE APP
# =========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )