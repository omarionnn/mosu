from app import app, db

def create_db():
    with app.app_context():
        db.drop_all()  # Drop all existing tables
        db.create_all()  # Create all tables
        print("Database tables created successfully!")

if __name__ == '__main__':
    create_db()
