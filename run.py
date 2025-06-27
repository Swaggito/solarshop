from app import create_app, db
from app.models import User, Product, Brand, Category, Order, OrderItem, Payment, Settings  # Changed from SiteSettings to Settings

app = create_app()

with app.app_context():
    # Create/update admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin',
            is_admin=True,
            admin_access_level=2
        )
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("Admin user already exists")

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Product': Product, 'Brand': Brand, 
            'Category': Category, 'Order': Order, 'OrderItem': OrderItem, 
            'Payment': Payment, 'Settings': Settings}

if __name__ == '__main__':
    app.run(debug=True)