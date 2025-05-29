from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, session, send_from_directory
import mysql.connector
from mysql.connector import Error
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta, date
from decimal import Decimal
import os
import logging
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, ValidationError
from flask_wtf.file import FileAllowed
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import random
from flask_mail import Mail, Message
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy import text
from functools import wraps
from sqlalchemy.orm import joinedload
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_session import Session
import string
import traceback
from sqlalchemy import or_


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads/profile_pics'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/ecommerce' 
db = SQLAlchemy(app)
logging.basicConfig(level=logging.DEBUG)
CORS(app)

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'proof_images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(app.root_path, 'static', 'proof_images'), exist_ok=True)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'lordjoaquin72@gmail.com' 
app.config['MAIL_PASSWORD'] = 'sibe cuck zddj lzxg'  
app.config['MAIL_DEFAULT_SENDER'] = 'lordjoaquin72@gmail.com' 
app.config['MAIL_DEBUG'] = True


mail = Mail(app)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'ecommerce'
}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(image):
    """Save an image to the upload folder."""
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)
    return image_path

def create_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        logging.error(f"Error connecting to MySQL: {e}")
        flash("Could not connect to the database. Please try again later.", "error")
        return None

def generate_otp():
    return str(random.randint(100000, 999999))  # Generate a 6-digit OTP

def send_otp_email(email, otp):
    # Email sending logic
    try:
        msg = MIMEMultipart()
        msg['From'] = 'lordjoaquin72@gmail.com'  # Use your email address
        msg['To'] = email
        msg['Subject'] = 'Your OTP Code'
        body = f"Your OTP code is {otp}. It is valid for 10 minutes."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)  # Example using Gmail SMTP
        server.starttls()
        server.login('lordjoaquin72@gmail.com', 'sibe cuck zddj lzxg')  # Use your email credentials
        text = msg.as_string()
        server.sendmail('lordjoaquin72@gmail.com', email, text)
        server.quit()
    except Exception as e:
        flash(f"Failed to send OTP email: {str(e)}", "error")

def update_stock(variation_id, quantity):
    variation = db.session.query(VariationAttribute).filter_by(id=variation_id).first()
    if variation:
        if variation.attribute_stock >= quantity:
            variation.attribute_stock -= quantity
            db.session.add(variation)
            return True
        else:
            flash(f"Insufficient stock for variation {variation_id}.", "error")
            return False
    else:
        flash(f"Variation with ID {variation_id} not found.", "error")
        return False
    
