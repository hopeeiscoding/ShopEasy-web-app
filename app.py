from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask import render_template

app = Flask(__name__)

#  Config FIRST
app.config["SECRET_KEY"] = "change-this-to-any-random-string"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/shopeasy"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#  Extensions AFTER config
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Login required"}), 401

login_manager.login_view = "login"

CORS(app, supports_credentials=True)


# ================= MODELS =================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    lists = db.relationship("List", backref="user", lazy=True)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    items = db.relationship("Item", backref="category", lazy=True)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)


class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    list_items = db.relationship("ListItem", backref="list", lazy=True, cascade="all, delete-orphan")


class ListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    list_id = db.Column(db.Integer, db.ForeignKey("list.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    checked = db.Column(db.Boolean, default=False)

    item = db.relationship("Item", backref="list_items")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ===== PAGE ROUTES =====
@app.route("/")
def index():
    return render_template("index.html")

# ================= CATEGORY ROUTES =================

@app.route("/api/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    return jsonify([{"id": c.id, "name": c.name} for c in categories])


@app.route("/api/categories", methods=["POST"])
def create_category():
    data = request.get_json() or {}
    name = data.get("name")

    if not name:
        return jsonify({"error": "Category name is required"}), 400

    existing = Category.query.filter_by(name=name).first()
    if existing:
        return jsonify({"error": "Category already exists"}), 409

    c = Category(name=name)
    db.session.add(c)
    db.session.commit()
    return jsonify({"id": c.id, "name": c.name}), 201


@app.route("/api/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    c = Category.query.get(category_id)
    if not c:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Category deleted"})

# ================= ITEM ROUTES =================

@app.route("/api/items", methods=["GET"])
def get_items():
    # Filters:
    # /api/items?category_id=1
    # /api/items?search=chick
    # /api/items?category_id=1&search=chick

    category_id = request.args.get("category_id", type=int)
    search = request.args.get("search", type=str)

    query = Item.query

    if category_id:
        query = query.filter(Item.category_id == category_id)

    if search:
        like = f"%{search}%"
        query = query.filter(Item.name.ilike(like))  # case-insensitive

    items = query.all()
    return jsonify([
        {"id": i.id, "name": i.name, "category_id": i.category_id}
        for i in items
    ])



@app.route("/api/items", methods=["POST"])
def create_item():
    data = request.get_json() or {}
    name = data.get("name")
    category_id = data.get("category_id")

    if not name or not category_id:
        return jsonify({"error": "name and category_id are required"}), 400

    # make sure category exists
    c = Category.query.get(category_id)
    if not c:
        return jsonify({"error": "Category not found"}), 404

    item = Item(name=name, category_id=category_id)
    db.session.add(item)
    db.session.commit()

    return jsonify({"id": item.id, "name": item.name, "category_id": item.category_id}), 201


@app.route("/api/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json() or {}

    if "name" in data and data["name"]:
        item.name = data["name"]

    if "category_id" in data and data["category_id"]:
        c = Category.query.get(data["category_id"])
        if not c:
            return jsonify({"error": "Category not found"}), 404
        item.category_id = data["category_id"]

    db.session.commit()
    return jsonify({"id": item.id, "name": item.name, "category_id": item.category_id})


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted"})

# ================= LIST ROUTES =================

@app.route("/api/lists", methods=["GET"])
@login_required
def get_lists():
    lists = List.query.filter_by(user_id=current_user.id).all()
    return jsonify([
        {"id": l.id, "name": l.name, "user_id": l.user_id}
        for l in lists
    ])


@app.route("/api/lists", methods=["POST"])
@login_required
def create_list():
    data = request.get_json() or {}
    name = data.get("name")
    user_id = current_user.id

    if not name or not user_id:
        return jsonify({"error": "name and user_id required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    l = List(name=name, user_id=user_id)
    db.session.add(l)
    db.session.commit()

    return jsonify({"id": l.id, "name": l.name, "user_id": l.user_id}), 201

# ================= LIST ITEM ROUTES =================

@app.route("/api/list-items", methods=["POST"])
@login_required
def add_item_to_list():
    data = request.get_json() or {}
    list_id = data.get("list_id")
    item_id = data.get("item_id")

    if not list_id or not item_id:
        return jsonify({"error": "list_id and item_id required"}), 400

    l = List.query.get(list_id)
    i = Item.query.get(item_id)

    if not l or not i:
        return jsonify({"error": "List or Item not found"}), 404

    if l.user_id != current_user.id:
        return jsonify({"error": "Forbidden"}), 403

    li = ListItem(list_id=list_id, item_id=item_id)
    db.session.add(li)
    db.session.commit()

    return jsonify({
        "id": li.id,
        "list_id": li.list_id,
        "item_id": li.item_id,
        "checked": li.checked
    }), 201

@app.route("/api/list-items/<int:list_item_id>/toggle", methods=["PATCH"])
@login_required
def toggle_list_item(list_item_id):
    li = ListItem.query.get(list_item_id)
    if not li:
        return jsonify({"error": "List item not found"}), 404

    if li.list.user_id != current_user.id:
        return jsonify({"error": "Forbidden"}), 403

    li.checked = not li.checked
    db.session.commit()

    return jsonify({"id": li.id, "checked": li.checked})


@app.route("/api/lists/<int:list_id>/items", methods=["GET"])
@login_required
def get_items_in_list(list_id):
    l = List.query.get(list_id)
    if not l:
        return jsonify({"error": "List not found"}), 404

    if l.user_id != current_user.id:
        return jsonify({"error": "Forbidden"}), 403

    checked_str = request.args.get("checked")
    search = request.args.get("search", type=str)

    query = ListItem.query.filter_by(list_id=list_id)

    if checked_str is not None:
        checked = checked_str.lower() == "true"
        query = query.filter(ListItem.checked == checked)

    if search:
        like = f"%{search}%"
        query = query.join(Item).filter(Item.name.ilike(like))

    list_items = query.all()

    return jsonify([
        {
            "list_item_id": li.id,
            "item_id": li.item.id,
            "name": li.item.name,
            "checked": li.checked
        }
        for li in list_items
    ])
# ================= AUTH ROUTES =================

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "username, email, password required"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "User already exists"}), 409

    hashed = generate_password_hash(password)
    u = User(username=username, email=email, password=hashed)
    db.session.add(u)
    db.session.commit()

    login_user(u)
    return jsonify({"id": u.id, "username": u.username, "email": u.email}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    u = User.query.filter_by(email=email).first()
    if not u or not check_password_hash(u.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    login_user(u)
    return jsonify({"id": u.id, "username": u.username, "email": u.email})


@app.route("/api/auth/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"})


@app.route("/api/auth/me", methods=["GET"])
@login_required
def me():
    return jsonify({"id": current_user.id, "username": current_user.username, "email": current_user.email})

# Simple test route
@app.route("/")
def home():
    return "ShopEasy database connected! 🛒"

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)