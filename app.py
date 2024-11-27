from flask import Flask, request, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-123'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
# Association table for the many-to-many relationship between users and orders
order_users = db.Table('order_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(128))
    # Add relationship to orders
    orders = db.relationship('Order', secondary=order_users, lazy='dynamic',
                           backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pin = db.Column(db.String(4), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')
    # Add relationship to order items
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Add relationships for easier access to related data
    user = db.relationship('User', backref='order_items')
    menu_item = db.relationship('MenuItem', backref='order_items')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_pin():
    while True:
        pin = ''.join(random.choices(string.digits, k=4))
        if not Order.query.filter_by(pin=pin).first():
            return pin

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not all([name, email, password]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 400

        # Create new user
        new_user = User(name=name, email=email)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Log the user in
            login_user(new_user)
            
            return jsonify({
                'success': True,
                'message': 'Signup successful',
                'user': {
                    'id': new_user.id,
                    'name': new_user.name,
                    'email': new_user.email
                }
            })
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Database error occurred'
            }), 500

    except Exception as e:
        print(f"Error during signup: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to create account'
        }), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401

    except Exception as e:
        print(f"Error during login: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Login failed'
        }), 500

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        # Clear session
        session.clear()
        # Logout user
        logout_user()
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        print(f"Error during logout: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to logout'})

@app.route('/create_order', methods=['POST'])
@login_required
def create_order():
    try:
        data = request.get_json()
        order_name = data.get('order_name')
        
        if not order_name:
            return jsonify({
                'success': False,
                'message': 'Order name is required'
            }), 400
            
        # Create new order
        pin = generate_pin()
        new_order = Order(
            name=order_name,
            pin=pin,
            created_by=current_user.id
        )
        
        # Add creator to the order's users
        new_order.users.append(current_user)
        
        db.session.add(new_order)
        db.session.commit()
        
        # Set the current order in session
        session['current_order_id'] = new_order.id
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order': {
                'name': new_order.name,
                'pin': new_order.pin
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating order: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to create order'
        }), 500

@app.route('/join_order', methods=['POST'])
@login_required
def join_order():
    try:
        data = request.get_json()
        pin = data.get('pin')
        
        if not pin:
            return jsonify({
                'success': False,
                'message': 'PIN is required'
            }), 400
            
        # Find order by PIN
        order = Order.query.filter_by(pin=pin).first()
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
            
        # Check if user is already in the order
        if current_user in order.users:
            # If user is already in the order, just set the session
            session['current_order_id'] = order.id
            return jsonify({
                'success': True,
                'message': 'Rejoined order successfully',
                'order': {
                    'name': order.name,
                    'pin': order.pin
                }
            })
            
        # Add user to order
        order.users.append(current_user)
        
        # Set the current order in session
        session['current_order_id'] = order.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Joined order successfully',
            'order': {
                'name': order.name,
                'pin': order.pin
            }
        })
        
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error joining order: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Database error occurred'
        }), 500
    except Exception as e:
        print(f"Error joining order: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to join order'
        }), 500

@app.route('/check_auth', methods=['GET'])
def check_auth():
    if current_user.is_authenticated:
        # Get user's active order if any
        active_order = None
        active_orders = current_user.orders.filter_by(status='active').all()
        if active_orders:
            active_order = active_orders[0]
            active_order_data = {
                'id': active_order.id,
                'name': active_order.name,
                'pin': active_order.pin
            }
        else:
            active_order_data = None
            
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email
            },
            'active_order': active_order_data
        })
    return jsonify({'authenticated': False}), 401

@app.route('/menu_items')
@login_required
def get_menu_items():
    try:
        items = MenuItem.query.all()
        menu_items = []
        
        for item in items:
            menu_items.append({
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'category': item.category
            })
        
        return jsonify({'menu_items': menu_items})
    except Exception as e:
        print(f"Error fetching menu items: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to load menu items'
        }), 500