def generate_tracking_number():
    """Generates a unique tracking number."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    

def place_order(user_id, address, payment_method, cart_items):
    """Places an order and generates tracking numbers for the order items."""
        
    # Calculate the total amount for the order
    total_amount = sum(item['product_price'] * item['quantity'] for item in cart_items)
        
    # Create a new order record
    new_order = Order(
        user_id=user_id,
        address=address,
        payment_method=payment_method,
        total=total_amount,
        created_at=datetime.utcnow()
    )
        
    # Add the order to the session (but don't commit yet)
    db.session.add(new_order)
        
    # Loop through cart items to create order items and generate tracking numbers
    for item in cart_items:
        new_order_item = OrderItem(
            order_id=new_order.id,
            product_id=item['inventory_id'],
            product_name=item['product_name'],
            product_price=item['product_price'],
            quantity=item['quantity'],
            total=item['product_price'] * item['quantity'],
            status='Pending',  # You can update this based on your order status logic
            variation_name=item.get('variation_name', ''),
            variation_value=item.get('variation_value', ''),
            product_image=item.get('product_image', ''),
            seller_id=item.get('seller_id'),
            variation_id=item.get('variation_id', None),
            cancellation_reason=None,  # Set based on your requirements
            date_received=None,
            tracking_number=generate_tracking_number()  # Assign a tracking number
    )
    db.session.add(new_order_item)
        
    # Commit all changes to the database
    db.session.commit()

    return new_order


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    middlename = StringField('Middle Name', validators=[Length(max=250)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(max=250)])
    birthdate = StringField('Birthdate', validators=[DataRequired()])
    sex = SelectField('Sex', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    housenumber = StringField('House Number', validators=[DataRequired(), Length(max=50)])
    street = StringField('Street', validators=[DataRequired(), Length(max=50)])
    city = StringField('City', validators=[DataRequired(), Length(max=50)])
    province = StringField('Province', validators=[DataRequired(), Length(max=50)])
    region = StringField('Region', validators=[DataRequired(), Length(max=100)])  # New field for region
    barangay = StringField('Barangay', validators=[DataRequired(), Length(max=100)])  # New field for barangay
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    role = SelectField('Role', choices=[('Buyer', 'Buyer'), ('Seller', 'Seller')], validators=[DataRequired()])
    shop_name = StringField('Shop Name', validators=[Optional(), Length(max=250)])
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    valid_id = FileField('Valid ID', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Register')

    def validate_shop_name(self, field):
        if self.role.data == 'Seller' and not field.data:
            raise ValidationError('Shop name is required for Sellers.')



class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    middlename = db.Column(db.String(250), nullable=True)
    lastname = db.Column(db.String(250), nullable=False)
    birthdate = db.Column(db.String(20), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    housenumber = db.Column(db.String(200))
    street = db.Column(db.String(200))
    barangay = db.Column(db.String(100))
    city = db.Column(db.String(100))
    province = db.Column(db.String(100))
    region = db.Column(db.String(100))
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)
    otp = db.Column(db.Integer, nullable=True)
    shop_name = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.Integer, nullable=True)
    account_status  = db.Column(db.String(250), nullable=False)

    carts = db.relationship('Cart', back_populates='user')
    orders = db.relationship('Order', back_populates='user')
    notifications = db.relationship('Notification', back_populates='account', lazy=True)
  

    def __repr__(self):
        return f'<Account {self.email}>'


    
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(250), nullable=False)


class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), default=None)
    details = db.Column(db.Text, default=None)
    product_picture = db.Column(db.String(255), default=None)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    shop_name = db.Column(db.String(250), nullable=False)
    seller_id = db.Column(db.Integer, nullable=False)
    
    variations = db.relationship('ProductVariation', backref='inventory', lazy=True)
    
    # Define the foreign key relationship with OrderItem
    order_items = db.relationship('OrderItem', back_populates='product', foreign_keys='OrderItem.product_id')


class ProductVariation(db.Model):
    __tablename__ = 'product_variations'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))
    
    attributes = db.relationship('VariationAttribute', backref='variation', lazy=True)


class VariationAttribute(db.Model):
    __tablename__ = 'variation_attributes'

    id = db.Column(db.Integer, primary_key=True)
    variation_id = db.Column(db.Integer, db.ForeignKey('product_variations.id'))
    attribute_name = db.Column(db.String(50))
    attribute_value = db.Column(db.String(50))
    attribute_image = db.Column(db.String(255))
    attribute_image = db.Column(db.String(255))  # Assuming this stores image path
    attribute_price = db.Column(db.Integer)  # Add this line for price
    attribute_stock = db.Column(db.Integer)  # Add this line for stock

    def __repr__(self):
        return f"<VariationAttribute {self.attribute_name} - {self.attribute_value}>"


class Cart(db.Model):
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)  # Updated from users
    total_items = db.Column(db.Integer, default=0)
    total_price = db.Column(db.Numeric(10, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('Account', back_populates='carts')
    items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')


    def __repr__(self):
        return f'<Cart {self.id}, Total Items: {self.total_items}>'

def get_all_products_from_db():
    return Cart.query.all()

    
class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'))
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))
    quantity = db.Column(db.Numeric(10, 2))  # Ensure quantity is Numeric to handle decimals
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    variation_name = db.Column(db.String(100), nullable=True)  # Variation name
    variation_value = db.Column(db.String(100), nullable=True)  # Variation value
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Corrected to db.Numeric for price
    stock = db.Column(db.Integer, nullable=False)  # Add stock field
    variation_attribute_id = db.Column(db.Integer, db.ForeignKey('variation_attributes.id'), nullable=False)

    # Relationships
    cart = db.relationship('Cart', back_populates='items')  # Relationship with Cart
    # inventory = db.relationship('Inventory', foreign_keys=[inventory_id])
    variation_attribute = db.relationship('VariationAttribute', backref='cart_items')
    product = db.relationship('Inventory', backref='cart_items', lazy=True)


    def __init__(self, cart_id, inventory_id, quantity, variation_name=None, variation_value=None, stock=None, price=None, variation_attribute_id=None):
        self.cart_id = cart_id
        self.inventory_id = inventory_id
        self.quantity = quantity
        self.variation_name = variation_name  # Initialize variation name
        self.variation_value = variation_value  # Initialize variation value
        self.price = price if price is not None else 0  # Default to 0 if no price is passed
        self.stock = stock if stock is not None else 0  # Default to 0 if no stock is passed
        self.variation_attribute_id = variation_attribute_id 

    def update_quantity(self, new_quantity):
        if new_quantity <= 0:
            db.session.delete(self)
        else:
            self.quantity = new_quantity
        db.session.commit()

    def calculate_item_total(self):
        return self.quantity * self.price

    def as_dict(self):
        return {
            'id': self.id,
            'cart_id': self.cart_id,
            'inventory_id': self.inventory_id,
            'product_name': self.inventory.product_name,
            'product_price': str(self.price),
            'quantity': self.quantity,
            'variation_name': self.variation_name,
            'variation_value': self.variation_value,
            'total': str(self.calculate_item_total()),
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<CartItem {self.inventory.product_name}, Quantity: {self.quantity}, Variation: {self.variation_name} - {self.variation_value}>'


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with OrderItem
    items = db.relationship('OrderItem', back_populates='order', lazy=True)  # back_populates instead of backref

    # Relationship with Account (User)
    user = db.relationship('Account', back_populates='orders')
    



class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(250), nullable=False)
    variation_name = db.Column(db.String(255), nullable=True)
    variation_value = db.Column(db.String(255), nullable=True)
    product_image = db.Column(db.String(250), nullable=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('inventory.seller_id'), nullable=False)  # New field
    variation_id = db.Column(db.Integer, db.ForeignKey('variation_attributes.id'), nullable=True)  # Add this line
    cancellation_reason = db.Column(db.String(255))  # Ensure this line exists
    date_received = db.Column(db.DateTime, default=None) 
    tracking_number = db.Column(db.String(50), nullable=True)
    ridername = db.Column(db.String(255), nullable=True)
    rider_id = db.Column(db.Integer, nullable=True)
    status_changed_at = db.Column(db.DateTime) 
    proof_image = db.Column(db.String(255), nullable=True)


    # Relationship to Order
    order = db.relationship('Order', back_populates='items')  # back_populates instead of backref
    
    # Relationship to Inventory
    product = db.relationship('Inventory', back_populates='order_items', foreign_keys=[product_id])  # Explicitly specify the foreign key
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} - {self.status}>'
    


class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)  # Linking to accounts table
    role = db.Column(db.String(50), nullable=False)  # e.g., 'customer', 'admin'
    user_name = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    photo = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tracking_number = db.Column(db.String(50), nullable=False)

    # Relationships
    user = db.relationship('Account', backref=db.backref('feedbacks', lazy=True))

    def __init__(self, product_id, user_id, role, user_name, comment, rating, photo=None, tracking_number=None):
        self.product_id = product_id
        self.user_id = user_id
        self.role = role
        self.user_name = user_name
        self.comment = comment
        self.rating = rating
        self.photo = photo
        self.tracking_number = tracking_number


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('unread', 'read', name='status'), default='unread')
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    notification_type = db.Column(db.String(50), nullable=False)

    account = db.relationship('Account', back_populates='notifications')
   

    def __repr__(self):
        return f"<Notification {self.id} - {self.message}>"
    
class RiderCommission(db.Model):
    __tablename__ = 'rider_commissions'
    id = db.Column(db.Integer, primary_key=True)
    rider_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'), nullable=False)
    commission_amount = db.Column(db.Numeric(10,2), nullable=False)
    computed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.String(255))


@app.route('/')
def home():
    return render_template('login2.html')

@app.route('/index')
def index():
    products = Inventory.query.all()  
    return render_template('index.html', products=products)

@app.route('/profile')
def profile():
    # Retrieve user_id from session
    user_id = session.get('user_id')

    if user_id:
        user = Account.query.get(user_id)
        profile_picture_url = url_for('static', filename=f'uploads/profile_pics/{user.profile_picture}') if user.profile_picture else None
        return render_template('buyer_profile.html', user=user, profile_picture_url=profile_picture_url)
    else:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))
    
@app.route('/update_profile', methods=['POST', 'GET'])
def update_profile():
    user_id = session.get('user_id')
    if user_id:
        user = Account.query.get(user_id)
        if user:
            user.firstname = request.form['firstname']
            user.middlename = request.form['middlename']
            user.lastname = request.form['lastname']
            user.birthdate = request.form['birthdate']
            user.sex = request.form['sex']
            user.email = request.form['email']
            user.password = request.form['password']
            db.session.commit()
            flash("Profile updated successfully.", "success")
        else:
            flash("User not found.", "danger")
        return redirect(url_for('profile'))
    else:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))
    
@app.route('/update_address', methods=['POST', 'GET'])
def update_address():
    user_id = session.get('user_id')
    if user_id:
        user = Account.query.get(user_id)
        if user:
            user.housenumber = request.form['housenumber']
            user.street = request.form['street']
            user.barangay = request.form['barangay']
            user.city = request.form['city']
            user.province = request.form['province']
            user.region = request.form['region']
            db.session.commit()
            flash("Address updated successfully.", "success")
        else:
            flash("User not found.", "danger")
        return redirect(url_for('profile'))
    else:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))
    
@app.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    if 'profile_picture' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['profile_picture']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)  # Keep the original filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Store only the filename in the database (no path)
        user_id = session.get('user_id')
        if user_id:
            # Update the profile picture filename in the database
            update_profile_picture(user_id, filename)
            flash('Profile picture updated successfully!')
            return redirect(url_for('profile'))

    flash('Invalid file format. Please upload an image.')
    return redirect(request.url)

def update_profile_picture(user_id, filename):
    # Update the user's profile picture filename in the database
    user = Account.query.get(user_id)  # Get the actual user from the database
    if user:
        user.profile_picture = filename  # Only store the filename, not the full path
        db.session.commit()



@app.context_processor
def inject_profile_picture():
    user_id = session.get('user_id')
    if user_id:
        # Fetch the user's profile picture from the database
        user = Account.query.filter_by(id=user_id).first()
        if user and user.profile_picture:
            profile_picture_url = url_for('static', filename=f'uploads/profile_pics/{user.profile_picture}')
        else:
            # Use a default image if no profile picture is set
            profile_picture_url = url_for('static', filename='uploads/profile_pics/default.jpg')
    else:
        # If no user is logged in, return a default profile picture
        profile_picture_url = url_for('static', filename='uploads/profile_pics/default.jpg')
    
    return {'profile_picture_url': profile_picture_url}


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    logging.debug("Received request to add to cart")
    try:
        data = request.get_json()
        logging.debug(f"Request data: {data}")

        product_id = data.get('product_id')
        quantity = data.get('quantity')
        variation_name = data.get('variation_name')  # Get variation name
        variation_value = data.get('variation_value')  # Get variation value
        variation_price = data.get('price')  # Get the price of the variation
        variation_stock = data.get('stock')  # Get the stock of the variation
        variation_id = data.get('variation_id')  # Get the variation_id from the request data
        max_quantity = 9999  # Define the maximum allowed quantity per variation (can be dynamic)

        if not product_id or not quantity:
            logging.error("Product ID or quantity not provided")
            return jsonify({'success': False, 'message': 'Product ID and quantity are required'}), 400

        # Check if the stock is 0
        if int(variation_stock) <= 0:
            logging.warning(f"Attempt to add a product with no stock: Product ID {product_id}, Variation '{variation_name}: {variation_value}'")
            return jsonify({'success': False, 'message': 'This item is out of stock and cannot be added to the cart.'}), 400

        # Find the product in the inventory
        product = db.session.get(Inventory, product_id)
        if not product:
            logging.error(f"Product not found: ID {product_id}")
            return jsonify({'success': False, 'message': 'Product not found'}), 404

        # Get the current user's cart or create one
        user_id = session.get('user_id')
        if not user_id:
            logging.warning("User not logged in.")
            return jsonify({'success': False, 'message': 'You must be logged in to add to cart'}), 403

        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()
            logging.info(f"Created a new cart for User ID: {user_id}")

        # Check if the product with the selected variation is already in the cart
        cart_item = CartItem.query.filter_by(
            cart_id=cart.id,
            inventory_id=product.id,
            variation_name=variation_name,
            variation_value=variation_value,
        ).first()

        quantity_decimal = Decimal(quantity)

        # If the item already exists in the cart, check if adding the quantity exceeds the stock
        if cart_item:
            new_quantity = cart_item.quantity + quantity_decimal
            if new_quantity > int(variation_stock):
                logging.error(f"Not enough stock for variation '{variation_value}'. Available: {variation_stock}, Requested: {new_quantity}")
                return jsonify({'success': False, 'message': 'Not enough stock available for the selected variation'}), 400
            if new_quantity > max_quantity:
                logging.error(f"Maximum quantity exceeded for variation '{variation_value}'. Maximum allowed: {max_quantity}, Requested: {new_quantity}")
                return jsonify({'success': False, 'message': 'You have already added the maximum allowed quantity in your cart.'}), 400
            cart_item.quantity = new_quantity
            logging.info(f"Updated quantity for Product ID: {product.id} in Cart ID: {cart.id} with variation '{variation_name}: {variation_value}'")
        else:
            if quantity_decimal > int(variation_stock):
                logging.error(f"Not enough stock for variation '{variation_value}'. Available: {variation_stock}, Requested: {quantity_decimal}")
                return jsonify({'success': False, 'message': 'Not enough stock available for the selected variation'}), 400
            if quantity_decimal > max_quantity:
                logging.error(f"Maximum quantity exceeded for variation '{variation_value}'. Maximum allowed: {max_quantity}, Requested: {quantity_decimal}")
                return jsonify({'success': False, 'message': 'You have already added the maximum allowed quantity in your cart.'}), 400
            # Add the new product to the cart with variation details and variation_id
            cart_item = CartItem(
                cart_id=cart.id,
                inventory_id=product.id,
                quantity=quantity_decimal,
                variation_name=variation_name,
                variation_value=variation_value,
                price=Decimal(variation_price),  # Store variation price
                stock=variation_stock,  # Store variation stock
                variation_attribute_id=variation_id  # Store the variation_id in the variation_attribute_id column
            )
            db.session.add(cart_item)
            logging.info(f"Added Product ID: {product.id} to Cart ID: {cart.id} with variation '{variation_name}: {variation_value}'")

        # Update cart total items and price based on the variation's price
        cart.total_items += int(quantity)
        cart.total_price += Decimal(variation_price) * quantity_decimal

        db.session.commit()
        logging.info(f"Cart updated. Total items: {cart.total_items}, Total price: {cart.total_price}")

        return jsonify({'success': True, 'cart_total_items': cart.total_items})

    except Exception as e:
        logging.error(f"Error while adding to cart: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while adding to the cart.'}), 500


@app.route('/buy_now', methods=['POST'])
def buy_now():
    logging.debug("Received request to add to cart")
    try:
        data = request.get_json()
        logging.debug(f"Request data: {data}")

        product_id = data.get('product_id')
        quantity = data.get('quantity')
        variation_name = data.get('variation_name')  # Get variation name
        variation_value = data.get('variation_value')  # Get variation value
        variation_price = data.get('price')  # Get the price of the variation
        variation_stock = data.get('stock')  # Get the stock of the variation
        variation_id = data.get('variation_id')  # Get the variation_id from the request data
        max_quantity = 9999  # Define the maximum allowed quantity per variation (can be dynamic)

        if not product_id or not quantity:
            logging.error("Product ID or quantity not provided")
            return jsonify({'success': False, 'message': 'Product ID and quantity are required'}), 400
        
        # Check if the stock is 0
        if int(variation_stock) <= 0:
            logging.warning(f"Attempt to add a product with no stock: Product ID {product_id}, Variation '{variation_name}: {variation_value}'")
            return jsonify({'success': False, 'message': 'This item is out of stock'}), 400

        # Find the product in the inventory
        product = db.session.get(Inventory, product_id)
        if not product:
            logging.error(f"Product not found: ID {product_id}")
            return jsonify({'success': False, 'message': 'Product not found'}), 404

        # Get the current user's cart or create one
        user_id = session.get('user_id')
        if not user_id:
            logging.warning("User not logged in.")
            return jsonify({'success': False, 'message': 'You must be logged in to add to cart'}), 403

        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()
            logging.info(f"Created a new cart for User ID: {user_id}")

        # Check if the product with the selected variation is already in the cart
        cart_item = CartItem.query.filter_by(
            cart_id=cart.id,
            inventory_id=product.id,
            variation_name=variation_name,
            variation_value=variation_value,
        ).first()

        quantity_decimal = Decimal(quantity)

        # If the item already exists in the cart, we check if adding the quantity exceeds the max limit
        if cart_item:
            new_quantity = cart_item.quantity + quantity_decimal
            if new_quantity > int(variation_stock):
                logging.error(f"Not enough stock for variation '{variation_value}'. Available: {variation_stock}, Requested: {new_quantity}")
                return jsonify({'success': False, 'message': 'You have already added the maximum allowed quantity in your cart.'}), 400
            if new_quantity > max_quantity:
                logging.error(f"Maximum quantity exceeded for variation '{variation_value}'. Maximum allowed: {max_quantity}, Requested: {new_quantity}")
                return jsonify({'success': False, 'message': 'You have already added the maximum allowed quantity in your cart.'}), 400
            cart_item.quantity = new_quantity
            logging.info(f"Updated quantity for Product ID: {product.id} in Cart ID: {cart.id} with variation '{variation_name}: {variation_value}'")
        else:
            if quantity_decimal > int(variation_stock):
                logging.error(f"Not enough stock for variation '{variation_value}'. Available: {variation_stock}, Requested: {quantity_decimal}")
                return jsonify({'success': False, 'message': 'Not enough stock available for the selected variation'}), 400
            if quantity_decimal > max_quantity:
                logging.error(f"Maximum quantity exceeded for variation '{variation_value}'. Maximum allowed: {max_quantity}, Requested: {quantity_decimal}")
                return jsonify({'success': False, 'message': 'You have already added the maximum allowed quantity in your cart.'}), 400
            # Add the new product to the cart with variation details and variation_id
            cart_item = CartItem(
                cart_id=cart.id,
                inventory_id=product.id,
                quantity=quantity_decimal,
                variation_name=variation_name,
                variation_value=variation_value,
                price=Decimal(variation_price),  # Store variation price
                stock=variation_stock,  # Store variation stock
                variation_attribute_id=variation_id  # Store the variation_id in the variation_attribute_id column
            )
            db.session.add(cart_item)
            logging.info(f"Added Product ID: {product.id} to Cart ID: {cart.id} with variation '{variation_name}: {variation_value}'")

        # Update cart total items and price based on the variation's price
        cart.total_items += int(quantity)
        cart.total_price += Decimal(variation_price) * quantity_decimal

        db.session.commit()
        logging.info(f"Cart updated. Total items: {cart.total_items}, Total price: {cart.total_price}")

        return jsonify({'success': True, 'redirect': url_for('view_cart')})
        

    except Exception as e:
        logging.error(f"Error while adding to cart: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while adding to the cart.'}), 500



@app.route('/cart')
def view_cart():
    user_id = session.get('user_id')
    if not user_id:
        flash("You need to log in to view your cart.", "error")
        return redirect(url_for('home'))  # Redirect to the home page if not logged in

    connection = create_connection()
    if not connection:
        flash("Could not connect to the database. Please try again later.", "error")
        return render_template('cart.html', carts=[], total=0)

    cursor = connection.cursor(dictionary=True)
    cursor.execute(""" 
        SELECT ci.id, ci.quantity, i.product_name AS name, ci.price, i.product_picture, 
               (ci.quantity * ci.price) AS total, ci.variation_name, ci.variation_value, ci.inventory_id
        FROM cart_items ci 
        JOIN inventory i ON ci.inventory_id = i.id 
        JOIN carts c ON ci.cart_id = c.id 
        WHERE c.user_id = %s
    """, (user_id,))
    carts = cursor.fetchall()

    subtotal = sum(item['total'] for item in carts) if carts else 0
    total = subtotal  # No shipping cost added

    cursor.close()
    connection.close()

    return render_template('cart.html', carts=carts, subtotal=subtotal, total=total)


@app.route('/check_stock/<int:item_id>/<int:new_quantity>', methods=['GET'])
def check_stock(item_id, new_quantity):
    # Debugging: Print the item_id to verify it is passed correctly
    print(f"Requested item_id: {item_id}")

    # Fetch the cart item from the cart_items table based on item_id
    cart_item = CartItem.query.filter_by(id=item_id).first()

    if cart_item:
        # Get the available stock for this item
        available_stock = cart_item.stock
        print(f"Available stock for item {item_id}: {available_stock}")  # Debugging available stock

        # Check if the new quantity is less than or equal to the available stock
        if new_quantity <= available_stock:
            return jsonify({"success": True, "message": "Stock available", "current_quantity": available_stock})
        else:
            return jsonify({"success": False, "message": f"Only {available_stock} items available", "current_quantity": available_stock})
    else:
        print("Cart item not found.")
        return jsonify({"success": False, "message": "Cart item not found", "current_quantity": 0})





@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User not logged in.'}), 403

    data = request.get_json()
    item_id = data.get('item_id')

    if not item_id:
        return jsonify({'status': 'error', 'message': 'Item ID is required.'}), 400

    connection = create_connection()
    if not connection:
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500

    try:
        cursor = connection.cursor()

        # Delete the item from cart_items
        cursor.execute("""
            DELETE FROM cart_items
            WHERE id = %s AND cart_id IN (SELECT id FROM carts WHERE user_id = %s)
        """, (item_id, user_id))

        # Calculate new total_price
        cursor.execute("""
            SELECT SUM(i.price * ci.quantity) 
            FROM cart_items ci 
            JOIN inventory i ON ci.inventory_id = i.id 
            WHERE ci.cart_id IN (SELECT id FROM carts WHERE user_id = %s)
        """, (user_id,))
        total_price = cursor.fetchone()[0] or 0.00

        # Update total_price in carts table
        cursor.execute("""
            UPDATE carts 
            SET total_price = %s 
            WHERE user_id = %s
        """, (total_price, user_id))

        connection.commit()
        return jsonify({'status': 'success', 'message': 'Item removed successfully.', 'total_price': total_price}), 200

    except Exception as e:
        print("Error:", e)  # Log the error for debugging
        return jsonify({'status': 'error', 'message': 'Failed to remove item.'}), 500

    finally:
        cursor.close()
        connection.close()

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user_id = session.get('user_id')
    if not user_id:
        flash("You need to log in to view your cart.", "error")
        return redirect(url_for('home'))

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    user = Account.query.get(user_id)
    info = f"{user.firstname} {user.middlename} {user.lastname}"

    # Fetch the user's primary address from the accounts table
    cursor.execute("""
    SELECT 
        CONCAT(
            COALESCE(housenumber, ''), ', ',
            COALESCE(street, ''), ', ',
            COALESCE(barangay, ''), ', ',
            COALESCE(city, ''), ', ',
            COALESCE(province, ''), ', ',
            COALESCE(region, '')
        ) AS address 
    FROM accounts 
    WHERE id = %s
    """, (user_id,))
    user_address = cursor.fetchone()
    address = user_address['address'] if user_address and user_address['address'].strip() else "No address on file. Please add one."
    print("Fetched user_address:", user_address)


    # Handle POST request (when the user confirms the order)
    if request.method == 'POST':
        selected_item_ids = request.form.getlist('product_ids')  # Get selected product IDs
        quantities = {item_id: int(request.form.get(f'quantity_{item_id}', 1)) for item_id in selected_item_ids}

        # Check if no items are selected for checkout
        if not selected_item_ids:
            flash("No items selected for checkout.", "error")
            return redirect(url_for('view_cart'))

        # Store selected items and quantities in the session
        session['selected_item_ids'] = selected_item_ids
        session['selected_quantities'] = quantities

        print("Selected item IDs stored in session (POST):", session.get('selected_item_ids'))
        print("Selected quantities stored in session (POST):", session.get('selected_quantities'))

        # Fetch selected items from the cart
        placeholders = ','.join(['%s'] * len(selected_item_ids))  # Use placeholders for safety
        # Fetch selected items from the cart and include variation_attribute_id
        query = f"""
            SELECT ci.id, i.product_name AS name, ci.price, ci.quantity, 
                (ci.quantity * i.price) AS total, i.product_picture AS image,
                ci.variation_name, ci.variation_value, ci.inventory_id, ci.variation_attribute_id
            FROM cart_items ci 
            JOIN inventory i ON ci.inventory_id = i.id 
            WHERE ci.id IN ({placeholders}) AND ci.cart_id IN (SELECT id FROM carts WHERE user_id = %s)
        """
        cursor.execute(query, tuple(selected_item_ids) + (user_id,))
        selected_items = cursor.fetchall()


        # Calculate total based on updated quantities
        total = 0
        for item in selected_items:
            item['quantity'] = quantities.get(str(item['id']), item['quantity'])  # Get updated quantity
            item['total'] = item['quantity'] * item['price']  # Update total for the item
            total += item['total']

        cursor.close()
        connection.close()

        return render_template('checkout.html', selected_items=selected_items, total=total, address=address, info=info)

    # Handle GET request (initial page load with selected items)
    selected_item_ids = session.get('selected_item_ids', [])
    quantities = session.get('selected_quantities', {})

    print("Selected item IDs from session (GET):", selected_item_ids)
    print("Selected quantities from session (GET):", quantities)

    if selected_item_ids:
        placeholders = ','.join(['%s'] * len(selected_item_ids))  # Use placeholders for safety
        query = f"""
            SELECT ci.id, i.product_name AS name, ci.price, ci.quantity, 
                   (ci.quantity * i.price) AS total, i.product_picture AS image,
                   ci.variation_name, ci.variation_value, ci.inventory_id
            FROM cart_items ci 
            JOIN inventory i ON ci.inventory_id = i.id 
            WHERE ci.id IN ({placeholders}) AND ci.cart_id IN (SELECT id FROM carts WHERE user_id = %s)
        """
        cursor.execute(query, tuple(selected_item_ids) + (user_id,))
        selected_items = cursor.fetchall()
    else:
        # If no items are selected, fetch all cart items
        cursor.execute("""
            SELECT ci.id, i.product_name AS name, i.price, ci.quantity, 
                   (ci.quantity * i.price) AS total, i.product_picture AS image,
                   ci.variation_name, ci.variation_value, ci.inventory_id
            FROM cart_items ci 
            JOIN inventory i ON ci.inventory_id = i.id 
            WHERE ci.cart_id IN (SELECT id FROM carts WHERE user_id = %s)
        """, (user_id,))
        selected_items = cursor.fetchall()

    # Calculate total for the selected items
    total = sum(item['total'] for item in selected_items)

    cursor.close()
    connection.close()

    return render_template('checkout.html', selected_items=selected_items, total=total, address=address, info=info)




@app.route('/finalize_checkout', methods=['POST'])
def finalize_checkout():
    # Capture form data
    address = request.form.get('address')
    payment_method = request.form.get('payment_method')
    subtotal = request.form.get('subtotal')
    shipping_fee = 50.00  # Adjust as needed

    print(f"Address: {address}, Payment Method: {payment_method}, Subtotal: {subtotal}")

    try:
        subtotal = float(subtotal)
    except ValueError:
        flash("Invalid subtotal value.", "error")
        print("Error: Invalid subtotal value.")
        return redirect(url_for('checkout'))

    # Get user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to place an order.", "error")
        print("Error: User not logged in.")
        return redirect(url_for('login'))

    # Fetch cart for the user
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart or not cart.items:
        flash("Your cart is empty.", "error")
        print("Error: Cart is empty.")
        return redirect(url_for('checkout'))

    cart_items = cart.items  # Relationship defined in Cart model

    # Extract form data for order processing
    product_ids = request.form.getlist('product_id')
    cart_item_ids = request.form.getlist('cart_item_id')  # Get cart item IDs from the form
    product_names = request.form.getlist('product_name')
    product_prices = request.form.getlist('product_price')
    quantities = request.form.getlist('product_quantity')
    total_items = request.form.getlist('product_total')
    product_images = request.form.getlist('product_image')
    variation_names = request.form.getlist('variation_name')
    variation_values = request.form.getlist('variation_value')
    variation_attribute_ids = request.form.getlist('variation_attribute_id')

    # Collect unique seller IDs
    seller_ids = {item.product.seller_id for item in cart_items if item.product}

    try:
        for seller_id in seller_ids:
            # Create a new order for this seller
            new_order = Order(
                user_id=user_id,
                address=address,
                payment_method=payment_method,
                total=0,  # Will calculate based on items
            )
            db.session.add(new_order)
            db.session.commit()

            for i in range(len(product_ids)):
                inventory_item = Inventory.query.get(product_ids[i])
                if inventory_item and inventory_item.seller_id == seller_id:
                    # Fetch the variation from the cart items
                    variation_attribute_id = variation_attribute_ids[i]

                    # Create order items
                    order_item = OrderItem(
                        order_id=new_order.id,
                        product_id=product_ids[i],
                        product_name=product_names[i],
                        product_price=float(product_prices[i]),
                        quantity=int(quantities[i]),
                        total=float(total_items[i]),
                        variation_name=variation_names[i],
                        variation_value=variation_values[i],
                        variation_id=variation_attribute_id,  # Correctly assign the variation ID
                        product_image=product_images[i],
                        seller_id=seller_id,
                        status="Pending",
                        tracking_number=generate_tracking_number(),
                    )
                    db.session.add(order_item)

            # Calculate order total after adding items
            db.session.commit()
            order_total = sum(item.total for item in OrderItem.query.filter_by(order_id=new_order.id))
            new_order.total = order_total + shipping_fee
            db.session.commit()

            # Reduce stock for inventory and variations
            for order_item in OrderItem.query.filter_by(order_id=new_order.id).all():
                print(f"Checking variation: {order_item.variation_id}, {order_item.variation_name}, {order_item.variation_value}")  # Debugging line
                
                # Now, we match variation_id, variation_name, and variation_value
                variation = VariationAttribute.query.filter_by(
                    variation_id=order_item.variation_id,  # Match with the variation ID from order
                    attribute_name=order_item.variation_name,
                    attribute_value=order_item.variation_value
                ).first()

                if variation:
                    print(f"Found variation: {variation.attribute_name} = {variation.attribute_value}")  # Debugging line
                    
                    # Ensure enough stock is available
                    if variation.attribute_stock >= order_item.quantity:
                        variation.attribute_stock -= order_item.quantity
                        db.session.add(variation)
                    else:
                        flash(f"Insufficient stock for variation {variation.attribute_name}.", "error")
                        print(f"Error: Insufficient stock for variation {variation.attribute_name}.")  # Debugging line
                        db.session.rollback()
                        return redirect(url_for('checkout'))
                else:
                    flash("Variation not found.", "error")
                    print("Error: Variation not found.")  # Debugging line
                    db.session.rollback()
                    return redirect(url_for('checkout'))

                # Update the product's total stock based on variations
                inventory_item = Inventory.query.get(order_item.product_id)
                if inventory_item:
                    total_variation_stock = db.session.query(
                        db.func.sum(VariationAttribute.attribute_stock)
                    ).join(ProductVariation, ProductVariation.id == VariationAttribute.variation_id) \
                    .filter(ProductVariation.product_id == inventory_item.id) \
                    .scalar()

                    inventory_item.quantity = total_variation_stock if total_variation_stock is not None else 0
                    db.session.add(inventory_item)
                else:
                    flash(f"Inventory item not found for product ID {order_item.product_id}.", "error")
                    print(f"Error: Inventory item not found for product ID {order_item.product_id}.")
                    db.session.rollback()
                    return redirect(url_for('checkout'))

            # Commit the stock changes
            db.session.commit()

        # Clear selected cart items after successful order placement based on cart_item_ids
        for cart_item_id in cart_item_ids:
            cart_item = CartItem.query.get(cart_item_id)
            if cart_item:
                db.session.delete(cart_item)
        db.session.commit()

        print("Selected cart items deleted.")
        flash("Order(s) placed successfully!", "success")
        return redirect(url_for('index'))

    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {str(e)}")  # Added print for debugging
        flash(f"An error occurred while processing your order: {str(e)}", "error")
        return redirect(url_for('checkout'))




@app.route('/category/<category_name>')
def category(category_name):
    # Query the database to get products based on the selected category
    products = Inventory.query.filter_by(category=category_name).all()
    
    return render_template('category.html', products=products, category_name=category_name)

@app.route('/search_products', methods=['GET'])
def search_products():
    query = request.args.get('query', '').strip()
    if query:
        # Fetch products from the database that match the query
        products = Inventory.query.filter(Inventory.product_name.like(f"%{query}%")).all()
    else:
        products = []

    return render_template('search_results.html', products=products, query=query)


@app.route('/add_address', methods=['POST'])
def add_address():
    user_id = session.get('user_id')
    if not user_id:
        flash("You need to log in to add an address.", "error")
        return redirect(url_for('login'))

    # Get the address from the form
    address = request.form.get('address')
    print("Received address:", address)  # Debugging statement

    if not address:
        flash("Address is required.", "error")
        return redirect(url_for('checkout'))

    # Debugging: Check if the address is indeed passed and not empty
    if address.strip() == "":
        print("Address is empty after trimming!")
        flash("Address is required.", "error")
        return redirect(url_for('checkout'))

    # If address is provided, insert into the database
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO buyer_address (user_id, address) 
            VALUES (%s, %s)
        """, (user_id, address))
        connection.commit()
        cursor.close()
        connection.close()

        print("Address inserted successfully:", address)  # Debugging statement
        flash("Address added successfully.", "success")
    except Exception as e:
        print("Error inserting address:", e)  # Debugging statement
        flash("An error occurred while adding the address. Please try again.", "error")
        return redirect(url_for('checkout'))

    # Check if the selected items are still in the session, and re-store them if necessary
    selected_item_ids = session.get('selected_item_ids')
    selected_quantities = session.get('selected_quantities')

    # If the items are in session, make sure they persist
    if selected_item_ids:
        session['selected_item_ids'] = selected_item_ids
    if selected_quantities:
        session['selected_quantities'] = selected_quantities

    print("Address added. Selected items from session:", session.get('selected_item_ids'))

    # Redirect back to checkout page after adding address
    return redirect(url_for('checkout'))





    #@app.route('/seller_orders')
    #@login_required
    #def seller_orders():
        # Fetch the orders, including the associated account details
        #orders = Order.query.options(db.joinedload(Order.account)).all()
        #orders = db.session.query(Order).all()  # or similar query
    
        #print(orders)
        #return render_template('seller_orders.html', orders=orders)
