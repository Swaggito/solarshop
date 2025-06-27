from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

class AnonymousUser(AnonymousUserMixin):
    def get_unread_notifications_count(self):
        return 0

    @property
    def notifications(self):
        class DummyQuery:
            def count(self):
                return 0
            def order_by(self, *args, **kwargs):
                return self
            def limit(self, *args, **kwargs):
                return []
        return DummyQuery()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.anonymous_user = AnonymousUser

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    admin_access_level = db.Column(db.Integer, default=0)  # 0: normal user, 1: admin, 2: super admin
    role = db.Column(db.String(20), default='user')  # Add this line
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_administrator(self):
        return self.is_admin and self.admin_access_level > 0 and self.role == 'admin'

    def is_buyer(self):
        return self.role == 'buyer'

    def get_unread_notifications_count(self):
        return AdminNotification.query.filter_by(user_id=self.id, read=False).count()

    @staticmethod
    def create_admin():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin',
                is_admin=True,
                admin_access_level=2
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            return "Admin user created with username: 'admin' and password: 'admin123'"
        return "Admin user already exists"

    def get_reset_token(self, expires_in=1800):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='password-reset-salt', max_age=1800)['user_id']
        except:
            return None
        return User.query.get(user_id)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    images = db.relationship('ProductImage', backref='product_parent', lazy=True, 
                           cascade='all, delete-orphan')  # Add cascade delete
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    
class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    products = db.relationship('Product', backref='brand', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255))  # Verify this line exists
    products = db.relationship('Product', backref='category', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))  # Add this line
    special_notes = db.Column(db.Text)  # Add this line
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_items = db.relationship('OrderItem', backref='order', lazy=True)
    user = db.relationship('User', backref='orders', lazy=True)
    checkout = db.relationship('Checkout', backref='order', lazy=True)  # Add this line
    payments = db.relationship('Payment', backref='parent_order', lazy=True)  # Changed from 'payment' to 'payments'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float, nullable=False)
    tracking_code = db.Column(db.String(20), unique=True)  # Add this line
    product = db.relationship('Product')

    def generate_tracking_code(self):
        import random
        import string
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            tracking_code = f"ORD-{self.order_id}-{code}"
            # Check if code already exists
            if not OrderItem.query.filter_by(tracking_code=tracking_code).first():
                return tracking_code

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only generate tracking code after we have an order_id
        db.session.flush()  # Ensure we have an order_id
        if not self.tracking_code:
            self.tracking_code = self.generate_tracking_code()

    def get_subtotal(self):
        return self.price * self.quantity

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    amount = db.Column(db.Float)
    method = db.Column(db.String(50))
    status = db.Column(db.String(50))
    card_last4 = db.Column(db.String(4))  # Add this line
    cardholder_name = db.Column(db.String(100))  # Add this line
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Removed the conflicting relationship line

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    site_url = db.Column(db.String(200))
    contact_email = db.Column(db.String(120))
    sales_email = db.Column(db.String(120))
    support_email = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    smtp_server = db.Column(db.String(100))
    smtp_port = db.Column(db.Integer)
    smtp_username = db.Column(db.String(100))
    smtp_password = db.Column(db.String(100))
    smtp_use_tls = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# app/models.py

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ProductImage {self.id} for Product {self.product_id}>'
    def __init__(self, product_id, image):
        self.product_id = product_id
        self.image = image
        self.created_at = datetime.utcnow()

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product')

    def get_subtotal(self):
        if self.product:
            return self.product.price * self.quantity
        else:
            return 0.0  # Or some other appropriate default

class Checkout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)
    shipping_address = db.Column(db.String(500), nullable=False)
    billing_address = db.Column(db.String(500), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    order_notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdminNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(50), default='general')  # Add this line
    
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic', cascade='all, delete-orphan'))
    order = db.relationship('Order')