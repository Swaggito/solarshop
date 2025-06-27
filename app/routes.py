from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, jsonify
from app import db, create_app
from app.models import (
    User, Product, Brand, Category, Order, OrderItem, 
    Payment, Settings, Cart, CartItem, ProductImage, Checkout, AdminNotification
)
from app.forms import (
    LoginForm, RegistrationForm, ProductForm, BrandForm, 
    CategoryForm, SettingsForm, EditUserForm, CheckoutForm, UserSettingsForm
)
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
# app/routes.py
from app.models import ProductImage
from flask import Blueprint
from app.forms import ProductForm, BrandForm, CategoryForm, SettingsForm
from app.models import Product, Brand, Category, User, Order, Settings
import os
from functools import wraps
from datetime import datetime

bp = Blueprint('main', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_administrator():
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('main.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def send_admin_notification(order, checkout):
    try:
        admin_users = User.query.filter_by(is_admin=True).all()
        for admin in admin_users:
            notification = AdminNotification(
                user_id=admin.id,
                order_id=order.id,
                message=f"New order #{order.id} received from {checkout.contact_email}",
                read=False
            )
            db.session.add(notification)
        db.session.flush()
    except Exception as e:
        print(f"Error sending admin notification: {str(e)}")
        db.session.rollback()
        raise

@bp.route('/')
@bp.route('/home')
def home():
    products = Product.query.all()
    categories = Category.query.all()  # Add this line
    return render_template('home.html', products=products, categories=categories)  # Update this line

@bp.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    related_products = Product.query.filter_by(brand_id=product.brand_id).filter(Product.id != id).limit(4).all()
    return render_template('product.html', product=product, related_products=related_products)

@bp.route('/contact')
def contact():
    return render_template('contact.html')

@bp.route('/about')
def about():
    return render_template('about.html')

# Admin Routes
@bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_administrator():
        return redirect(url_for('main.admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.is_administrator():
            login_user(user)
            return redirect(url_for('main.admin_dashboard'))
        flash('Invalid admin credentials', 'danger')
    return render_template('admin/login.html', form=form)

@bp.route('/admin')
@bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    user_count = User.query.count()
    product_count = Product.query.count()
    order_count = Order.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', 
                         user_count=user_count,
                         product_count=product_count,
                         order_count=order_count,
                         recent_orders=recent_orders)

@bp.route('/admin/users')
@login_required
@admin_required
def user_management():
    users = User.query.all()
    return render_template('admin/user_management.html', users=users)

@bp.route('/admin/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = EditUserForm()
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.set_password(form.password.data)
        user.is_admin = form.is_admin.data
        user.admin_access_level = form.admin_access_level.data
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('main.user_management'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.is_admin.data = user.is_admin
        form.admin_access_level.data = user.admin_access_level
    
    return render_template('admin/edit_user.html', form=form, user=user)

@bp.route('/admin/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    return redirect(url_for('main.user_management'))

@bp.route('/admin/orders')
@login_required
@admin_required
def order_management():
    orders = Order.query.all()
    return render_template('admin/order_management.html', orders=orders)

@bp.route('/admin/orders/<int:id>/view')
@login_required
@admin_required
def view_order(id):
    order = Order.query.get_or_404(id)
    return render_template('admin/view_order.html', order=order)

@bp.route('/admin/orders/<int:id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_order_status(id):
    order = Order.query.get_or_404(id)
    if request.method == 'POST':
        order.status = request.form.get('status')
        db.session.commit()
        flash('Order status updated successfully!', 'success')
        return redirect(url_for('main.order_management'))
    return render_template('admin/update_order_status.html', order=order)

@bp.route('/admin/orders/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_order(id):
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    flash('Order deleted successfully!', 'success')
    return redirect(url_for('main.order_management'))
# app/routes.py

@bp.route('/admin/products', methods=['GET', 'POST'])
@login_required
@admin_required
def product_management():
    form = ProductForm()
    form.brand.choices = [(b.id, b.name) for b in Brand.query.all()]
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            brand_id=form.brand.data,
            category_id=form.category.data
        )
        db.session.add(product)
        db.session.commit()  # Commit first to get product.id

        # Handle multiple images
        for i, image_field in enumerate([form.image1, form.image2, form.image3, form.image4], 1):
            if image_field.data:
                file = image_field.data
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{product.id}_image{i}_{file.filename}")
                    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    product_image = ProductImage(product_id=product.id, image=filename)
                    db.session.add(product_image)
        db.session.commit()
        flash('Product created successfully!', 'success')
        return redirect(url_for('main.product_management'))
    
    products = Product.query.all()
    return render_template('admin/product_management.html', form=form, products=products)

@bp.route('/admin/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm()
    form.brand.choices = [(b.id, b.name) for b in Brand.query.all()]
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.brand_id = form.brand.data
        product.category_id = form.category.data
        db.session.commit()  # Commit product changes first

        # Handle multiple images
        for i, image_field in enumerate([form.image1, form.image2, form.image3, form.image4], 1):
            if image_field.data:
                file = image_field.data
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{product.id}_image{i}_{file.filename}")
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    product_image = ProductImage(product_id=product.id, image=filename)
                    db.session.add(product_image)
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('main.product_management'))
        
    elif request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.price.data = product.price
        form.brand.data = product.brand_id
        form.category.data = product.category_id
    
    return render_template('admin/edit_product.html', form=form, product=product)

@bp.route('/admin/products/<int:id>/delete')
@login_required
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    
    # Delete associated images from filesystem
    for image in product.images:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image.image)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('main.product_management'))

@bp.route('/admin/brands', methods=['GET', 'POST'])
@login_required
@admin_required
def brand_management():
    form = BrandForm()
    if form.validate_on_submit():
        brand = Brand(name=form.name.data)
        db.session.add(brand)
        db.session.commit()
        flash('Brand created successfully!', 'success')
        return redirect(url_for('main.brand_management'))
    
    brands = Brand.query.all()
    return render_template('admin/brand_management.html', form=form, brands=brands)

@bp.route('/admin/brands/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_brand(id):
    brand = Brand.query.get_or_404(id)
    form = BrandForm()
    if form.validate_on_submit():
        brand.name = form.name.data
        db.session.commit()
        flash('Brand updated successfully!', 'success')
        return redirect(url_for('main.brand_management'))
    elif request.method == 'GET':
        form.name.data = brand.name
    return render_template('admin/edit_brand.html', form=form, brand=brand)

@bp.route('/admin/brands/<int:id>/delete')
@login_required
@admin_required
def delete_brand(id):
    brand = Brand.query.get_or_404(id)
    db.session.delete(brand)
    db.session.commit()
    flash('Brand deleted successfully!', 'success')
    return redirect(url_for('main.brand_management'))

@bp.route('/admin/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def category_management():
    form = CategoryForm()
    if form.validate_on_submit():
        # Handle image upload
        if form.image.data:
            image = form.image.data
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                
                category = Category(
                    name=form.name.data,
                    image=filename
                )
                db.session.add(category)
                db.session.commit()
                flash('Category created successfully!', 'success')
                return redirect(url_for('main.category_management'))
            else:
                flash('Invalid file type. Please upload an image.', 'danger')
        else:
            category = Category(name=form.name.data)
            db.session.add(category)
            db.session.commit()
            flash('Category created successfully!', 'success')
            return redirect(url_for('main.category_management'))

    categories = Category.query.all()
    return render_template('admin/category_management.html', form=form, categories=categories)

@bp.route('/admin/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('main.category_management'))
    elif request.method == 'GET':
        form.name.data = category.name
    return render_template('admin/edit_category.html', form=form, category=category)

@bp.route('/admin/categories/<int:id>/delete')
@login_required
@admin_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('main.category_management'))

@bp.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    from app.forms import GeneralSettingsForm, ContactSettingsForm, SMTPSettingsForm, AddressSettingsForm
    general_form = GeneralSettingsForm()
    contact_form = ContactSettingsForm()
    smtp_form = SMTPSettingsForm()
    address_form = AddressSettingsForm()

    settings_obj = Settings.query.first()
    if not settings_obj:
        settings_obj = Settings()
        db.session.add(settings_obj)
        db.session.commit()

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'general_settings' and general_form.validate_on_submit():
            settings_obj.site_name = general_form.site_name.data
            settings_obj.description = general_form.description.data
            settings_obj.site_url = general_form.site_url.data
        elif form_type == 'contact_settings' and contact_form.validate_on_submit():
            settings_obj.contact_email = contact_form.contact_email.data
            settings_obj.sales_email = contact_form.sales_email.data
            settings_obj.support_email = contact_form.support_email.data
            settings_obj.phone_number = contact_form.phone_number.data
        elif form_type == 'smtp_settings' and smtp_form.validate_on_submit():
            settings_obj.smtp_server = smtp_form.smtp_server.data
            settings_obj.smtp_port = smtp_form.smtp_port.data
            settings_obj.smtp_username = smtp_form.smtp_username.data
            settings_obj.smtp_password = smtp_form.smtp_password.data
            settings_obj.smtp_use_tls = smtp_form.smtp_use_tls.data
        elif form_type == 'address_settings' and address_form.validate_on_submit():
            settings_obj.address_line1 = address_form.address_line1.data
            settings_obj.address_line2 = address_form.address_line2.data
            settings_obj.city = address_form.city.data
            settings_obj.state = address_form.state.data
            settings_obj.postal_code = address_form.postal_code.data
            settings_obj.country = address_form.country.data
        db.session.commit()
        flash('Settings updated successfully', 'success')
        return redirect(url_for('main.settings'))

    # Pre-populate forms with existing settings data
    if settings_obj:
        general_form.site_name.data = settings_obj.site_name
        general_form.description.data = settings_obj.description
        general_form.site_url.data = settings_obj.site_url

        contact_form.contact_email.data = settings_obj.contact_email
        contact_form.sales_email.data = settings_obj.sales_email
        contact_form.support_email.data = settings_obj.support_email
        contact_form.phone_number.data = settings_obj.phone_number

        smtp_form.smtp_server.data = settings_obj.smtp_server
        smtp_form.smtp_port.data = settings_obj.smtp_port
        smtp_form.smtp_username.data = settings_obj.smtp_username
        smtp_form.smtp_use_tls.data = settings_obj.smtp_use_tls

        address_form.address_line1.data = settings_obj.address_line1
        address_form.address_line2.data = settings_obj.address_line2
        address_form.city.data = settings_obj.city
        address_form.state.data = settings_obj.state
        address_form.postal_code.data = settings_obj.postal_code
        address_form.country.data = settings_obj.country

    return render_template('admin/settings.html',
                           settings=settings_obj,
                           general_form=general_form,
                           contact_form=contact_form,
                           smtp_form=smtp_form,
                           address_form=address_form)

# Auth Routes
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_administrator():
            return redirect(url_for('main.admin_dashboard'))
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            if user.is_administrator():
                return redirect(url_for('main.admin_dashboard'))
            return redirect(url_for('main.home'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Create new user with selected role
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data,
                is_admin=False,  # Always false for regular registration
                admin_access_level=0  # No admin access for regular registration
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()

            # Create cart for new user
            cart = Cart(user_id=user.id)
            db.session.add(cart)
            db.session.commit()
            
            # Auto login after registration
            login_user(user)
            flash(f'Successfully registered as {form.role.data.title()}!', 'success')
            return redirect(url_for('main.home'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
            
    return render_template('register.html', form=form)

@bp.route('/products')
def products():
    # Get filter parameters with safe integer conversion
    try:
        category_id = int(request.args.get('category_id')) if request.args.get('category_id') else None
        brand_id = int(request.args.get('brand_id')) if request.args.get('brand_id') else None
    except (ValueError, TypeError):
        category_id = None
        brand_id = None
    
    # Base query
    query = Product.query
    
    # Apply filters only if they have valid values
    if category_id:
        query = query.filter_by(category_id=category_id)
    if brand_id:
        query = query.filter_by(brand_id=brand_id)
    
    # Get all categories for the filter sidebar
    categories = Category.query.all()
    brands = Brand.query.all()
    
    # Get filtered products
    products = query.all()
    
    return render_template(
        'products_list.html',
        products=products,
        categories=categories,
        brands=brands,
        category_id=category_id,
        brand_id=brand_id
    )

@bp.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('main.products'))
    
    # Search in product names, descriptions, brands, and categories
    products = Product.query.join(Brand).join(Category).filter(
        db.or_(
            Product.name.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%'),
            Brand.name.ilike(f'%{query}%'),
            Category.name.ilike(f'%{query}%')
        )
    ).all()
    
    return render_template(
        'products_list.html',
        products=products,
        search_query=query,
        categories=Category.query.all(),
        brands=Brand.query.all()
    )

@bp.route('/brands')
def brands():
    brands = Brand.query.all()
    return render_template('brands_list.html', brands=brands)

@bp.route('/categories')
def categories():
    categories = Category.query.all()
    return render_template('categories_list.html', categories=categories)

@bp.route('/cart')
@login_required
def cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    return render_template('cart.html', cart=cart)

@bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    try:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
        
        # Get quantity from form, default to 1
        try:
            quantity = int(request.form.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1
        
        product = Product.query.get_or_404(product_id)
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        
        db.session.commit()
        
        # Return JSON response with cart info
        return jsonify({
            'status': 'success',
            'message': f'{product.name} added to cart successfully!',
            'cart_count': len(cart.items),
            'cart_total': f"${cart.get_total():.2f}"
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error adding to cart: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to add item to cart.'
        }), 400

@bp.route('/cart/remove/<int:item_id>', methods=['POST', 'GET'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id == current_user.id:
        try:
            db.session.delete(cart_item)
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                cart = Cart.query.filter_by(user_id=current_user.id).first()
                return jsonify({
                    'status': 'success',
                    'message': 'Item removed from item shop!',
                    'cart_count': len(cart.items),
                    'cart_total': f"${cart.get_total():.2f}"
                })
            
            flash('Item removed from item shop!', 'success')
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to remove item from item shop.'
                }), 400
            flash('Error removing item from item shop.', 'danger')
            
    return redirect(url_for('main.cart'))

@bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id == current_user.id:
        try:
            quantity = int(request.form.get('quantity', 1))
            if quantity > 0:
                cart_item.quantity = quantity
                db.session.commit()
                # Calculate updated subtotal and cart total
                subtotal = cart_item.get_subtotal()
                cart_total = cart_item.cart.get_total()
                return jsonify({
                    'success': True,
                    'message': 'Cart updated successfully!',
                    'subtotal': f"{subtotal:.2f}",
                    'cart_total': f"{cart_total:.2f}"
                })
            else:
                db.session.delete(cart_item)
                db.session.commit()
                flash('Item removed from cart!', 'success')
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid quantity provided'})
    return redirect(url_for('main.cart'))

@bp.route('/order/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized access to order', 'danger')
        return redirect(url_for('main.home'))
    return render_template('order_confirmation.html', order=order)

@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart or not cart.items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('main.cart'))
    
    form = CheckoutForm(request.form)
    if form.validate_on_submit():
        try:
            # --- CLEANUP: Remove orphaned Checkout records for this user ---
            Checkout.query.filter_by(user_id=current_user.id, order_id=None).delete()
            db.session.commit()
            # -------------------------------------------------------------

            # 1. Create order record with payment method
            order = Order(
                user_id=current_user.id,
                total=cart.get_total(),
                status='pending',
                payment_method=form.payment_method.data,
                special_notes=form.order_notes.data
            )
            db.session.add(order)
            db.session.flush()  # Get order ID

            # 2. Create payment record with all details
            payment = Payment(
                order_id=order.id,
                amount=order.total,
                method=form.payment_method.data,
                status='pending',
                card_last4=form.card_number.data[-4:] if form.payment_method.data == 'credit_card' else None,
                cardholder_name=form.cardholder_name.data if form.payment_method.data == 'credit_card' else None
            )
            db.session.add(payment)
            db.session.flush()  # Get payment ID

            # 3. Create checkout record with full details (always create new)
            checkout = Checkout(
                order_id=order.id,
                user_id=current_user.id,
                payment_id=payment.id,
                shipping_address=f"{form.full_name.data}\n{form.shipping_address.data}\n{form.city.data}, {form.state.data} {form.postal_code.data}\n{form.country.data}",
                billing_address=f"{form.full_name.data}\n{form.shipping_address.data}\n{form.city.data}, {form.state.data} {form.postal_code.data}\n{form.country.data}",
                contact_email=form.email.data,
                contact_phone=form.phone.data,
                order_notes=form.order_notes.data
            )
            db.session.add(checkout)
            db.session.flush()

            # 4. Create order items and clear cart
            for cart_item in cart.items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                db.session.add(order_item)
                db.session.delete(cart_item)  # Remove item from cart
            
            # Clear all items from cart
            cart.items = []
            
            # 5. Send notifications to admin users
            admin_users = User.query.filter_by(is_admin=True).all()
            for admin in admin_users:
                notification = AdminNotification(
                    user_id=admin.id,
                    order_id=order.id,
                    message=f"""New order #{order.id}
                    Customer: {current_user.username}
                    Total: ${order.total:.2f}
                    Items: {len(cart.items)}""",
                    type='new_order'
                )
                db.session.add(notification)

            # 6. Commit all changes
            db.session.commit()
            
            flash('Order placed successfully! Our team will process it soon.', 'success')
            return redirect(url_for('main.order_confirmation', order_id=order.id))

        except Exception as e:
            db.session.rollback()
            flash('Error processing order: ' + str(e), 'danger')
            return render_template('checkout.html', form=form, cart=cart)

    return render_template('checkout.html', form=form, cart=cart)

def notify_admin(order, checkout):
    admin_users = User.query.filter_by(is_admin=True).all()
    for admin in admin_users:
        notification = AdminNotification(
            user_id=admin.id,
            order_id=order.id,
            message=f"""
            New order #{order.id}
            Customer: {checkout.contact_email}
            Phone: {checkout.contact_phone}
            Total: ${order.total:.2f}
            """,
            type='order_processing'
        )
        db.session.add(notification)

@bp.route('/admin/notifications')
@login_required
@admin_required
def admin_notifications():
    notifications = AdminNotification.query.filter_by(user_id=current_user.id).order_by(AdminNotification.created_at.desc()).all()
    return render_template('admin/notifications.html', notifications=notifications)

@bp.route('/admin/notifications/mark_read/<int:id>')
@login_required
@admin_required
def mark_notification_read(id):
    notification = AdminNotification.query.get_or_404(id)
    notification.read = True
    db.session.commit()
    return redirect(url_for('main.admin_notifications'))

@bp.route('/admin/notifications/clear-all', methods=['POST'])
@login_required
@admin_required
def clear_all_notifications():
    try:
        AdminNotification.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash('All notifications cleared', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to clear notifications: ' + str(e), 'danger')
    return redirect(url_for('main.admin_notifications'))

@bp.route('/admin/profile')
@login_required
@admin_required
def admin_profile():
    orders_count = Order.query.count()
    products_count = Product.query.count()
    users_count = User.query.count()
    return render_template('admin/profile.html', 
                         orders_count=orders_count,
                         products_count=products_count,
                         users_count=users_count)

@bp.route('/profile')
@login_required
def user_profile():
    if current_user.is_administrator():
        return redirect(url_for('main.admin_profile'))
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('user/profile.html', orders=orders)

@bp.route('/user/settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    form = UserSettingsForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.username = form.username.data
            current_user.email = form.email.data
            if form.new_password.data:
                current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your settings have been updated!', 'success')
            return redirect(url_for('main.user_profile'))
        flash('Current password is incorrect!', 'danger')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('user/settings.html', form=form)

@bp.route('/user/orders')
@login_required
def user_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('user/orders.html', orders=orders)

@bp.route('/user/addresses')
@login_required
def user_addresses():
    # For now we'll just redirect to user settings since we haven't implemented addresses yet
    flash('Address management will be available soon!', 'info')
    return redirect(url_for('main.user_settings'))

@bp.route('/admin/orders/<int:order_id>/process', methods=['POST'])
@login_required
@admin_required
def process_order(order_id):
    if not request.form.get('csrf_token'):
        return jsonify({'error': 'CSRF token missing'}), 400
        
    order = Order.query.get_or_404(order_id)
    action = request.form.get('action')
    
    try:
        if action == 'process':
            order.status = 'processing'
            notification = AdminNotification(
                user_id=current_user.id,
                order_id=order.id,
                message=f"Order #{order.id} is ready for shipping",
                type='shipping'
            )
            db.session.add(notification)
            flash('Order marked for processing', 'success')
        
        elif action == 'complete':
            order.status = 'completed'
            flash('Order marked as completed', 'success')
        
        db.session.commit()
        return redirect(url_for('main.order_management'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error processing order: {str(e)}', 'danger')
        return redirect(url_for('main.order_management'))

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        email = request.json.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            reset_token = user.get_reset_token()
            
            # Send reset email
            send_reset_email(user.email, reset_token)
            
            return jsonify({'success': True})
        
        return jsonify({
            'success': False, 
            'message': 'No account found with that email address'
        }), 404
        
    return render_template('auth/forgot_password.html')

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired reset token', 'danger')
        return redirect(url_for('main.forgot_password'))
        
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset!', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('auth/reset_password.html', form=form)

@bp.context_processor
def utility_processor():
    return {
        'now': datetime.utcnow(),
        'Cart': Cart  # Add Cart to the context
    }