@app.route('/my_orders')
def my_orders():
    user_id = session.get('user_id')  # Get the logged-in user's ID from the session

    if user_id:
        # Eagerly load the related order items using joinedload
        orders = Order.query.filter_by(user_id=user_id).options(db.joinedload(Order.items)).all()
        
        return render_template('my_orders.html', orders=orders)
    else:
        flash("Please log in to view your orders.", "warning")
        return redirect(url_for('login'))
    
    
@app.route('/confirm_order/<int:order_id>', methods=['POST'])
def confirm_order(order_id):
    try:
        # Log the incoming order_id for debugging
        print(f"Attempting to confirm order with ID: {order_id}")

        # Find the first order item with one of the allowed statuses
        allowed_statuses = ['Pending']
        order_item = OrderItem.query.filter_by(id=order_id).filter(OrderItem.status.in_(allowed_statuses)).first()

        if order_item:
            # Log the found order item for debugging
            print(f"Order Item found: {order_item.id}, Current Status: {order_item.status}")

            # Update the status to 'Confirmed'
            order_item.status = 'Confirmed'
            db.session.commit()

            # Log after committing for debugging
            print(f"Order Item confirmed: {order_item.id}, New Status: {order_item.status}")

            return jsonify({'success': True, 'message': 'Order confirmed!'})

        else:
            # Log if no order item found
            print(f"No pending order item found for Order ID: {order_id}")
            return jsonify({'success': False, 'message': 'Order cannot be confirmed. Invalid status.'})

    except Exception as e:
        # Log the exception for debugging
        print(f"Error occurred while confirming order: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to confirm order. Please try again later.'})




    
@app.route('/cancel_order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    data = request.get_json()
    cancellation_reason = data.get('cancellation_reason')

    try:
        # Get the user ID from session or request
        user_id = session.get('user_id')

        # Query the Account table to get the user's name
        user = Account.query.get(user_id)
        if user is None:
            return jsonify({"success": False, "message": "User not found"})
        


        # Insert cancellation reason into the notification table
        notification = Notification(
            user_id=user_id,  # User ID
            message=f"Your order with {user.firstname} {user.middlename}, {user.lastname} (Order ID: {order_id}) has been canceled. Reason: {cancellation_reason}",
            status="unread", notification_type="order_cancellation"
        )
        db.session.add(notification)
        db.session.commit()

        # Query for the order item associated with the given order_id
        allowed_statuses = ['Pending', 'Confirmed']
        order_item = OrderItem.query.filter_by(id=order_id).filter(OrderItem.status.in_(allowed_statuses)).first()

        # Check if order_item exists and its status can be updated
        if not order_item:
            return jsonify({"success": False, "message": "No eligible order item found or order is already cancelled."})

        # Update the order item's status to "Cancelled" and insert the cancellation reason
        order_item.status = "Cancelled"
        order_item.cancellation_reason = cancellation_reason  # Add this line
        db.session.commit()

        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})
    

@app.route('/seller_cancel_order/<int:order_id>', methods=['POST'])
def seller_cancel_order(order_id):
    data = request.get_json()
    cancellation_reason = data.get('cancellation_reason')

    try:
        # Get the user ID from session or request
        user_id = session.get('user_id')

        # Query the Account table to get the user's name
        user = Account.query.get(user_id)
        if user is None:
            return jsonify({"success": False, "message": "User not found"})
        


        # Insert cancellation reason into the notification table
        notification = Notification(
            user_id=user_id,  # User ID
            message=f"Your order with {user.firstname} {user.middlename}, {user.lastname} (Order ID: {order_id}) has been canceled. Reason: {cancellation_reason}",
            status="unread", notification_type="seller_order_cancellation"
        )
        db.session.add(notification)
        db.session.commit()

        # Query for the order item associated with the given order_id
        allowed_statuses = ['Pending', 'Confirmed']
        order_item = OrderItem.query.filter_by(id=order_id).filter(OrderItem.status.in_(allowed_statuses)).first()

        # Check if order_item exists and its status can be updated
        if not order_item:
            return jsonify({"success": False, "message": "No eligible order item found or order is already cancelled."})

        # Update the order item's status to "Cancelled" and insert the cancellation reason
        order_item.status = "Cancelled"
        order_item.cancellation_reason = cancellation_reason  # Add this line
        db.session.commit()

        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})
    

@app.route('/submit_feedback/<int:order_id>', methods=['POST'])
def submit_feedback(order_id):
    # Check if the order item exists and is in the "Received" status
    order_item = OrderItem.query.filter_by(id=order_id).first()
    if not order_item or order_item.status != 'Received':
        flash("Order is not in 'Received' status.", "danger")
        return redirect(request.referrer)

    # Retrieve feedback data from the form
    comment = request.form.get('comment')
    rating = request.form.get('rating')
    photo = request.files.get('photo')

    if not comment or not rating:
        flash("Comment and rating are required.", "danger")
        return redirect(request.referrer)

    # Get the logged-in user info
    user_id = session.get('user_id')
    if not user_id:
        flash("User not logged in.", "danger")
        return redirect(request.referrer)

    user = Account.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(request.referrer)

    user_name = f"{user.firstname} {user.middlename or ''} {user.lastname}".strip()

    # Handle file upload
    filename = None
    if photo:
        if not allowed_file(photo.filename):
            flash("Invalid file type. Only images are allowed.", "danger")
            return redirect(request.referrer)
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Create and save the feedback entry
    try:
        new_feedback = Feedback(
            product_id=order_item.product_id,
            user_id=user.id,
            role=user.role,
            user_name=user_name,
            comment=comment,
            rating=rating,
            photo=filename
        )

        db.session.add(new_feedback)
        db.session.commit()

        flash("Thank you for your feedback!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {e}", "danger")
    
    return redirect(url_for('product_details', product_id=order_item.product_id))


@app.route('/mark_order_received/<int:order_id>', methods=['POST'])
def mark_order_received(order_id):
    try:
        # Find the order item that matches the order_id and has status 'Out for Delivery'
        allowed_statuses = ['Delivered']
        order_item = OrderItem.query.filter_by(id=order_id).filter(OrderItem.status.in_(allowed_statuses)).first()

        if order_item:
            # Update the order item status to 'Received' and set the date_received
            order_item.status = 'Received'
            order_item.date_received = datetime.utcnow()  # Set the current UTC timestamp

            db.session.commit()
            return jsonify({'success': True, 'message': 'Order marked as received!'})

        else:
            return jsonify({'success': False, 'message': 'Order cannot be marked as received. Invalid status.'})

    except Exception as e:
        print(f"Error occurred while marking order as received: {str(e)}")
        return jsonify({'success': False, 'message': 'Error marking the order as received.'})
    

@app.route('/get_sales_data', methods=['GET'])
def get_sales_data():
    date = request.args.get('date')
    seller_id = session.get('user_id')  # Get the seller_id from the query parameters
    try:
        # Parse the date from the query parameter
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()

        # Query for total sales grouped by hour and filtered by seller_id
        sales = (
            db.session.query(
                func.hour(OrderItem.date_received).label('hour'),
                func.sum(OrderItem.product_price).label('total_sales')
            )
            .filter(func.date(OrderItem.date_received) == selected_date)
            .filter(OrderItem.status == 'Received')
            .filter(OrderItem.seller_id == seller_id)  # Filter by seller_id
            .group_by(func.hour(OrderItem.date_received))
            .all()
        )

        # Format data for the chart
        labels = [f'{hour}:00' for hour, _ in sales]
        data = [total_sales for _, total_sales in sales]

        return jsonify({'success': True, 'labels': labels, 'data': data})
    
    except Exception as e:
        print(f"Error fetching sales data: {str(e)}")
        return jsonify({'success': False, 'message': 'Error fetching sales data.'})



@app.route('/seller/orders')
def seller_orders():
    seller_id = session.get('user_id')
    if not seller_id:
        flash("You must be logged in to view your orders.", "error")
        return redirect(url_for('login'))

    # 1) fetch orders for this seller
    orders = (
        db.session.query(Order, Account.profile_picture, Account.firstname, Account.middlename, Account.lastname)
        .join(OrderItem, Order.id == OrderItem.order_id)
        .join(Account, Account.id == Order.user_id)
        .filter(OrderItem.seller_id == seller_id)
        .all()
    )

    # 2) load this seller's own location
    seller = Account.query.get(seller_id)
    province = seller.province
    city     = seller.city

    # 3) try fetching Riders in the same province or city
    riders = Account.query.filter(
        Account.role == 'Rider',
        Account.account_status == 'Approved',
        or_(
          Account.province == province,
          Account.city     == city
        )
    ).all()

    # 4) fallback to ALL approved Riders if none found locally
    if not riders:
        riders = Account.query.filter_by(
            role='Rider',
            account_status='Approved'
        ).all()

    # 5) render template with both orders & riders
    return render_template(
        'seller_orders.html',
        orders=orders,
        riders=riders
    )

