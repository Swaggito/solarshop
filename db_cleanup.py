from app import create_app, db
from app.models import Product, ProductImage

def cleanup_orphaned_images():
    app = create_app()
    with app.app_context():
        # Delete any product images with NULL product_id
        ProductImage.query.filter_by(product_id=None).delete()
        
        # Delete any product images where the product no longer exists
        ProductImage.query.filter(
            ~ProductImage.product_id.in_(
                db.session.query(Product.id)
            )
        ).delete(synchronize_session=False)
        
        db.session.commit()
        print("Database cleaned up successfully!")

if __name__ == '__main__':
    cleanup_orphaned_images()
