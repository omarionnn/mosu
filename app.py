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
        # Get user's active orders
        active_orders = current_user.orders.filter_by(status='active').all()
        
        # Remove user from all active orders
        for order in active_orders:
            order.users.remove(current_user)
            # Delete user's order items
            OrderItem.query.filter_by(
                order_id=order.id,
                user_id=current_user.id
            ).delete()
        
        db.session.commit()
        
        # Logout the user
        logout_user()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        print(f"Error during logout: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to logout'
        }), 500

@app.route('/create_order', methods=['POST'])
@login_required
def create_order():
    try:
        data = request.get_json()
        order_name = data.get('name')
        if not order_name:
            return jsonify({'success': False, 'message': 'Order name is required'}), 400

        # Generate a unique 4-digit PIN
        pin = generate_pin()

        # Create new order
        new_order = Order(
            name=order_name,
            pin=pin,
            created_by=current_user.id,
            status='active'
        )
        
        try:
            # Add the order to the database
            db.session.add(new_order)
            db.session.commit()
            
            # Add the creator to the order's users
            new_order.users.append(current_user)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Order created successfully',
                'pin': pin,
                'order': {
                    'id': new_order.id,
                    'name': new_order.name,
                    'pin': new_order.pin
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
        print(f"Error creating order: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to create order'
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

@app.route('/join_order', methods=['POST'])
@login_required
def join_order():
    print("Join order request received")
    try:
        data = request.get_json()
        print("Request data:", data)
        
        pin = data.get('pin')
        print("PIN:", pin)

        if not pin:
            print("No PIN provided")
            return jsonify({
                'success': False,
                'message': 'PIN is required'
            }), 400

        # Find the order with the given PIN
        order = Order.query.filter_by(pin=pin).first()
        print("Found order:", order)
        
        if not order:
            print("No order found with PIN:", pin)
            return jsonify({
                'success': False,
                'message': 'Invalid PIN or order not found'
            }), 404

        # Check if user is already in the order
        is_member = current_user in order.users
        print("User is already member:", is_member)
        
        if is_member:
            print("User already in order")
            return jsonify({
                'success': True,
                'message': 'Already joined this order',
                'order': {
                    'id': order.id,
                    'name': order.name,
                    'pin': order.pin,
                    'status': order.status
                }
            })

        # Add user to order
        print("Adding user to order")
        order.users.append(current_user)
        db.session.commit()
        print("Successfully added user to order")
        
        return jsonify({
            'success': True,
            'message': 'Successfully joined order',
            'order': {
                'id': order.id,
                'name': order.name,
                'pin': order.pin,
                'status': order.status
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

@app.route('/menu_items')
@login_required
def get_menu_items():
    # Group items by category
    items_by_category = {}
    items = MenuItem.query.all()
    
    for item in items:
        if item.category not in items_by_category:
            items_by_category[item.category] = []
        items_by_category[item.category].append({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'price': item.price
        })
    
    return jsonify({'categories': items_by_category})

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
        menu_item_id = data.get('menu_item_id')
        
        if not menu_item_id:
            return jsonify({'success': False, 'message': 'Menu item ID is required'}), 400
            
        # Verify menu item exists
        menu_item = MenuItem.query.get(menu_item_id)
        if not menu_item:
            return jsonify({'success': False, 'message': 'Invalid menu item'}), 400
            
        # Get the user's current active order
        active_orders = current_user.orders.filter_by(status='active').all()
        if not active_orders:
            return jsonify({'success': False, 'message': 'No active order found'}), 404
            
        current_order = active_orders[0]  # Use the first active order
        
        try:
            # Check if the item already exists in the cart
            existing_item = OrderItem.query.filter_by(
                order_id=current_order.id,
                menu_item_id=menu_item_id,
                user_id=current_user.id
            ).first()
            
            if existing_item:
                existing_item.quantity += 1
            else:
                new_item = OrderItem(
                    order_id=current_order.id,
                    menu_item_id=menu_item_id,
                    user_id=current_user.id,
                    quantity=1
                )
                db.session.add(new_item)
                
            db.session.commit()
            
            # Get updated cart items
            cart_items = []
            order_items = OrderItem.query.filter_by(
                order_id=current_order.id,
                user_id=current_user.id
            ).all()
            
            for item in order_items:
                menu_item = MenuItem.query.get(item.menu_item_id)
                cart_items.append({
                    'id': item.id,
                    'name': menu_item.name,
                    'price': menu_item.price,
                    'quantity': item.quantity,
                    'total': menu_item.price * item.quantity
                })
            
            return jsonify({
                'success': True,
                'message': 'Item added to cart',
                'cart_items': cart_items
            })
            
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Database error occurred'
            }), 500
            
    except Exception as e:
        print(f"Error adding to cart: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to add item to cart'
        }), 500

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    order_id = session.get('current_order_id')
    
    if not order_id:
        return jsonify({'message': 'No active order'}), 400
    
    try:
        order_item = OrderItem.query.filter_by(
            order_id=order_id,
            menu_item_id=item_id,
            user_id=current_user.id
        ).first()
        
        if order_item:
            if order_item.quantity > 1:
                order_item.quantity -= 1
            else:
                db.session.delete(order_item)
            
            db.session.commit()
        
        return get_cart()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error removing item from cart'}), 500

@app.route('/leave_order', methods=['POST'])
@login_required
def leave_order():
    try:
        # Get the user's current active order
        active_orders = current_user.orders.filter_by(status='active').all()
        if not active_orders:
            return jsonify({'success': False, 'message': 'No active order found'}), 404
            
        current_order = active_orders[0]  # Use the first active order
        
        try:
            # Remove user from order
            current_order.users.remove(current_user)
            
            # Delete user's order items
            OrderItem.query.filter_by(
                order_id=current_order.id,
                user_id=current_user.id
            ).delete()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Successfully left the order'
            })
            
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Database error occurred'
            }), 500
            
    except Exception as e:
        print(f"Error leaving order: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to leave order'
        }), 500

@app.route('/generate_receipt', methods=['GET'])
@login_required
def generate_receipt():
    try:
        # Get the user's active order
        active_orders = current_user.orders.filter_by(status='active').all()
        if not active_orders:
            return jsonify({
                'success': False,
                'message': 'No active order found'
            }), 404
            
        current_order = active_orders[0]
        
        # Get all cart items for all users in this order
        all_cart_items = []
        total_amount = 0
        
        # Group items by user
        user_items = {}
        
        for user in current_order.users:
            cart_items = OrderItem.query.filter_by(
                order_id=current_order.id,
                user_id=user.id
            ).all()
            
            if cart_items:
                user_items[user.name] = {
                    'items': [],
                    'subtotal': 0
                }
                
                for item in cart_items:
                    menu_item = MenuItem.query.get(item.menu_item_id)
                    if menu_item:
                        item_total = menu_item.price * item.quantity
                        user_items[user.name]['items'].append({
                            'name': menu_item.name,
                            'price': menu_item.price,
                            'quantity': item.quantity,
                            'total': item_total
                        })
                        user_items[user.name]['subtotal'] += item_total
                        total_amount += item_total

        if not user_items:
            return jsonify({
                'success': False,
                'message': 'No items in cart'
            }), 404

        receipt = {
            'order_name': current_order.name,
            'order_pin': current_order.pin,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user_orders': user_items,
            'total_amount': total_amount
        }

        return jsonify({
            'success': True,
            'receipt': receipt
        })

    except Exception as e:
        print(f"Error generating receipt: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to generate receipt'
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=9091, debug=True)