@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    order_item_id = request.form.get('order_item_id')
    new_status    = request.form.get('new_status')

    if not order_item_id or not new_status:
        flash("Order ID and status are required", "error")
        return redirect(url_for('seller_orders'))

    try:
        order_item = OrderItem.query.get(order_item_id)
        if not order_item:
            flash("Order item not found", "error")
            return redirect(url_for('seller_orders'))

        # 1) Update status …
        order_item.status = new_status
        # 2) … and stamp the time of that change
        order_item.status_changed_at = datetime.now()

        db.session.commit()

        flash("Order status updated successfully", "success")
        return redirect(url_for('seller_orders'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('seller_orders'))
    


@app.route('/order_item/<int:item_id>/pickup', methods=['GET','POST'])
def assign_rider(item_id):
    conn = create_connection()
    cur  = conn.cursor(dictionary=True)

    # 1) Load the order_item
    cur.execute("SELECT * FROM order_items WHERE id=%s", (item_id,))
    order_item = cur.fetchone()
    if not order_item:
        cur.close()
        conn.close()
        abort(404, "Order item not found.")

    # 2) Fetch ALL approved Riders
    cur.execute("""
      SELECT id, firstname, lastname
      FROM accounts
      WHERE role = 'Rider'
        AND account_status = 'Approved'
    """)
    riders = cur.fetchall()

    # 3) Handle form submission
    if request.method == 'POST':
        rider_id = request.form.get('rider_id')
        if not rider_id:
            flash("Please select a rider before confirming.", "warning")
        else:
            selected = next((r for r in riders if str(r['id']) == rider_id), None)
            if not selected:
                flash("Invalid rider selection.", "danger")
            else:
                ridername = f"{selected['firstname']} {selected['lastname']}"

                # Use MySQL NOW() to set status_changed_at on the DB side:
                cur.execute("""
                  UPDATE order_items
                    SET status              = 'Waiting for Pick up',
                        ridername           = %s,
                        rider_id            = %s,
                        status_changed_at   = NOW()
                  WHERE id = %s
                """, (ridername, selected['id'], item_id))

                # — or, if you prefer Python timestamps:
                # now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # cur.execute("""
                #   UPDATE order_items
                #     SET status              = %s,
                #         ridername           = %s,
                #         rider_id            = %s,
                #         status_changed_at   = %s
                #   WHERE id = %s
                # """, ('Waiting for Pick up', ridername, selected['id'], now, item_id))

                conn.commit()
                cur.close()
                conn.close()
                return redirect(url_for('seller_orders'))

    # 4) Render form (GET or validation errors)
    cur.close()
    conn.close()
    return render_template(
        'assign_pickup.html',
        order_item=order_item,
        riders=riders
    )

@app.route('/product/<int:product_id>')
def product_details(product_id):
    # Fetch the product from the Inventory table
    inventory_item = Inventory.query.get(product_id)
    if inventory_item is None:
        abort(404)

    # Fetch the seller's details: profile_picture and full name
    seller = (
        db.session.query(
            Account.profile_picture,
            Account.firstname,
            Account.middlename,
            Account.lastname,
            Account.status
        )
        .filter(Account.id == inventory_item.seller_id)
        .first()
    )

    if seller:
        seller_profile_picture = seller.profile_picture
        seller_full_name = f"{seller.firstname} {seller.middlename or ''} {seller.lastname}".strip()
        seller_status = seller.status
    else:
        seller_profile_picture = None
        seller_full_name = "Unknown Seller"

    # Fetch variations with their associated attributes and prices/stock
    variations = ProductVariation.query.filter_by(product_id=product_id).all()
    formatted_variations = []
    for variation in variations:
        # Fetch attributes for each variation, including price and stock from the VariationAttribute table
        attributes = VariationAttribute.query.filter_by(variation_id=variation.id).all()
        variation_details = []
        for attribute in attributes:
            # Each attribute contains price, stock, and image information
            variation_details.append({
                "attribute_name": attribute.attribute_name,
                "attribute_value": attribute.attribute_value,
                "attribute_price": attribute.attribute_price,  # Price for this variation
                "attribute_stock": attribute.attribute_stock,  # Stock for this variation
                "attribute_image": attribute.attribute_image  # Image for this variation
            })
        formatted_variations.append({
            "id": variation.id,
            "attributes": variation_details  # Includes price, stock, and image details for each attribute
        })

    # Fetch feedbacks and combine firstname, middlename, lastname into user_name
    feedbacks = (
        db.session.query(
            Feedback.id,
            Feedback.product_id,
            Feedback.comment,
            Feedback.rating,
            Feedback.photo,
            Feedback.created_at.label('timestamp'),
            Account.firstname,
            Account.middlename,
            Account.lastname
        )
        .join(Account, Feedback.user_id == Account.id)
        .filter(Feedback.product_id == product_id)
        .all()
    )

    # Format feedbacks with full name as user_name
    formatted_feedbacks = [
        {
            'id': feedback.id,
            'comment': feedback.comment,
            'rating': feedback.rating,
            'photo': feedback.photo,
            'timestamp': feedback.timestamp,
            'user_name': f"{feedback.firstname} {feedback.middlename or ''} {feedback.lastname}".strip()
        }
        for feedback in feedbacks
    ]

    # Render the product details page with product info, variations, feedbacks, seller profile picture, and seller name
    return render_template(
        'product_details.html',
        product=inventory_item,
        variations=formatted_variations,
        feedbacks=formatted_feedbacks,
        seller_profile_picture=seller_profile_picture,
        seller_full_name=seller_full_name,
        seller_status=seller_status  # Add this to the template
    )

@app.route('/shop/<int:seller_id>')
def view_shop(seller_id):
    # Fetch the seller's details
    seller = (
        db.session.query(
            Account.id,
            Account.firstname,
            Account.middlename,
            Account.lastname,
            Account.profile_picture,
            Account.shop_name,
            Account.status

        )
        .filter(Account.id == seller_id)
        .first()
    )

    if seller is None:
        abort(404, description="Seller not found")

    seller_full_name = f"{seller.firstname} {seller.middlename or ''} {seller.lastname}".strip()

    seller_status = seller.status

    # Fetch the inventory items associated with the seller
    inventory_items = Inventory.query.filter_by(seller_id=seller_id).all()

    # Render the shop page
    return render_template(
        'shop.html',
        seller_id=seller_id,
        seller_name=seller_full_name,
        profile_picture=seller.profile_picture,
        inventory_items=inventory_items,
        seller_shop_name=seller.shop_name,
        seller_status=seller_status
    )


@app.route('/update_quantity/<int:product_id>', methods=['POST'])
def update_quantity(product_id):
    product = Inventory.query.get(product_id)
    action = request.form['action']
    current_quantity = int(request.form.get('quantity', 1))

    if action == 'increase':
        if current_quantity + 1 > product.quantity:
            flash(f'Cannot add more than {product.quantity} items.', 'error')
        else:
            # Logic to add to cart
            current_quantity += 1

    elif action == 'decrease':
        if current_quantity - 1 < 1:
            flash('Quantity cannot be less than 1.', 'error')
        else:
            # Logic to remove from cart
            current_quantity -= 1

    # Update session or any other logic
    session['current_quantity'] = current_quantity
    return redirect(url_for('product_details', product_id=product_id))




@app.route('/seller/home')
def seller_home():
    # Check if user is logged in
    if 'user_id' not in session:
        return "Please log in to view your inventory", 403

    user_id = session.get('user_id')

    # Calculate total stocks based on the logged-in user's ID
    total_stocks = db.session.query(func.sum(Inventory.quantity)).filter_by(seller_id=user_id).scalar() or 0

    # Count total orders made by the logged-in user, excluding canceled orders
    allowed_statuses = ['Pending', 'Confirmed', 'Preparing To Ship', 'Order Shipped', 'Out for Delivery', 'Received']
    total_orders = db.session.query(func.count(OrderItem.id)).filter(
        OrderItem.seller_id == user_id,
        OrderItem.status.in_(allowed_statuses)
    ).scalar() or 0

    # Calculate total of 'Received' orders
    total_received = db.session.query(func.sum(OrderItem.product_price)).filter(
        OrderItem.seller_id == user_id,
        OrderItem.status == 'Received'
    ).scalar() or 0

    # Calculate the 10% commission from total received
    total_commission = total_received * 0.10

    # Query the products with variations and attributes
    products = db.session.query(Inventory, ProductVariation, VariationAttribute).join(
        ProductVariation, Inventory.id == ProductVariation.product_id
    ).join(VariationAttribute, ProductVariation.id == VariationAttribute.variation_id).filter(
        Inventory.seller_id == user_id
    ).all()

    # Process the products to structure them correctly for rendering
    inventory = {}
    for product in products:
        product_id = product.Inventory.id  # Product ID
        if product_id not in inventory:
            inventory[product_id] = {
                'id': product_id,
                'product_name': product.Inventory.product_name,
                'price': product.Inventory.price,
                'quantity': product.Inventory.quantity,
                'category': product.Inventory.category,
                'details': product.Inventory.details,
                'product_picture': product.Inventory.product_picture,
                'variations': []
            }
        if product.ProductVariation:
            inventory[product_id]['variations'].append({
                'attribute_name': product.VariationAttribute.attribute_name,
                'attribute_value': product.VariationAttribute.attribute_value,
            })

    return render_template(
        'seller_home.html',
        products=inventory.values(),
        total_stocks=total_stocks,
        total_orders=total_orders,
        total_received=f"{total_received:,.2f}",
        total_commission=f"{total_commission:,.2f}"
    )





 


    

@app.route('/seller/sales')
def seller_sales():
    try:
        # Get the logged-in seller's ID (assumed to be stored in session or passed in some way)
        seller_id = session.get('user_id')  # Update this to match your method of getting the logged-in seller's ID

        if not seller_id:
            return "Seller not logged in."

        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Count sellers
        cursor.execute("SELECT COUNT(*) FROM accounts WHERE role = 'Seller'")
        sellers_count = cursor.fetchone()[0]

        # Count buyers
        cursor.execute("SELECT COUNT(*) FROM accounts WHERE role = 'Buyer'")
        buyers_count = cursor.fetchone()[0]

        # Get the total of 'Received' orders for the specific seller
        cursor.execute("""
            SELECT COALESCE(SUM(product_price), 0) AS total_received
            FROM order_items
            WHERE status = 'Received' AND seller_id = %s
        """, (seller_id,))
        total_received = float(cursor.fetchone()[0])  # Convert to float for consistency

        # Find the most used product_id for the specific seller
        cursor.execute("""
            SELECT product_id
            FROM order_items
            WHERE seller_id = %s
            GROUP BY product_id
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """, (seller_id,))
        most_used_product = cursor.fetchone()
        most_used_product_id = most_used_product[0] if most_used_product else None

        # Get details for the most used product_id for the specific seller
        if most_used_product_id:
            cursor.execute("""
                SELECT product_image, product_name, variation_name, variation_value, product_price, status
                FROM order_items
                WHERE product_id = %s AND seller_id = %s
            """, (most_used_product_id, seller_id))
            order_items = [
                {
                    'product_image': row[0],
                    'product_name': row[1],
                    'variation_name': row[2],
                    'variation_value': row[3],
                    'product_price': f"{float(row[4]):,.2f}",  # Format price with peso sign
                    'status': row[5]
                }
                for row in cursor.fetchall()
            ]
        else:
            order_items = []  # No product data available

        # Count the number of 'Pending' statuses for the specific seller
        cursor.execute("""
            SELECT COUNT(*) 
            FROM order_items
            WHERE status = 'Pending' AND seller_id = %s
        """, (seller_id,))
        pending_count = cursor.fetchone()[0]

        # Count the number of 'Received' statuses for the specific seller
        cursor.execute("""
            SELECT COUNT(*) 
            FROM order_items
            WHERE status = 'Received' AND seller_id = %s
        """, (seller_id,))
        completed_count = cursor.fetchone()[0]

        cursor.close()
        cnx.close()

        return render_template(
            'seller_sales.html',
            sellers_count=sellers_count,
            buyers_count=buyers_count,
            total_received=f"{total_received:,.2f}",  # Format total received
            order_items=order_items,
            pending_count=pending_count,
            completed_count=completed_count
        )
    except Exception as e:
        print("Error: ", e)
        return "An error occurred: " + str(e)



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        firstname = form.firstname.data
        middlename = form.middlename.data
        lastname = form.lastname.data
        birthdate = form.birthdate.data
        sex = form.sex.data
        housenumber = form.housenumber.data
        street = form.street.data
        city = form.city.data
        province = form.province.data
        region = form.region.data
        barangay = form.barangay.data
        email = form.email.data
        password = form.password.data  
        role = form.role.data
        shop_name = form.shop_name.data if role == "Seller" else None

        # Handle file uploads
        profile_picture = form.profile_picture.data
        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None

        valid_id = form.valid_id.data
        if valid_id:
            valid_id_filename = secure_filename(valid_id.filename)
            valid_id.save(os.path.join(app.config['UPLOAD_FOLDER'], valid_id_filename))
        else:
            valid_id_filename = None

        # Generate OTP for verification
        otp = generate_otp()

        account_status = 'Approved' if role == 'Buyer' else 'Pending'

        data = (firstname, middlename, lastname, birthdate, sex, housenumber,street, city, province, region, barangay, email, password, role, filename, valid_id_filename, shop_name, otp, account_status)

        # Create database connection
        connection = create_connection()
        if not connection:
            flash("Failed to connect to the database.", "error")
            return redirect(url_for('register'))

        cursor = connection.cursor()
        try:
            # Insert user data into the accounts table
            cursor.execute("""
                INSERT INTO accounts (
                    firstname, middlename, lastname, birthdate, sex, housenumber, street, city, 
                    province, region, barangay, email, password, role, profile_picture, 
                    valid_id, shop_name, otp, account_status
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, data)

            # Commit the transaction to get the new user ID
            connection.commit()

            # Retrieve the user ID of the newly inserted account
            user_id = cursor.lastrowid

            # Insert into the notifications table using the new user_id
            notification_data = (user_id, 'Account Created', 'Please verify your account via OTP.', 'unread')
            cursor.execute("""
                INSERT INTO notifications (user_id, notification_type, message, status) 
                VALUES (%s, %s, %s, %s)
            """, notification_data)

            # Commit the notification insert
            connection.commit()

            # Send OTP email to the user
            send_otp_email(email, otp)

            return redirect(url_for('verify_otp', email=email))

        except Exception as db_err:
            flash(f"An error occurred during registration: {db_err}", "error")
            logging.error(f"Database error during registration: {db_err}", exc_info=True)
        finally:
            cursor.close()
            connection.close()

    return render_template('register.html', form=form)





@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    email = request.args.get('email')
    if request.method == 'POST':
        otp = request.form.get('otp')
        
        # Ensure OTP is provided
        if not otp:
            flash("OTP is required.", "error")
            return redirect(url_for('verify_otp', email=email))

        try:
            connection = create_connection()
            if not connection:
                flash("Failed to connect to the database.", "error")
                return redirect(url_for('home'))

            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM accounts WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user:
                # Check if OTP is correct and matches
                if user['otp'] == int(otp):
                    # OTP is valid, update account status
                    if user['role'] == 'Seller':
                        # Set account status to 'pending' for sellers
                        cursor.execute("UPDATE accounts SET account_status = 'pending', otp = NULL WHERE email = %s", (email,))
                        connection.commit()

                        # Add a notification for admin
                        cursor.execute("""
                            INSERT INTO notifications (user_id, message, notification_type, status) 
                            VALUES (%s, %s, %s, 'unread')
                        """, (user['id'], f"A new seller account for {user['firstname']} {user['lastname']} is awaiting approval.", 'seller_approval'))
                        connection.commit()

                    else:
                        # Directly approve buyers
                        cursor.execute("UPDATE accounts SET account_status = 'Approved', otp = NULL WHERE email = %s", (email,))
                        connection.commit()

                    flash("OTP verification successful! You can now log in.", "success")
                else:
                    flash("Invalid OTP. Please try again.", "error")
            else:
                flash("Account not found. Please try again.", "error")

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            logging.error(f"Error during OTP verification: {e}", exc_info=True)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return redirect(url_for('home'))

    return render_template('verify_otp.html', email=email)



@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    email = request.form.get('email')
    if not email:
        flash("Email is required to resend OTP.", "error")
        return redirect(url_for('verify_otp', email=email))

    connection = create_connection()
    if not connection:
        return redirect(url_for('home'))

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM accounts WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user:
        otp = generate_otp()  # Generate a new OTP
        # Store the new OTP in the database (replace the old one)
        cursor.execute("UPDATE accounts SET otp = %s WHERE email = %s", (otp, email))
        connection.commit()

        # Send the OTP to the user's email
        send_otp_email(email, otp)

        flash("A new OTP has been sent to your email. Please check your inbox.", "success")
    else:
        flash("No account found with that email.", "error")

    cursor.close()
    connection.close()

    return redirect(url_for('verify_otp', email=email))


@app.route('/seller/add_to_inventory', methods=['GET', 'POST'])
@login_required
def add_to_inventory():
    if request.method == 'POST':
        print("Form Data Received:", request.form)

        # Product details
        product_name = request.form.get('product_name')
        price = request.form.get('price')
        category = request.form.get('category')
        details = request.form.get('details')
        product_picture = request.files.get('product_picture')
        shop_name = session.get('shop_name')  # Assuming shop_name is in the session
        seller_id = session.get('user_id')  # Retrieve logged-in user ID

        # Validate inputs
        if not product_name or not price or not category:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('seller_inventory'))

        # Save main product picture
        picture_filename = None
        if product_picture:
            picture_filename = secure_filename(product_picture.filename)
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_filename)
            product_picture.save(picture_path)

        try:
            with create_connection() as connection:
                cursor = connection.cursor()

                # Insert product into the inventory table
                cursor.execute("""
                    INSERT INTO inventory (product_name, price, quantity, category, details, product_picture, shop_name, seller_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (product_name, price, 0, category, details, picture_filename, shop_name, seller_id))

                product_id = cursor.lastrowid  # Get the product ID of the newly inserted product

                # Retrieve variation data from the form
                variation_names = request.form.getlist('variation_name[]')
                variation_values = [request.form.getlist(f'variation_value[{i}][]') for i in range(len(variation_names))]
                stock_values = [request.form.getlist(f'stock[{i}][]') for i in range(len(variation_names))]
                variation_prices = [request.form.getlist(f'variation_price[{i}][]') for i in range(len(variation_names))]

                total_stock = 0  # Initialize total stock for this product

                # Insert variations and their attributes
                for index, variation_name in enumerate(variation_names):
                    cursor.execute("""
                        INSERT INTO product_variations (product_id)
                        VALUES (%s)
                    """, (product_id,))
                    variation_id = cursor.lastrowid  # Get the variation ID

                    insert_data = []
                    values_for_variation = variation_values[index]
                    stock_for_variation = stock_values[index]
                    price_for_variation = variation_prices[index]

                    for value_index, value in enumerate(values_for_variation):
                        if value:
                            image_file = request.files.get(f'variation_image[{index}][{value_index}]')
                            value_image_filename = None
                            
                            # Save image if it exists
                            if image_file:
                                value_image_filename = secure_filename(image_file.filename)
                                value_image_path = os.path.join(app.config['UPLOAD_FOLDER'], value_image_filename)
                                image_file.save(value_image_path)

                            # Accumulate total stock
                            stock_value = int(stock_for_variation[value_index]) if len(stock_for_variation) > value_index and stock_for_variation[value_index].isdigit() else 0
                            total_stock += stock_value

                            # Collect data for batch insertion
                            insert_data.append((
                                variation_id,
                                variation_name,
                                value,
                                value_image_filename,
                                price_for_variation[value_index] if len(price_for_variation) > value_index else None,
                                stock_value
                            ))

                    # Perform batch insert for variation attributes
                    if insert_data:
                        cursor.executemany("""
                            INSERT INTO variation_attributes (variation_id, attribute_name, attribute_value, attribute_image, attribute_price, attribute_stock)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, insert_data)
                        print(f"Inserted {len(insert_data)} variation attributes for variation {variation_name}")

                # Update the total stock in the inventory table
                cursor.execute("""
                    UPDATE inventory
                    SET quantity = %s
                    WHERE id = %s
                """, (total_stock, product_id))

                connection.commit()  # Commit all changes to the database
                flash('Product added successfully!', 'success')
        except Error as e:
            flash(f"An error occurred: {e}", 'error')
            print(f"Database error: {e}")

        return redirect(url_for('seller_inventory'))

    return render_template('seller_inventory.html')



@app.route('/get_product_details/<int:product_id>', methods=['GET'])
def get_product_details(id):
    product = Inventory.query.get(id)
    if product:
        # Assuming the Product model has these fields, modify according to your model
        images = [image.filename for image in product.images]  # Modify this based on your images relationship
        return jsonify({
            'product_name': product.product_name,
            'price': product.price,
            'quantity': product.quantity,
            'description': product.description,
            'images': images
        })
    return jsonify({'error': 'Product not found'}), 404



@app.route('/seller/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    connection = create_connection()
    if not connection:
        flash('Database connection failed!', 'error')
        return redirect(url_for('seller_inventory'))

    try:
        cursor = connection.cursor()

        # Check if the product exists in the inventory
        print(f"Checking if product with ID {product_id} exists in inventory.")
        cursor.execute("SELECT * FROM inventory WHERE id = %s", (product_id,))
        product = cursor.fetchone()

        if not product:
            flash('Product not found!', 'error')
            return redirect(url_for('seller_inventory'))

        print(f"Product found: {product}")
        
        # Insert the product into the inventory_archive table
        print(f"Moving product to inventory_archive with ID {product_id}")
        cursor.execute("""
            INSERT INTO inventory_archive (inventory_id, product_name, price, quantity, category, details, product_picture, created_at, shop_name, seller_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (product[0], product[1], product[2], product[3], product[4], product[5], product[6], product[7], product[8], product[9]))
        print(f"Product moved to inventory_archive.")

        # Move product variations for product_id to archived_product_variations
        print(f"Moving product variations for product_id {product_id}")
        cursor.execute("SELECT id FROM product_variations WHERE product_id = %s", (product_id,))
        variations = cursor.fetchall()
        for variation in variations:
            print(f"Moving variation: {variation}")
            cursor.execute("""
                INSERT INTO archived_product_variations (product_variation_id, product_id)
                VALUES (%s, %s)
            """, (variation[0], product_id))
        print(f"Product variations moved.")

        # Move variation attributes to archived_variation_attributes
        print(f"Moving variation attributes for product_id {product_id}")
        cursor.execute("""
            SELECT va.id, va.variation_id, va.attribute_name, va.attribute_value 
            FROM variation_attributes AS va
            JOIN product_variations AS pv ON va.variation_id = pv.id
            WHERE pv.product_id = %s
        """, (product_id,))
        attributes = cursor.fetchall()
        for attribute in attributes:
            print(f"Moving attribute: {attribute}")
            cursor.execute("""
                INSERT INTO archived_variation_attributes (variation_attribute_id, variation_id, attribute_name, attribute_value)
                VALUES (%s, %s, %s, %s)
            """, (attribute[0], attribute[1], attribute[2], attribute[3]))
        print(f"Variation attributes moved.")

        # Delete variation attributes and product variations from original tables
        print(f"Deleting variation attributes and product variations from original tables.")
        cursor.execute("DELETE FROM variation_attributes WHERE variation_id IN (SELECT id FROM product_variations WHERE product_id = %s)", (product_id,))
        cursor.execute("DELETE FROM product_variations WHERE product_id = %s", (product_id,))

        # Finally, delete the product from the inventory table
        print(f"Deleting product with ID {product_id} from inventory.")
        cursor.execute("DELETE FROM inventory WHERE id = %s", (product_id,))

        connection.commit()
        flash('Product archived successfully!', 'success')

    except Exception as e:
        connection.rollback()  # Roll back any changes in case of an error
        flash(f'Error archiving product: {str(e)}', 'error')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('seller_inventory'))


@app.route('/seller/inventory')
def seller_inventory():
    # Assuming you're using Flask-Login or another method to retrieve the logged-in user's ID
    user_id = session.get('user_id')

    # Using context manager for database connection
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Fetch products along with their variations and attributes for the logged-in user
        cursor.execute(""" 
            SELECT i.id, i.product_name, i.price, i.quantity, i.category, i.details, i.product_picture, 
                   pv.id as variation_id, va.attribute_name, va.attribute_value, va.attribute_price, va.attribute_stock, va.id
            FROM inventory i
            LEFT JOIN product_variations pv ON i.id = pv.product_id
            LEFT JOIN variation_attributes va ON pv.id = va.variation_id
            WHERE i.seller_id = %s
        """, (user_id,))
        products = cursor.fetchall()

    except Exception as e:
        # Handle error (e.g., log it or show a message to the user)
        print(f"Database error: {e}")
        return "An error occurred while fetching the inventory. Please try again later."

    finally:
        # Ensure the connection is closed
        cursor.close()
        connection.close()

    # Process the products to structure them correctly for rendering
    inventory = {}
    for product in products:
        product_id = product[0]  # Product ID
        if product_id not in inventory:
            inventory[product_id] = {
                'id': product_id,
                'product_name': product[1],  # Product name
                'price': product[2],          # Price
                'quantity': product[3],       # Quantity
                'category': product[4],       # Category
                'details': product[5],        # Details
                'product_picture': product[6], # Picture
                'variations': []               # Variations
            }
        if product[7]:  # Check for variation_id
            inventory[product_id]['variations'].append({
                'attribute_name': product[8],  # Attribute name
                'attribute_value': product[9],  # Attribute value
                'attribute_price': product[10],  # Attribute price
                'attribute_stock': product[11],  # Attribute stock
                'id': product[12],  # Attribute stock
            })

    # If no products are found, inform the seller
    if not inventory:
        flash('No products found in your inventory.', 'warning')

    # Return the values of the inventory dictionary for rendering
    return render_template('seller_inventory.html', products=inventory.values())



@app.route('/seller/edit_product/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    print(f"Form Data: {request.form}")  # Log form data to debug

    product_name = request.form['product_name']
    price = request.form['price']
    category = request.form['category']
    details = request.form['details']

    # Fetch the product
    product = Inventory.query.get(product_id)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('seller_inventory'))

    # Update product details
    product.product_name = product_name
    product.price = price
    product.category = category
    product.details = details

    # Handle variations update
    for variation in product.variations:
        # Retrieve the attribute_id from the form
        attribute_id = request.form.get(f'attribute_id_{variation.id}')
        print(f"Variation ID: {variation.id}, Attribute ID: {attribute_id}")  # Debug output

        # Only process the variation if attribute_id is available
        if attribute_id:
            # Fetch the related variation attribute from the variation_attributes table
            attribute = VariationAttribute.query.get(attribute_id)

            if attribute:
                attribute_name = request.form.get(f'attribute_name_{variation.id}')
                attribute_value = request.form.get(f'attribute_value_{variation.id}')
                attribute_price_str = request.form.get(f'attribute_price_{variation.id}')
                attribute_stock_str = request.form.get(f'attribute_stock_{variation.id}')
                
                # Handle price conversion with a default value if None
                attribute_price = float(attribute_price_str) if attribute_price_str else 0.0
                
                # Handle stock conversion with a default value if None
                attribute_stock = int(attribute_stock_str) if attribute_stock_str else 0

                # Check if the attribute_name needs to be updated
                if attribute.attribute_name == attribute_name:
                    # Check if the attribute_value needs to be updated
                    if attribute.attribute_value != attribute_value:
                        print(f"Updating Attribute Value: {attribute_value}")
                        attribute.attribute_value = attribute_value

                    # Check if the attribute_price needs to be updated
                    if attribute.attribute_price != attribute_price:
                        print(f"Updating Attribute Price: {attribute_price}")
                        attribute.attribute_price = attribute_price

                    # Check if the attribute_stock needs to be updated
                    if attribute.attribute_stock != attribute_stock:
                        print(f"Updating Attribute Stock: {attribute_stock}")
                        attribute.attribute_stock = attribute_stock
                else:
                    print(f"Attribute Name {attribute_name} does not match the stored value")
            else:
                print(f"No matching attribute found for attribute_id {attribute_id}")
        else:
            print(f"No attribute_id found for variation {variation.id}")

    # Commit all changes to the database
    db.session.commit()
    flash('Product and variations updated successfully', 'success')
    return redirect(url_for('seller_inventory'))



@app.route('/seller/feedback')
def seller_feedback():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    # Fetch inventory items for the logged-in user (seller)
    inventory_items = Inventory.query.filter_by(seller_id=user_id).all()

    if not inventory_items:
        return render_template('seller_feedback.html', feedbacks=[])

    # Get feedbacks for the products owned by the logged-in user
    feedbacks = Feedback.query.filter(Feedback.product_id.in_([item.id for item in inventory_items])).all()

    # Pass additional product information (name, image) to the template
    for feedback in feedbacks:
        product = Inventory.query.get(feedback.product_id)
        feedback.product_name = product.product_name  # Assuming the Product model has a 'name' field
        feedback.product_image = product.product_picture  # Assuming the Product model has an 'image_filename' field
        feedback.date_posted = feedback.created_at  # Assuming the Feedback model has a 'date_posted' field

    return render_template('seller_feedback.html', feedbacks=feedbacks)

@app.route('/seller_messages')
def seller_messages():
    return render_template('seller_messages.html')




@app.route('/logout', methods=['POST'])
@login_required
def logout():
    user_id = session.get('user_id')  # Get the user's ID from the session

    if user_id:
        # Update the user's status to 'Offline' in the database
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    UPDATE accounts
                    SET status = 'Offline'
                    WHERE id = %s
                """, (user_id,))
                connection.commit()
            except Exception as e:
                flash('An error occurred while updating the user status.', 'error')
            finally:
                cursor.close()
                connection.close()

    # Clear the session to log the user out
    session.pop('user_id', None)
    session.pop('shop_name', None)
    session.pop('role', None)

    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))  # Redirect to the home page or login page

config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'ecommerce',
    'use_pure': True  # Keep this to avoid SSL issues
}


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Email and password fields cannot be empty.", "error")
            return redirect(url_for('login'))

        connection = create_connection()
        if not connection:
            flash("Database connection error.", "error")
            return redirect(url_for('home'))

        cursor = connection.cursor(dictionary=True)

        try:
            # Check if the user exists in archive_users
            cursor.execute("""
                SELECT status, firstname, lastname, ban_reason
                FROM archive_users 
                WHERE email = %s
            """, (email,))
            archived_user = cursor.fetchone()

            if archived_user:
                user_data = {
                    "user_name": f"{archived_user.get('firstname', '')} {archived_user.get('lastname', '')}",
                    "ban_reason": archived_user.get('ban_reason', 'Account banned.'),
                }
                if archived_user['status'] == 'permanent_ban':
                    return render_template('login2.html', banned=True, permanent_ban=True, **user_data)
                elif archived_user['status'] == 'banned':
                    return render_template('login2.html', banned=True, **user_data)

            # Check if the user is an admin
            cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
            admin_user = cursor.fetchone()

            if admin_user and admin_user['role'] == 'Admin' and admin_user['password'] == password:
                session['user_id'] = admin_user['id']
                session['role'] = 'Admin'
                return redirect(url_for('admin_dashboard'))

            # Check regular accounts
            cursor.execute("SELECT * FROM accounts WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user:
                # Handle account status
                if user['status'] == 'temporary_ban':
                    temp_ban_until = user.get('temp_ban_until')
                    if temp_ban_until:
                        # Handle case where temp_ban_until might be a string
                        if isinstance(temp_ban_until, str):
                            try:
                                temp_ban_until = datetime.fromisoformat(temp_ban_until)
                            except ValueError:
                                temp_ban_until = None
                        elif isinstance(temp_ban_until, datetime):
                            # If it's already a datetime object, no need to convert
                            pass

                    if temp_ban_until and datetime.now() > temp_ban_until:
                        # Unban the user
                        cursor.execute("""
                            UPDATE accounts
                            SET status = 'Offline', banned_at = NULL, ban_reason = NULL, temp_ban_until = NULL
                            WHERE id = %s
                        """, (user['id'],))
                        connection.commit()
                    else:
                        # Calculate remaining time for the countdown
                        remaining_time = temp_ban_until - datetime.now() if temp_ban_until else None
                        user_data = {
                            "user_name": f"{user.get('firstname', '')} {user.get('lastname', '')}",
                            "ban_reason": user.get('ban_reason', 'Your account has been temporarily banned.'),
                            "temp_ban_until": temp_ban_until.isoformat() if temp_ban_until else None,
                            "remaining_time": remaining_time.total_seconds() if remaining_time else 0
                        }
                        return render_template('login2.html', temporary_ban=True, **user_data)

                # Check account approval status
                if user['account_status'] == 'Rejected':
                    flash('Your account has been rejected. Please contact support.', 'error')
                elif user['account_status'] == 'pending':
                    flash('Your account is pending approval. Please wait for approval before logging in.', 'warning')
                elif user['password'] == password:
                    session['user_id'] = user['id']
                    session['shop_name'] = user.get('shop_name')
                    session['role'] = user['role']

                    cursor.execute("UPDATE accounts SET status = 'Online' WHERE email = %s", (email,))
                    connection.commit()
                    cursor.close()
                    connection.close()

                    return redirect(url_for('seller_home' if user['role'] == 'Seller' else 'index'))
                else:
                    flash('Invalid credentials. Please check your email and password.', 'error')
            else:
                flash('No account found with that email. Please register.', 'error')

        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('login'))

    return render_template('login2.html')




@app.route('/admin_sales', methods=['POST', 'GET'])
def admin_sales():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Count sellers
        cursor.execute("SELECT COUNT(*) FROM accounts WHERE role = 'Seller'")
        sellers_count = cursor.fetchone()[0]

        # Count buyers
        cursor.execute("SELECT COUNT(*) FROM accounts WHERE role = 'Buyer'")
        buyers_count = cursor.fetchone()[0]

        # Query to get order data and calculate 10% commission on the backend
        cursor.execute("""
            SELECT product_image, product_name, variation_name, product_price, 
                   (product_price * 0.10) AS commission, status
            FROM order_items
        """)
        order_data = cursor.fetchall()

        # Format data to pass to the template
        order_items = [
            {
                'product_image': row[0],
                'product_name': row[1],
                'variation_name': row[2],
                'product_price': f"{row[3]:,.2f}",  # Format price with peso sign
                'commission': f"{float(row[4]):,.2f}",  # Format commission with peso sign
                'status': row[5]
            }
            for row in order_data
        ]

        # Calculate the total commission by summing all individual commissions
        total_commission = sum(float(row[4]) for row in order_data)

        # Count the number of 'Pending' statuses
        cursor.execute("SELECT COUNT(*) FROM order_items WHERE status = 'Pending'")
        pending_count = cursor.fetchone()[0]

        # Count the number of 'Completed' statuses
        cursor.execute("SELECT COUNT(*) FROM order_items WHERE status = 'Completed'")
        completed_count = cursor.fetchone()[0]

        cursor.close()
        cnx.close()

        return render_template(
            'Admin_sales.html', 
            sellers_count=sellers_count, 
            buyers_count=buyers_count, 
            order_data=order_items, 
            pending_count=pending_count, 
            completed_count=completed_count,
            total_commission=f"₱{total_commission:,.2f}"  # Format total commission with peso sign
        )
    except Exception as e:
        print("Error: ", e)
        return "An error occurred: " + str(e)


@app.route('/admin_management')
def admin_management():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Query for sellers
        cursor.execute("SELECT profile_picture, lastname, firstname, created_at, account_status, id, email FROM accounts  WHERE role IN ('Seller', 'Rider') AND account_status = 'pending'")
        sellers = cursor.fetchall()

        cursor.execute("SELECT profile_picture, lastname, firstname, created_at, account_status, id, email FROM accounts WHERE role = 'Seller' AND account_status = 'Approved'")
        sellers_approved = cursor.fetchall()

        # Query for buyers
        cursor.execute("SELECT profile_picture, lastname, firstname, created_at FROM accounts WHERE role = 'Buyer'")
        buyers = cursor.fetchall()

        cursor.close()
        cnx.close()

        return render_template('Admin_management.html', accounts=sellers, buyers=buyers, sellers_approved=sellers_approved)
    except Exception as e:
        print("Error: ", e)
        return "An error occurred: " + str(e)


@app.route('/admin_dashboard')
def admin_dashboard():
    # Check if the user is an admin
    if 'role' not in session or session['role'] != 'Admin':
        flash("Access denied. Admins only.", "error")
        return redirect(url_for('login'))

    # Establish a database connection
    connection = create_connection()
    if not connection:
        return "Database connection error", 500

    cursor = connection.cursor(dictionary=True)

    # Fetch all users' data (Sellers and Buyers) from the accounts table
    cursor.execute("""
    SELECT 
        profile_picture,
        lastname,
        firstname,
        CONCAT(street, ', ', barangay, ', ', city, ', ', province, ', ', region) AS address,
        role,
        sex,
        created_at,
        status,
        shop_name,
        banned_at,
        ban_reason
    FROM accounts
    WHERE role IN ('Seller', 'Buyer')
    """)
    all_users = cursor.fetchall()

    # Get the count of buyers in the accounts table
    cursor.execute("""
        SELECT COUNT(*) AS buyer_count 
        FROM accounts 
        WHERE role IN ('Buyer','Seller')
    """)
    buyer_count = cursor.fetchone()['buyer_count']

     # Get the count of pending accounts
    cursor.execute("""
        SELECT COUNT(*) AS pending_count
        FROM accounts
        WHERE account_status = 'pending'
    """)
    pending_count = cursor.fetchone()['pending_count']

    # Calculate the total commission from all sellers
    cursor.execute("""
        SELECT SUM(product_price) * 0.10 AS total_commission 
        FROM order_items 
        WHERE status = 'Received'
    """)
    total_commission = cursor.fetchone()['total_commission'] or 0.0

    # Close the cursor and database connection
    cursor.close()
    connection.close()

    # Pass data to the template
    return render_template(
        'admin_dashboard.html',
        all_users=all_users,
        buyer_count=buyer_count,
        total_commission=f"{total_commission:,.2f}",
        pending_count=pending_count  # Pass pending_count to template
    )



    
#admin_approve_account
@app.route('/approve_account/<int:user_id>', methods=['POST'])
def approve_account(user_id):
    connection = create_connection()
    if not connection:
        flash("Database connection failed.", "error")
        return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard or the relevant page

    cursor = connection.cursor()
    cursor.execute("UPDATE accounts SET account_status = %s WHERE id = %s", ('Approved', user_id))
    connection.commit()

    cursor.close()
    connection.close()

    flash(f"Account with ID {user_id} has been approved.", "success")
    return redirect(url_for('admin_management'))  # Redirect to the admin dashboard or another page


@app.route('/reject_account', methods=['POST'])
def reject_account():
    user_id = request.form['user_id']
    message = request.form['message']

    # Debug: Log the user_id and message being passed
    app.logger.debug(f"Rejecting account with user_id: {user_id} and message: {message}")

    # Fetch the email of the user being rejected
    connection = create_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT email FROM accounts WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if user:
        # Since user is a tuple, access the email with index 0
        email = user[0]
        
        # Debug: Log the fetched email
        app.logger.debug(f"Fetched email for user_id {user_id}: {email}")
        
        try:
            # Sending rejection email
            msg = Message("Account Rejection Notice",
                          recipients=[email])
            msg.body = f"Your account has been rejected. Reason: {message}"

            # Debug: Log before sending email
            app.logger.debug(f"Attempting to send rejection email to {email}")
            mail.send(msg)
            app.logger.info(f"Rejection email sent to {email}")
        except Exception as e:
            app.logger.error(f"Error sending rejection email: {str(e)}")
            flash(f"Failed to send rejection email: {str(e)}", "error")

        # Update account status to 'Rejected'
        cursor.execute("UPDATE accounts SET account_status = 'Rejected' WHERE id = %s", (user_id,))
        connection.commit()

        # Debug: Log after account status update
        app.logger.debug(f"Account status for user_id {user_id} updated to 'Rejected'")
        
        flash(f"Account with email {email} has been rejected. Message: {message}", "success")
    else:
        # Debug: Log if user not found
        app.logger.warning(f"No account found for user_id {user_id}")

    cursor.close()
    connection.close()

    return redirect(url_for('admin_management'))  # Redirect back to the admin management page

    


@app.route('/notifications', methods=['GET'])
def get_notifications():
    connection = create_connection()
    if not connection:
        return jsonify([])

    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT id, message, status, created_at
        FROM notifications WHERE notification_type = 'seller_approval'
        ORDER BY created_at DESC
    """
    cursor.execute(query)
    notifications = cursor.fetchall()
    cursor.close()
    connection.close()

    return jsonify(notifications)

@app.route('/seller_notifications', methods=['GET'])
def seller_notifications():
    connection = create_connection()
    if not connection:
        return jsonify([])

    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT id, message, status, created_at
        FROM notifications WHERE notification_type = 'order_cancellation'
        ORDER BY created_at DESC
    """
    cursor.execute(query)
    notifications = cursor.fetchall()
    cursor.close()
    connection.close()

    return jsonify(notifications)

@app.route('/buyer_notifications', methods=['GET'])
def buyer_notifications():
    connection = create_connection()
    if not connection:
        return jsonify([])

    # Get the user_id from the session
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401  # Return error if user is not logged in

    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT id, message, status, created_at
        FROM notifications
        WHERE user_id = %s AND notification_type = 'seller_order_cancellation'
        ORDER BY created_at DESC
    """
    cursor.execute(query, (user_id,))
    notifications = cursor.fetchall()
    cursor.close()
    connection.close()

    return jsonify(notifications)


@app.route('/notifications/mark_as_read/<int:notification_id>', methods=['POST'])
def mark_notification_as_read(notification_id):
    connection = create_connection()
    if not connection:
        return '', 500

    cursor = connection.cursor()
    # Update the notification status to 'read'
    query = """
        UPDATE notifications
        SET status = 'read'
        WHERE id = %s AND status = 'unread'
    """
    cursor.execute(query, (notification_id,))
    connection.commit()
    cursor.close()
    connection.close()

    # Redirect to the admin management page after marking as read
    return redirect(url_for('admin_management'))

@app.route('/get_valid_id_image/<int:user_id>', methods=['GET'])
def get_valid_id_image(user_id):
    try:
        # Connect to the database
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Fetch the valid_id image URL for the given user
        cursor.execute("SELECT valid_id FROM accounts WHERE id = %s", (user_id,))
        result = cursor.fetchone()

        cursor.close()
        cnx.close()

        if result:
            # Return the image URL in the response
            return jsonify({'image_url': url_for('static', filename='uploads/profile_pics/' + result[0])})
        else:
            return jsonify({'image_url': ''}), 404  # If no valid ID image is found
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def login_required(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        if user_id:
            cursor.execute("SELECT status, ban_reason FROM accounts WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user and user['status'] == 'banned':
                session.clear()
                flash("Your account has been banned. Contact support for assistance.", "error")
                return redirect(url_for('home'))

        return view_function(*args, **kwargs)
    return wrapper

# Route to get messages from the database (Using MySQL Connector)
@app.route('/get_messages', methods=['GET'])
def get_messages():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10')
        messages = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(messages)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to send a message (Using MySQL Connector)
@app.route('/send_message', methods=['POST'])
def send_message():
    user = request.form['user']
    message = request.form['message']
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute('INSERT INTO messages (user, message) VALUES (%s, %s)', (user, message))
        connection.commit()
        cursor.close()
        connection.close()
        return '', 204  # No content, but indicates successful request
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_buyers', methods=['GET'])
def get_buyers():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, firstname, lastname, profile_picture FROM accounts WHERE role = 'Buyer'")
        buyers = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(buyers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_sellers', methods=['GET'])
def get_sellers():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, firstname, lastname FROM accounts WHERE role = 'Seller'")
        sellers = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(sellers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/send_private_message', methods=['POST'])
def send_private_message():
    sender_id = session.get('user_id')  # Get the logged-in user's ID
    receiver_id = request.form['receiver_id']  # Get the selected receiver's ID
    message = request.form['message']
    
    if not sender_id:
        return jsonify({'error': 'User not logged in'}), 401  # Unauthorized if no session
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)", 
                       (sender_id, receiver_id, message))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/get_private_messages', methods=['GET'])
def get_private_messages():
    sender_id = session.get('user_id')  # Get logged-in user ID
    receiver_id = request.args.get('receiver_id')
    
    if not sender_id:
        return jsonify({'error': 'User not logged in'}), 401  # Unauthorized if no session
    
    try:
        # Open MySQL connection
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Execute query to fetch the messages between the sender and receiver, including sender's name
        cursor.execute("""
            SELECT m.*, 
                   a.firstname AS sender_firstname, 
                   a.lastname AS sender_lastname, 
                   a.profile_picture AS sender_profile_picture
            FROM messages m
            JOIN accounts a ON m.sender_id = a.id
            WHERE (m.sender_id = %s AND m.receiver_id = %s) 
               OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.timestamp ASC
        """, (sender_id, receiver_id, receiver_id, sender_id))
        
        # Fetch messages from the database
        messages = cursor.fetchall()
        
        # Add sender's name to each message (already added via the JOIN)
        for message in messages:
            message['sender_name'] = f"{message['sender_firstname']} {message['sender_lastname']}"

        # Close cursor and connection
        cursor.close()
        connection.close()

        # Return messages as JSON
        return jsonify(messages)

    except Exception as e:
        # Return an error if something went wrong
        return jsonify({'error': str(e)}), 500
    
@app.route('/get_logged_in_user_id', methods=['GET'])
def get_logged_in_user_id():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401
    return jsonify({'user_id': user_id})

@app.route('/admin_ban', methods=['GET', 'POST'])
def admin_ban():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        if request.method == 'POST':
            user_id = request.form.get('user_id')
            action = request.form.get('action')

            if action == "ban":
                ban_reason = request.form.get('ban_reason')
                if ban_reason == "Other":
                    ban_reason = request.form.get('specific_ban_reason')
                
                # Temporary ban duration: 1 minute
                temp_ban_duration = 1  # Duration in minutes
                temp_ban_until = datetime.now() + timedelta(minutes=temp_ban_duration)

                # Increment ban count, set status to temporary_ban
                cursor.execute("""
                    UPDATE accounts 
                    SET status = 'temporary_ban', banned_at = NOW(), ban_reason = %s, ban_count = IFNULL(ban_count, 0) + 1,
                        temp_ban_until = %s
                    WHERE id = %s
                """, (ban_reason, temp_ban_until, user_id))

                # Check if user exceeds ban threshold
                cursor.execute("SELECT ban_count FROM accounts WHERE id = %s", (user_id,))
                ban_count = cursor.fetchone()[0]
                if ban_count >= 3:  # Archive after 3 bans
                    # Archive user
                    cursor.execute("""
                        INSERT INTO archive_users (original_id, firstname, middlename, lastname, birthdate, sex, email, password, role, profile_picture, ban_reason, street, city, province, region, barangay, valid_id, account_status, created_at, status, otp, shop_name) 
                        SELECT id, firstname, middlename, lastname, birthdate, sex, email, password, role, profile_picture, ban_reason, street, city, province, region, barangay, valid_id, account_status, created_at, status, otp, shop_name 
                        FROM accounts WHERE id = %s
                    """, (user_id,))
                    # Delete from accounts
                    cursor.execute("DELETE FROM accounts WHERE id = %s", (user_id,))
                    flash("User archived due to repeated bans.", "warning")
                else:
                    flash("User temporarily banned successfully!", "success")

            elif action == "unban":
                cursor.execute("""
                    UPDATE accounts 
                    SET status = 'Offline', banned_at = NULL, ban_reason = NULL, temp_ban_until = NULL
                    WHERE id = %s
                """, (user_id,))
                flash("User unbanned successfully!", "success")

        # Commit changes
        connection.commit()

        # Fetch active users
        cursor.execute("""
            SELECT 
                profile_picture, 
                CONCAT(firstname, ' ', lastname) AS name, 
                banned_at, 
                status, 
                role, 
                id 
            FROM accounts
        """)
        users = cursor.fetchall()

        # Fetch archived users
        cursor.execute("""
            SELECT 
                profile_picture, 
                CONCAT(firstname, ' ', lastname) AS name, 
                role, 
                archived_at, 
                id, ban_reason, status
            FROM archive_users
        """)
        archived_users = cursor.fetchall()

    except Exception as e:
        print("Error: ", e)
        flash("An error occurred: " + str(e), "danger")
        users = []
        archived_users = []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return render_template('Admin_ban.html', users=users, archived_users=archived_users)

@app.route('/permanent_ban', methods=['GET', 'POST'])
def permanent_ban():
    try:
        connection = create_connection()
        cursor = connection.cursor()

        if request.method == 'POST':
            user_id = request.form.get('user_id')
            if user_id:
                cursor.execute("""
                    UPDATE archive_users 
                    SET status = 'permanent_ban', banned_at = NOW()
                    WHERE id = %s
                """, (user_id,))
                
        print("User ID:", user_id)
        connection.commit()

    except Exception as e:
        print("Error: ", e)
        flash("An error occurred: " + str(e), "danger")
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for('admin_ban'))


## Mobile API
#mobile register
@app.route('/api/register', methods=['POST'])
def api_register():
    """
    Mobile API: create a buyer account, send OTP, return user_id.
    Mirrors the web /register logic but sets role="Buyer" by default.
    Expects multipart/form-data with the same fields + files as before.
    """
    # 1) Extract form fields
    f = request.form
    firstname   = f.get('firstname', '').strip()
    middlename  = f.get('middlename', '').strip()
    lastname    = f.get('lastname', '').strip()
    birthdate   = f.get('birthdate', '').strip()
    sex         = f.get('sex', '').strip()
    housenumber = f.get('housenumber', '').strip()
    street      = f.get('street', '').strip()
    city        = f.get('municipality', '').strip()  # maps to city
    province    = f.get('province', '').strip()
    region      = f.get('region', '').strip()
    barangay    = f.get('barangay', '').strip()
    email       = f.get('email', '').strip()
    password    = f.get('password', '').strip()

    # 2) Validate required fields
    if not (firstname and lastname and email and password):
        return jsonify({'message': 'firstname, lastname, email & password required'}), 400

    # 3) Handle file uploads
    profile_file = request.files.get('profile_picture')
    if profile_file:
        pic_name = secure_filename(profile_file.filename)
        profile_file.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
    else:
        pic_name = None

    valid_id_file = request.files.get('valid_id')
    if valid_id_file:
        id_name = secure_filename(valid_id_file.filename)
        valid_id_file.save(os.path.join(app.config['UPLOAD_FOLDER'], id_name))
    else:
        id_name = None

    # 4) Generate OTP and set account_status = 'pending'
    otp = generate_otp()
    account_status = 'pending'
    role = 'Buyer'   # default role
    status = 'Offline'

    # 5) Compose raw INSERT including role
    sql_insert = """
        INSERT INTO accounts (
            firstname, middlename, lastname, birthdate, sex,
            housenumber, street, city, province, region, barangay,
            email, password, role, status, profile_picture, valid_id, otp, account_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = (
        firstname, middlename, lastname, birthdate, sex,
        housenumber, street, city, province, region, barangay,
        email, password, role, status, pic_name, id_name, otp, account_status
    )

    conn = create_connection()
    if not conn:
        return jsonify({'message': 'Database connection failed'}), 500

    try:
        cur = conn.cursor()
        cur.execute(sql_insert, data)
        conn.commit()

        user_id = cur.lastrowid

        # 6) Insert a notification for the new user
        notif_sql = """
            INSERT INTO notifications (user_id, notification_type, message, status)
            VALUES (%s, %s, %s, %s)
        """
        notif_data = (
            user_id,
            'Account Created',
            'Please verify your account via OTP.',
            'unread'
        )
        cur.execute(notif_sql, notif_data)
        conn.commit()

        # 7) Send OTP email
        send_otp_email(email, otp)

        return jsonify({
            'message': 'Account created, OTP sent to email.',
            'user_id': user_id
        }), 201

    except Exception as e:
        conn.rollback()
        app.logger.error(f"[api_register] Error inserting account: {e}", exc_info=True)
        return jsonify({'message': 'Registration failed'}), 500

    finally:
        cur.close()
        conn.close()


#mobile verify otp
@app.route('/api/verify_otp', methods=['POST'])
def api_verify_otp():
    """
    Mobile API: verify the 6-digit OTP and activate the account.
    """
    data = request.get_json() or {}
    user_id = data.get('user_id')
    otp     = data.get('otp')

    if not user_id or not otp:
        return jsonify({'message': 'user_id and otp are required'}), 400

    account = Account.query.get(user_id)
    if not account:
        return jsonify({'message': 'Account not found'}), 404

    if account.otp == int(otp):
        account.account_status = 'Approved'
        account.otp    = None
        db.session.commit()
        return jsonify({'message': 'Account verified'}), 200
    else:
        return jsonify({'message': 'Invalid OTP'}), 401


# mobile log in

from werkzeug.exceptions import BadRequest

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True)
    if not data:
        raise BadRequest("Invalid JSON payload")

    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    if not email or not password:
        return jsonify(success=False, error="Email and password required"), 400

    conn = create_connection()
    if not conn:
        return jsonify(success=False, error="Database connection failed"), 500

    cur = conn.cursor(dictionary=True)
    try:
        # 1) Archived users
        cur.execute(
            "SELECT status, firstname, lastname, ban_reason "
            "FROM archive_users WHERE email=%s",
            (email,)
        )
        arch = cur.fetchone()
        if arch:
            name = f"{arch['firstname']} {arch['lastname']}".strip()
            reason = arch.get('ban_reason') or "Account banned."
            if arch['status'] == 'permanent_ban':
                return jsonify(
                    success=False,
                    banned=True,
                    permanent_ban=True,
                    ban_reason=reason,
                    user_name=name
                ), 403
            else:
                return jsonify(
                    success=False,
                    banned=True,
                    permanent_ban=False,
                    ban_reason=reason,
                    user_name=name
                ), 403

        # 2) Regular accounts
        cur.execute("SELECT * FROM accounts WHERE email=%s", (email,))
        user = cur.fetchone()
        if not user:
            return jsonify(success=False, error="No account with that email"), 404

        # 2a) Temporary ban?
        if user['status'] == 'temporary_ban':
            tbu = user.get('temp_ban_until')
            if isinstance(tbu, str):
                try:
                    tbu = datetime.fromisoformat(tbu)
                except ValueError:
                    tbu = None
            if tbu and datetime.now() > tbu:
                # lift the ban
                cur.execute(
                    "UPDATE accounts SET status='Offline', temp_ban_until=NULL, ban_reason=NULL WHERE id=%s",
                    (user['id'],)
                )
                conn.commit()
                user['status'] = 'Offline'
            else:
                remaining = (tbu - datetime.now()).total_seconds() if tbu else None
                return jsonify(
                    success=False,
                    banned=True,
                    permanent_ban=False,
                    ban_reason=user.get('ban_reason', "Temporarily banned."),
                    remaining_seconds=int(remaining or 0),
                    user_name=f"{user.get('firstname','')} {user.get('lastname','')}".strip()
                ), 403

        # 2b) Account approval status
        acct_stat = user.get('account_status', '').lower()
        if acct_stat == 'rejected':
            return jsonify(success=False, error="Account rejected; contact support"), 403
        if acct_stat == 'pending':
            return jsonify(success=False, error="Account pending approval"), 403

        # 2c) Password check
        if user['password'] != password:
            return jsonify(success=False, error="Invalid credentials"), 401
        
        # 2d) Only allow Buyers to log in here
        if user.get('role') != 'Buyer':
            return jsonify(success=False, error="Only users with the role 'Buyer' can log in here"), 403

        # 3) Success: mark online and return minimal user info
        cur.execute("UPDATE accounts SET status='Online' WHERE id=%s", (user['id'],))
        conn.commit()

        return jsonify(
            success=True,
            user_id=user['id'],
            firstname=user.get('firstname'),
            lastname=user.get('lastname')
        ), 200

    finally:
        cur.close()
        conn.close()



# Example of a route that requires authentication (user must be logged in)

#Mobile logout
@app.route('/api/logout', methods=['POST'])
def api_logout():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'message': 'User ID is required'}), 400

    connection = create_connection()
    if not connection:
        return jsonify({'message': 'Database connection error'}), 500

    cursor = connection.cursor(dictionary=True)
    try:
        # Update status to "Offline" when the user logs out
        cursor.execute("UPDATE accounts SET status = 'Offline' WHERE id = %s", (user_id,))
        connection.commit()

        return jsonify({'message': 'User logged out successfully, status set to Offline'}), 200

    finally:
        cursor.close()
        connection.close()


#Home Fetch Products
@app.route('/api/products')
def get_products():
    products = Inventory.query.all()
    product_list = []
    for product in products:
        product_list.append({
            'id': product.id,
            'product_name': product.product_name,
            'price': product.price,
            'product_picture': product.product_picture,  # adjust if your model has a field for image
            'details': product.details
        })
    
    return jsonify(product_list)

#Categories product fetch
@app.route('/api/products/category/<string:category_name>')
def get_products_by_category(category_name):
    """
    Mobile API: fetch all products in a given category.
    """
    # make sure your Inventory model actually has a `category` column :contentReference[oaicite:4]{index=4}:contentReference[oaicite:5]{index=5}
    products = Inventory.query.filter_by(category=category_name).all()
    category_list = []
    for p in products:
        category_list.append({
            'id': p.id,
            'product_name': p.product_name,
            'price': float(p.price),
            'product_image_url': url_for(
                'serve_profile_pics',
                filename=p.product_picture or '',
                _external=True
            ),
            'details': p.details,
            'category': p.category
        })
    return jsonify(category_list), 200    

@app.route('/static/uploads/profile_pics/<filename>')
def serve_profile_pics(filename):
    return send_from_directory('static/uploads/profile_pics', filename)

#product details mobile
@app.route('/api/product/<int:product_id>', methods=['GET'])
def api_get_product_details(product_id):
    # 1) fetch the product or 404
    product = Inventory.query.get_or_404(product_id)

    # 2) fetch its seller
    seller = Account.query.get(product.seller_id)
    if not seller:
        abort(404, description="Seller not found")

    # 3) build URLs for images
    prod_img_url = url_for(
        'serve_profile_pics',
        filename=product.product_picture or '',
        _external=True
    )
    seller_img_url = url_for(
        'serve_profile_pics',
        filename=seller.profile_picture or '',
        _external=True
    )

    # 4) pull in all feedback rows for this product
    feedback_rows = (
        Feedback.query
        .filter_by(product_id=product.id)
        .order_by(Feedback.created_at.desc())
        .all()
    )
    feedbacks = []
    for fb in feedback_rows:
        # build photo URL if they uploaded one
        photo_url = None
        if fb.photo:
            photo_url = url_for(
                'serve_profile_pics',
                filename=fb.photo,
                _external=True
            )
        feedbacks.append({
            'id':        fb.id,
            'user_id':   fb.user_id,
            'role':      fb.role,
            'user_name': fb.user_name,
            'comment':   fb.comment,
            'rating':    fb.rating,
            'photo_url': photo_url,
            'created_at': fb.created_at.isoformat()
        })

    # 5) assemble the payload
    data = {
        'id':                            product.id,
        'product_name':                  product.product_name,
        'price':                         float(product.price),
        'details':                       product.details or '',
        'product_image_url':             prod_img_url,

        # seller info
        'seller_id':                     seller.id,
        'seller_name':                   f"{seller.firstname} {seller.lastname}",
        'seller_role':                   seller.role,
        'seller_status':                 str(seller.status),
        'seller_profile_picture_url':    seller_img_url,

        # feedback list
        'feedbacks':                     feedbacks,
    }

    return jsonify(data), 200

@app.route('/api/variations/<int:product_id>', methods=['GET'])
def get_variations(product_id):
    # Fetch the base product first
    product = Inventory.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    base_image = product.product_picture  # Product's base image

    # Fetch all variations for the product
    variations = ProductVariation.query.filter_by(product_id=product_id).all()
    
    variation_attributes = []
    for variation in variations:
        for attr in variation.attributes:
            variation_attributes.append({
                'id': attr.id,
                'attribute_name': attr.attribute_name,
                'attribute_value': attr.attribute_value,
                'attribute_price': attr.attribute_price,
                'attribute_stock': attr.attribute_stock,
                'attribute_image': base_image   # <-- Always use base image
            })

    return jsonify(variation_attributes)

#mobile add to cart
@app.route('/api/add_to_cart', methods=['POST'])
def add_to_cart_mobile():
    data = request.get_json()

    user_id = data.get('user_id')
    product_id = data.get('product_id')
    variation_id = data.get('variation_id')
    quantity = data.get('quantity')

    if not user_id or not product_id or not variation_id or quantity is None:
        return jsonify({'message': 'User ID, Product ID, Variation ID, and Quantity are required'}), 400

    if quantity <= 0:
        return jsonify({'message': 'Quantity must be greater than 0'}), 400

    # Step 1: Check if the variation exists and has enough stock
    variation = VariationAttribute.query.filter_by(id=variation_id).first()
    
    if not variation:
        return jsonify({'message': 'Variation not found or invalid variation ID'}), 404

    if variation.attribute_stock < quantity:
        return jsonify({'message': 'Not enough stock available for this variation'}), 400

    # Step 2: Ensure the product exists in the inventory
    product = Inventory.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    # Step 3: Get or create the user's cart
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        # Create a new cart if it doesn't exist
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    # Step 4: Check if the product with the selected variation is already in the cart
    existing_item = CartItem.query.filter_by(cart_id=cart.id, inventory_id=product_id, variation_attribute_id=variation_id).first()

    if existing_item:
        # Step 5: Check if adding the quantity exceeds the available stock
        new_quantity = existing_item.quantity + quantity
        if new_quantity > variation.attribute_stock:
            return jsonify({'message': 'Not enough stock available for this quantity'}), 400
        # Update the existing item's quantity
        existing_item.update_quantity(new_quantity)
    else:
        # Step 6: Add the new product to the cart with variation details
        cart_item = CartItem(
            cart_id=cart.id,
            inventory_id=product_id,
            quantity=quantity,
            variation_name=variation.attribute_name,
            variation_value=variation.attribute_value,
            price=product.price + variation.attribute_price,
            stock=variation.attribute_stock,
            variation_attribute_id=variation_id
        )
        db.session.add(cart_item)

    # Step 7: Update cart total items and price
    db.session.commit()

    # Recalculate the total items and total price
    total_items = sum(item.quantity for item in cart.items)
    total_price = sum(item.calculate_item_total() for item in cart.items)

    cart.total_items = total_items
    cart.total_price = total_price

    db.session.commit()

    return jsonify({
        'message': 'Product added to cart successfully',
        'cart_total_items': total_items,
        'cart_total_price': str(total_price)
    }), 200

#mobile view cart
@app.route('/api/cart/<int:user_id>', methods=['GET'])
def get_cart_items(user_id):
    print(f"User ID from URL: {user_id}")

    # Fetch the user's cart
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404

    cart_data = []
    for item in cart.items:
        inventory = item.product  # assuming 'item.product' gets the inventory

        # Fetch the variation_id from the VariationAttribute table (variation_id is the id from VariationAttribute)
        variation = VariationAttribute.query.filter_by(
            attribute_name=item.variation_name,
            attribute_value=item.variation_value
        ).first()

        variation_id = variation.id if variation else None

        # Append cart data with variation_id, seller_id, etc.
        cart_data.append({
            'id': item.id,
            'product_name': inventory.product_name,
            'product_picture': inventory.product_picture,
            'price': float(item.price),
            'quantity': float(item.quantity),
            'variation_name': item.variation_name,
            'variation_value': item.variation_value,
            'stock': item.stock,
            'inventory_id': item.inventory_id,
            'selected': False,  # default for checkbox
            'seller_id': inventory.seller_id,  # Add the seller_id here
            'variation_id': variation_id  # Add variation_id here, which is the id from VariationAttribute
        })

    return jsonify(cart_data)

#check existing cart
@app.route('/api/cart/product_quantity')
def get_cart_quantity():
    user_id = request.args.get('user_id')
    product_id = request.args.get('product_id')
    variation_id = request.args.get('variation_id')
    
    item = Cart.query.filter_by(user_id=user_id, product_id=product_id, variation_id=variation_id).first()
    return jsonify(quantity=item.quantity if item else 0)


#mobile delete cart item
@app.route('/api/cart/item/<int:item_id>', methods=['DELETE'])
def delete_cart_item(item_id):
    item = CartItem.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        print('Failed to delete item, status code: ${response.statusCode}')
        print('Response body: ${response.body}')
        return jsonify({"message": "Item successfully deleted"}), 200
    else:
        return jsonify({"message": "Item not found"}), 404
    

#fetch address
@app.route('/get_address/<int:user_id>', methods=['GET'])
def get_address(user_id):
    conn = create_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute('SELECT region, province, city, barangay, street, housenumber FROM accounts WHERE id = %s', (user_id,))
    account = cur.fetchone()

    cur.close()
    conn.close()

    if account:
        # Format the address nicely
        address = f"{account['housenumber']} {account['street']}, {account['barangay']}, {account['city']}, {account['province']}, {account['region']}"
        return jsonify({'address': address})
    else:
        return jsonify({'error': 'User not found'}), 404
    
#mobile place order
@app.route('/place_order', methods=['POST'])
def place_order():
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload received"}), 400

        user_id = data.get('user_id')
        address = data.get('address')
        payment_method = data.get('payment_method')
        cart_items = data.get('cart_items')

        if not all([user_id, address, payment_method, cart_items]):
            return jsonify({"error": "Missing required fields"}), 400

        print("Cart items received:", cart_items)

        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in cart_items)

        # Create Order
        new_order = Order(
            user_id=user_id,
            address=address,
            payment_method=payment_method,
            total=total
        )
        db.session.add(new_order)
        db.session.flush()  # Get order ID before commit

        # Insert order items and update stock
        for item in cart_items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item['inventory_id'],
                product_name=item['product_name'],
                product_price=item['price'],
                quantity=item['quantity'],
                total=item['price'] * item['quantity'],
                status="Pending",
                variation_name=item.get('variation_name', ''),
                variation_value=item.get('variation_value', ''),
                product_image=item.get('product_picture', ''),
                seller_id=item.get('seller_id'),
                variation_id=item.get('variation_id'),
                cancellation_reason=None,
                date_received=None,
                tracking_number=generate_tracking_number()
            )
            db.session.add(order_item)

            # Reduce stock for inventory and variations
            print(f"Checking variation: {order_item.variation_id}, {order_item.variation_name}, {order_item.variation_value}")

            # Match variation_id, variation_name, and variation_value
            variation = VariationAttribute.query.filter_by(
                id=order_item.variation_id,  # Match with variation_id in VariationAttribute (primary key)
                attribute_name=order_item.variation_name,
                attribute_value=order_item.variation_value
            ).first()

            if variation:
                print(f"Found variation: {variation.attribute_name} = {variation.attribute_value}")
                
                # Ensure enough stock is available
                if variation.attribute_stock >= order_item.quantity:
                    variation.attribute_stock -= order_item.quantity
                    db.session.add(variation)
                else:
                    print(f"Error: Insufficient stock for variation {variation.attribute_name}.")
                    db.session.rollback()
                    return jsonify({"error": f"Insufficient stock for variation {variation.attribute_name}."}), 400
            else:
                print("Error: Variation not found.")
                db.session.rollback()
                return jsonify({"error": "Variation not found."}), 400

            # Update the product's total stock based on variations
            inventory_item = Inventory.query.get(order_item.product_id)
            if inventory_item:
                total_variation_stock = db.session.query(
                    db.func.sum(VariationAttribute.attribute_stock)
                ).join(ProductVariation, ProductVariation.id == VariationAttribute.variation_id) \
                .filter(ProductVariation.product_id == inventory_item.id) \
                .scalar()

                inventory_item.quantity = total_variation_stock if total_variation_stock is not None else 0
                db.session.add(inventory_item)
            else:
                print(f"Error: Inventory item not found for product ID {order_item.product_id}.")
                db.session.rollback()
                return jsonify({"error": f"Inventory item not found for product ID {order_item.product_id}."}), 400

            # Remove the item from the Cart table after placing the order
            cart = Cart.query.filter_by(user_id=user_id).first()
            if cart:
                cart_item = next((ci for ci in cart.items if ci.id == item['id']), None)
                if cart_item:
                    db.session.delete(cart_item)

        # Commit changes
        db.session.commit()

        # Return success response with redirect suggestion for Flutter screen
        return jsonify({"message": "Order placed successfully", "order_id": new_order.id, "redirect": "home_screen.dart"}), 200

    except Exception as e:
        db.session.rollback()
        print("Error placing order:", str(e))  # Optional for debugging
        return jsonify({"error": str(e)}), 500

#mobile orders fetch

@app.route('/api/orders/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    """
    Mobile API: fetch all orders (and their items) for a given user.
    """
    
    # Eager-load the Order.items relationship
    orders = (
        Order.query
             .filter_by(user_id=user_id)
             .options(db.joinedload(Order.items))
             .all()
    )

    # Serialize to JSON
    orders_data = []
    for order in orders:
        items_data = []
        for item in order.items:
            items_data.append({
                'id': item.id,
                'order_id': item.order_id,
                'product_id': item.product_id,
                'product_name': item.product_name,
                'product_price': float(item.product_price),
                'quantity': item.quantity,
                'total': float(item.total),
                'status': item.status,
                'variation_name': item.variation_name,
                'variation_value': item.variation_value,
                'product_image_url': url_for(
                    'static',
                    filename=f'uploads/profile_pics/{item.product_image}',
                    _external=True
                ),
                'seller_id': item.seller_id,
                'variation_id': item.variation_id,
                'cancellation_reason': item.cancellation_reason,
                'tracking_number': item.tracking_number,
                'date_received': item.date_received.isoformat() if item.date_received else None,
                'proof_image': url_for('static', filename=f'proof_images/{item.proof_image}', _external=True) if item.proof_image else None
            })

        orders_data.append({
            'id': order.id,
            'user_id': order.user_id,
            'address': order.address,
            'payment_method': order.payment_method,
            'total': float(order.total),
            'created_at': order.created_at.isoformat(),
            'items': items_data
        })

    return jsonify(orders_data), 200

#mobile cancel order
@app.route('/api/cancel_order/<int:order_id>', methods=['POST'])
def api_cancel_order(order_id):
    data = request.get_json() or {}
    # first try Flask session, then JSON payload
    user_id = session.get('user_id') or data.get('user_id')
    cancellation_reason = data.get('cancellation_reason')

    if not user_id:
        return jsonify({"success": False, "message": "User ID is required"}), 400
    if not cancellation_reason:
        return jsonify({"success": False, "message": "Cancellation reason is required"}), 400

    user = Account.query.get(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    # find the order‐item and ensure it's cancellable
    allowed = ['pending', 'Confirmed']
    oi = OrderItem.query.filter_by(id=order_id).filter(OrderItem.status.in_(allowed)).first()
    if not oi:
        return jsonify({"success": False, "message": "No eligible order to cancel"}), 400

    oi.status = 'Cancelled'
    oi.cancellation_reason = cancellation_reason
    db.session.commit()

    # optional: send notification etc.
    return jsonify({"success": True, "message": "Order cancelled"}), 200


@app.route('/api/mark_order_received/<int:order_item_id>', methods=['POST'])
def mark_order_received_mobile(order_item_id):
    """
    Mobile API: mark a delivered order item as received.
    Only items currently in 'Delivered' or 'Out for Delivery' can be marked.
    """
    try:
        # Only allow transitioning from delivered states
        allowed = ['Delivered', 'Out for Delivery']
        item = OrderItem.query.filter_by(id=order_item_id)\
                              .filter(OrderItem.status.in_(allowed))\
                              .first()

        if item:
            item.status = 'Received'
            item.date_received = datetime.utcnow()

            # ---- INSERT RIDER COMMISSION HERE ----
            product_total = float(item.product_price) * int(item.quantity)
            # Get shipping_fee safely (default to 0 if missing)
            shipping_fee = float(getattr(item, 'shipping_fee', 0))
            commission_amount = 0.10 * (product_total + shipping_fee)

            # Only insert if not already inserted (prevent duplicates)
            already = RiderCommission.query.filter_by(order_item_id=item.id).first()
            if not already:
                new_comm = RiderCommission(
                    rider_id = item.rider_id,
                    order_item_id = item.id,
                    commission_amount = commission_amount
                )
                db.session.add(new_comm)

            db.session.commit()
            return jsonify({'success': True, 'message': 'Order marked as received!'})

        return jsonify({
            'success': False,
            'message': 'Order cannot be marked as received (invalid status).'
        }), 400

    except Exception as e:
        app.logger.error(f"[mark_order_received] {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Error marking the order as received.'
        }), 500



@app.route('/api/confirm_order/<int:order_item_id>', methods=['POST'])
def mark_order_confirmed_mobile(order_item_id):

    try:
        # Only allow transitioning from delivered states
        allowed = ['Pending']
        item = OrderItem.query.filter_by(id=order_item_id)\
                              .filter(OrderItem.status.in_(allowed))\
                              .first()

        if item:
            item.status = 'Confirmed'
            item.date_received = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True, 'message': 'Order Confirmed!'})

        return jsonify({
            'success': False,
            'message': 'Order cannot be Confirmed (invalid status).'
        }), 400

    except Exception as e:
        app.logger.error(f"[mark_order_received] {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Error marking the order as received.'
        }), 500
    
@app.route('/api/submit_feedback/<int:item_id>', methods=['POST'])
def api_submit_feedback(item_id):
    print(f"[Feedback DEBUG] Received feedback POST for item_id={item_id}")

    # 1) Validate order item exists and status == 'Received'
    order_item = OrderItem.query.get(item_id)
    if not order_item or order_item.status != 'Received':
        return jsonify(success=False, message="Order not found or not in 'Received' status."), 404

    # 2) Pull required form fields
    comment = request.form.get('comment', '').strip()
    rating = request.form.get('rating', '').strip()
    user_id = request.form.get('user_id', '').strip()

    print(f"[Feedback DEBUG] user_id={user_id!r}, comment={comment!r}, rating={rating!r}")

    if not comment or not rating or not user_id:
        return jsonify(success=False, message="Missing comment, rating, or user_id."), 400

    # 3) Optional photo upload
    photo_file = request.files.get('photo')
    filename = None
    if photo_file:
        print(f"[Feedback DEBUG] photo file provided: filename={photo_file.filename!r}")
        if not allowed_file(photo_file.filename):
            return jsonify(success=False, message="Invalid image type."), 400
        filename = secure_filename(photo_file.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo_file.save(photo_path)
        print(f"[Feedback DEBUG] photo saved to: {photo_path}")

    # 4) Lookup user to get role & name
    try:
        user = Account.query.get(int(user_id))
        if not user:
            return jsonify(success=False, message="User not found."), 404
        user_name = f"{user.firstname} {user.middlename or ''} {user.lastname}".strip()
    except ValueError:
        return jsonify(success=False, message="Invalid user_id."), 400

    # 5) Insert Feedback row (now includes tracking_number)
    try:
        fb = Feedback(
            product_id=order_item.product_id,
            user_id=int(user_id),
            role=user.role,
            user_name=user_name,
            comment=comment,
            rating=int(rating),
            photo=filename,
            tracking_number=order_item.tracking_number  # ✅ required field
        )
        db.session.add(fb)
        db.session.commit()
        return jsonify(success=True, message="Feedback submitted successfully."), 200

    except Exception as e:
        db.session.rollback()
        print(f"[Feedback DEBUG] DB error on feedback commit: {e}")
        print(f"[DEBUG] Feedback model has: {Feedback.__table__.columns.keys()}")

        return jsonify(success=False, message=f"Database error: {str(e)}"), 500


@app.route('/api/has_feedback/<int:item_id>', methods=['GET'])
def api_has_feedback(item_id):
    """
    Mobile API: has this user already left feedback
    for the given tracking_number?
    Query params: user_id
    """
    order_item = OrderItem.query.get(item_id)
    if not order_item:
        return jsonify(has_feedback=False), 404

    # client must pass ?user_id=<int>
    try:
        uid = int(request.args.get('user_id', ''))
    except (TypeError, ValueError):
        return jsonify(has_feedback=False), 400

    # look up a feedback row matching this user & tracking number
    exists = Feedback.query.filter_by(
        tracking_number=order_item.tracking_number,
        user_id=uid
    ).first()

    return jsonify(has_feedback=exists is not None), 200
#profile mobile
@app.route('/api/profile/<int:user_id>', methods=['GET'])
def api_get_profile(user_id):
    """
    Mobile API: fetch a buyer’s profile by their user_id.
    """
    user = Account.query.get_or_404(user_id)  # your Account model :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
    return jsonify({
        'id': user.id,
        'firstname': user.firstname,
        'middlename': user.middlename,
        'lastname': user.lastname,
        'birthdate': user.birthdate,
        'sex': user.sex,
        'address': user.address,
        'housenumber': user.housenumber,
        'street': user.street,
        'barangay': user.barangay,
        'city': user.city,
        'province': user.province,
        'region': user.region,
        'email': user.email,
        'role': user.role,
        'profile_picture_url': url_for(
            'serve_profile_pics',
            filename=user.profile_picture or '',
            _external=True
        )
    }), 200





















#courier mobile

@app.route('/api/courier_register', methods=['POST'])
def api_courier_register():

    # 1) Extract form fields
    f = request.form
    firstname   = f.get('firstname', '').strip()
    middlename  = f.get('middlename', '').strip()
    lastname    = f.get('lastname', '').strip()
    birthdate   = f.get('birthdate', '').strip()
    sex         = f.get('sex', '').strip()
    housenumber = f.get('housenumber', '').strip()
    street      = f.get('street', '').strip()
    city        = f.get('municipality', '').strip()  # maps to city
    province    = f.get('province', '').strip()
    region      = f.get('region', '').strip()
    barangay    = f.get('barangay', '').strip()
    email       = f.get('email', '').strip()
    password    = f.get('password', '').strip()

    # 2) Validate required fields
    if not (firstname and lastname and email and password):
        return jsonify({'message': 'firstname, lastname, email & password required'}), 400

    # 3) Handle file uploads
    profile_file = request.files.get('profile_picture')
    if profile_file:
        pic_name = secure_filename(profile_file.filename)
        profile_file.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
    else:
        pic_name = None

    valid_id_file = request.files.get('valid_id')
    if valid_id_file:
        id_name = secure_filename(valid_id_file.filename)
        valid_id_file.save(os.path.join(app.config['UPLOAD_FOLDER'], id_name))
    else:
        id_name = None

    # 4) Generate OTP and set account_status = 'pending'
    otp = generate_otp()
    account_status = 'pending'
    role = 'Rider'   # default role
    status = 'Offline'

    # 5) Compose raw INSERT including role
    sql_insert = """
        INSERT INTO accounts (
            firstname, middlename, lastname, birthdate, sex,
            housenumber, street, city, province, region, barangay,
            email, password, role, status, profile_picture, valid_id, otp, account_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = (
        firstname, middlename, lastname, birthdate, sex,
        housenumber, street, city, province, region, barangay,
        email, password, role, status, pic_name, id_name, otp, account_status
    )

    conn = create_connection()
    if not conn:
        return jsonify({'message': 'Database connection failed'}), 500

    try:
        cur = conn.cursor()
        cur.execute(sql_insert, data)
        conn.commit()

        user_id = cur.lastrowid

        # 6) Insert a notification for the new user
        notif_sql = """
            INSERT INTO notifications (user_id, notification_type, message, status)
            VALUES (%s, %s, %s, %s)
        """
        notif_data = (
            user_id,
            'Account Created',
            'Please verify your account via OTP.',
            'unread'
        )
        cur.execute(notif_sql, notif_data)
        conn.commit()

        # 7) Send OTP email
        send_otp_email(email, otp)

        return jsonify({
            'message': 'Account created, OTP sent to email.',
            'user_id': user_id
        }), 201

    except Exception as e:
        conn.rollback()
        app.logger.error(f"[api_register] Error inserting account: {e}", exc_info=True)
        return jsonify({'message': 'Registration failed'}), 500

    finally:
        cur.close()
        conn.close()

@app.route('/api/courier_login', methods=['POST'])
def api_courier_login():
    data = request.get_json(silent=True)
    if not data:
        raise BadRequest("Invalid JSON payload")

    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    if not email or not password:
        return jsonify(success=False, error="Email and password required"), 400

    conn = create_connection()
    if not conn:
        return jsonify(success=False, error="Database connection failed"), 500

    cur = conn.cursor(dictionary=True)
    try:
        # 1) Archived users
        cur.execute(
            "SELECT status, firstname, lastname, ban_reason "
            "FROM archive_users WHERE email=%s",
            (email,)
        )
        arch = cur.fetchone()
        if arch:
            name = f"{arch['firstname']} {arch['lastname']}".strip()
            reason = arch.get('ban_reason') or "Account banned."
            if arch['status'] == 'permanent_ban':
                return jsonify(
                    success=False,
                    banned=True,
                    permanent_ban=True,
                    ban_reason=reason,
                    user_name=name
                ), 403
            else:
                return jsonify(
                    success=False,
                    banned=True,
                    permanent_ban=False,
                    ban_reason=reason,
                    user_name=name
                ), 403

        # 2) Regular accounts
        cur.execute("SELECT * FROM accounts WHERE email=%s", (email,))
        user = cur.fetchone()
        if not user:
            return jsonify(success=False, error="No account with that email"), 404

        # 2a) Temporary ban?
        if user['status'] == 'temporary_ban':
            tbu = user.get('temp_ban_until')
            if isinstance(tbu, str):
                try:
                    tbu = datetime.fromisoformat(tbu)
                except ValueError:
                    tbu = None
            if tbu and datetime.now() > tbu:
                # lift the ban
                cur.execute(
                    "UPDATE accounts SET status='Offline', temp_ban_until=NULL, ban_reason=NULL WHERE id=%s",
                    (user['id'],)
                )
                conn.commit()
                user['status'] = 'Offline'
            else:
                remaining = (tbu - datetime.now()).total_seconds() if tbu else None
                return jsonify(
                    success=False,
                    banned=True,
                    permanent_ban=False,
                    ban_reason=user.get('ban_reason', "Temporarily banned."),
                    remaining_seconds=int(remaining or 0),
                    user_name=f"{user.get('firstname','')} {user.get('lastname','')}".strip()
                ), 403

        # 2b) Account approval status
        acct_stat = user.get('account_status', '').lower()
        if acct_stat == 'rejected':
            return jsonify(success=False, error="Account rejected; contact support"), 403
        if acct_stat == 'pending':
            return jsonify(success=False, error="Account pending approval"), 403

        # 2c) Password check
        if user['password'] != password:
            return jsonify(success=False, error="Invalid credentials"), 401
        
        # 2d) Only allow Buyers to log in here
        if user.get('role') != 'Rider':
            return jsonify(success=False, error="Only users with the role 'Buyer' can log in here"), 403

        # 3) Success: mark online and return minimal user info
        cur.execute("UPDATE accounts SET status='Online' WHERE id=%s", (user['id'],))
        conn.commit()

        return jsonify(
            success=True,
            user_id=user['id'],
            firstname=user.get('firstname'),
            lastname=user.get('lastname')
        ), 200

    finally:
        cur.close()
        conn.close()


@app.route('/api/assigned_orders', methods=['GET'])
def assigned_orders():
    rider_id = request.args.get('rider_id', type=int)
    if rider_id is None:
        return jsonify({'status':'error','message':'rider_id is required'}), 400

    # fetch all order_items assigned to this rider
    items = OrderItem.query.filter_by(rider_id=rider_id).all()

    orders_map = {}
    for i in items:
        o = i.order  # via relationship on OrderItem.order
        # get buyer account
        buyer = Account.query.get(o.user_id)
        buyer_name = f"{buyer.firstname} {buyer.lastname}" if buyer else ''

        seller = Account.query.get(i.seller_id)

        if o.id not in orders_map:
            orders_map[o.id] = {
                'id': o.id,
                'buyer_name': buyer_name,
                'address': o.address,
                'payment_method': o.payment_method,
                'total': float(o.total),
                'created_at': o.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'items': []
            }

        # append this item’s details
        orders_map[o.id]['items'].append({
            'id': i.id,
            'product_name': i.product_name,
            'product_image':      url_for(
                                        'static',
                                        filename=f'uploads/profile_pics/{i.product_image}',
                                      _external=True
                                    ),       # include product_image
            'variation_name': i.variation_name or '',
            'variation_value': i.variation_value or '',
            'quantity': i.quantity,
            'product_price': float(i.product_price),
            'total': float(i.total),
            'status': i.status,
            'tracking_number': i.tracking_number,
            'seller_firstname': seller.firstname if seller else '',
            'seller_middlename': seller.middlename if seller and seller.middlename else '',
            'seller_lastname': seller.lastname if seller else '',
            'proof_image': url_for('static', filename=f'proof_images/{i.proof_image}', _external=True) if i.proof_image else None

        })

    return jsonify({
        'status': 'success',
        'orders': list(orders_map.values())
    })

@app.route('/api/update_order_status', methods=['POST'])
def api_update_order_status():
    data = request.get_json()
    order_id = data.get('order_id')
    new_status = data.get('new_status')

    if not order_id or not new_status:
        return jsonify({'status': 'error', 'message': 'Missing order_id or new_status'}), 400

    items = OrderItem.query.filter_by(order_id=order_id).all()

    if not items:
        return jsonify({'status': 'error', 'message': 'No order items found'}), 404

    for item in items:
        item.status = new_status
        item.status_changed_at = datetime.utcnow()

    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/mark_delivered', methods=['POST'])
def mark_delivered():
    order_id = request.form.get('order_id')
    file = request.files.get('proof')

    if not order_id or not file:
        return jsonify({'status': 'error', 'message': 'Missing order_id or proof image'}), 400

    items = OrderItem.query.filter_by(order_id=order_id, status='Out for Delivery').all()

    if not items:
        return jsonify({'status': 'error', 'message': 'No eligible items found'}), 404

    # Save image
    filename = secure_filename(file.filename)
    timestamped_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, timestamped_filename)
    file.save(filepath)

    # Update all eligible items
    for item in items:
        item.status = 'Delivered'
        item.status_changed_at = datetime.utcnow()
        item.proof_image = timestamped_filename

    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Order marked as delivered'})

@app.route('/api/rider_commissions_summary')
def rider_commissions_summary():
    rider_id = request.args.get('rider_id', type=int)
    if not rider_id:
        return jsonify({'success': False, 'message': 'Missing rider_id'}), 400

    # Get today string
    today = date.today()

    # Query all commissions for this rider
    commissions = RiderCommission.query.filter_by(rider_id=rider_id).all()

    # Prepare daily summary
    daily_map = {}
    total_commission = 0.0
    today_commission = 0.0

    for comm in commissions:
        comm_date = comm.computed_at.date()
        amount = float(comm.commission_amount)
        dstr = comm_date.isoformat()
        daily_map.setdefault(dstr, 0.0)
        daily_map[dstr] += amount
        total_commission += amount
        if comm_date == today:
            today_commission += amount

    # Convert to sorted daily list (latest first)
    daily_list = [
        {'date': d, 'amount': daily_map[d]}
        for d in sorted(daily_map.keys(), reverse=True)
    ]

    return jsonify({
        'success': True,
        'total_commission': round(total_commission, 2),
        'today_commission': round(today_commission, 2),
        'daily_commissions': daily_list,
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

