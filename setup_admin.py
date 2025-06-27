from app import create_app, db
from app.models import User

def setup_admin():
    app = create_app()
    with app.app_context():
        result = User.create_admin()
        print(result)

if __name__ == '__main__':
    setup_admin()