@app.route('/cart')
@login_required
def get_cart():
    order_id = session.get('current_order_id')
    
    if not order_id:
        return jsonify({
            'items': [],
            'total': 0
        })
    
    cart_items = db.session.query(
        OrderItem, MenuItem
    ).join(
        MenuItem, OrderItem.menu_item_id == MenuItem.id
    ).filter(
        OrderItem.order_id == order_id,
        OrderItem.user_id == current_user.id
    ).all()
    
    items = [{
        'id': item.MenuItem.id,
        'name': item.MenuItem.name,
        'price': item.MenuItem.price,
        'quantity': item.OrderItem.quantity
    } for item in cart_items]
    
    total = sum(item['price'] * item['quantity'] for item in items)
    
    return jsonify({
        'items': items,
        'total': total
    })

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    try:
        data = request.get_json()
        item_name = data.get('item_name')
        price = float(data.get('price'))
        
        if not item_name or not price:
            return jsonify({
                'success': False,
                'message': 'Item name and price are required'
            })
        
        # Get current order
        order_id = session.get('current_order_id')
        if not order_id:
            return jsonify({
                'success': False,
                'message': 'No active order'
            })
            
        # Find or create menu item
        menu_item = MenuItem.query.filter_by(name=item_name).first()
        if not menu_item:
            menu_item = MenuItem(name=item_name, price=price)
            db.session.add(menu_item)
            db.session.flush()
        
        # Check if item already in cart
        order_item = OrderItem.query.filter_by(
            order_id=order_id,
            user_id=current_user.id,
            menu_item_id=menu_item.id
        ).first()
        
        if order_item:
            # Increment quantity if already exists
            order_item.quantity += 1
        else:
            # Create new order item
            order_item = OrderItem(
                order_id=order_id,
                user_id=current_user.id,
                menu_item_id=menu_item.id,
                quantity=1
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # Get updated cart
        cart = get_cart()
        return jsonify({
            'success': True,
            'message': 'Item added to cart',
            'cart_items': cart.json['items']
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding to cart: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to add item to cart'
        })

@app.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    data = request.get_json()
    item_name = data.get('item_name')
    
    if not item_name:
        return jsonify({'success': False, 'message': 'Item name is required'})
    
    try:
        # Get current order
        order_id = session.get('current_order_id')
        if not order_id:
            return jsonify({'success': False, 'message': 'No active order'})
        
        # Find the order item
        order_item = OrderItem.query.filter_by(
            order_id=order_id,
            user_id=current_user.id
        ).join(MenuItem).filter(MenuItem.name == item_name).first()
        
        if not order_item:
            return jsonify({'success': False, 'message': 'Item not found in cart'})
        
        # Remove the item
        db.session.delete(order_item)
        db.session.commit()
        
        # Get updated cart
        cart = get_cart()
        return jsonify({
            'success': True,
            'message': 'Item removed successfully',
            'cart_items': cart.json['items']
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error removing item from cart: {str(e)}")
        return jsonify({'success': False, 'message': 'Error removing item from cart'})

@app.route('/leave_order', methods=['POST'])
@login_required
def leave_order():
    try:
        order_id = session.get('current_order_id')
        if not order_id:
            return jsonify({'success': False, 'message': 'No active order'})
            
        # Get the order
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'})
            
        # Remove all cart items for this user in this order
        OrderItem.query.filter_by(
            order_id=order_id,
            user_id=current_user.id
        ).delete()
        
        # Remove user from order
        if current_user in order.users:
            order.users.remove(current_user)
            
        # Clear session order ID
        session.pop('current_order_id', None)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Successfully left the order'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error leaving order: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to leave order'})

@app.route('/generate_receipt', methods=['GET'])
@login_required
def generate_receipt():
    try:
        order_id = session.get('current_order_id')
        if not order_id:
            return jsonify({
                'success': False,
                'message': 'No active order'
            })

        # Get the order and all its items
        order = Order.query.get(order_id)
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            })

        # Group items by user
        user_orders = {}
        for item in order.items:
            user_id = item.user_id
            if user_id not in user_orders:
                user_orders[user_id] = {
                    'name': item.user.name,
                    'items': [],
                    'subtotal': 0
                }
            
            item_total = item.quantity * item.menu_item.price
            user_orders[user_id]['items'].append({
                'name': item.menu_item.name,
                'quantity': item.quantity,
                'price': item.menu_item.price,
                'total': item_total
            })
            user_orders[user_id]['subtotal'] += item_total

        # Calculate grand total
        grand_total = sum(user['subtotal'] for user in user_orders.values())

        return jsonify({
            'success': True,
            'order_name': order.name,
            'order_pin': order.pin,
            'user_orders': user_orders,
            'grand_total': grand_total
        })

    except Exception as e:
        print(f"Error generating receipt: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to generate receipt'
        })

@app.route('/update_quantity', methods=['POST'])
@login_required
def update_quantity():
    try:
        data = request.get_json()
        item_name = data.get('item_name')
        quantity = data.get('quantity')
        
        if not item_name or not quantity:
            return jsonify({
                'success': False,
                'message': 'Item name and quantity are required'
            })
        
        # Get current order
        order_id = session.get('current_order_id')
        if not order_id:
            return jsonify({
                'success': False,
                'message': 'No active order'
            })
            
        # Get menu item
        menu_item = MenuItem.query.filter_by(name=item_name).first()
        if not menu_item:
            return jsonify({
                'success': False,
                'message': 'Item not found'
            })
        
        # Update quantity
        order_item = OrderItem.query.filter_by(
            order_id=order_id,
            user_id=current_user.id,
            menu_item_id=menu_item.id
        ).first()
        
        if order_item:
            order_item.quantity = quantity
            db.session.commit()
            
            # Get updated cart
            cart = get_cart()
            return jsonify({
                'success': True,
                'message': 'Quantity updated',
                'cart_items': cart.json['items']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Item not found in cart'
            })
            
    except Exception as e:
        db.session.rollback()
        print(f"Error updating quantity: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update quantity'
        })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=9091, debug=True)
