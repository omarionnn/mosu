from app import app, db, MenuItem

def init_db():
    with app.app_context():
        db.create_all()
        
        # Add menu items if they don't exist
        if not MenuItem.query.first():
            menu_items = [
                # Noodles/Rice
                {'name': 'Fresh Noodles', 'description': 'Handmade fresh noodles (VG)', 'category': 'Noodles/Rice', 'price': 4.00},
                {'name': 'Sweet Potato Noodles', 'description': 'Gluten-free sweet potato noodles (GF) (VG)', 'category': 'Noodles/Rice', 'price': 4.00},
                {'name': 'Rice Cakes', 'description': 'Traditional Korean rice cakes (GF) (VG)', 'category': 'Noodles/Rice', 'price': 4.00},
                {'name': 'White Rice', 'description': 'Steamed jasmine rice (GF) (VG) (16oz)', 'category': 'Noodles/Rice', 'price': 3.00},
                {'name': 'Egg Fried Rice', 'description': 'Wok-fried rice with eggs (16oz)', 'category': 'Noodles/Rice', 'price': 4.00},

                # Vegetables
                {'name': 'Broccoli', 'description': 'Fresh steamed broccoli', 'category': 'Vegetables', 'price': 4.00},
                {'name': 'Lotus Root', 'description': 'Sliced lotus root', 'category': 'Vegetables', 'price': 5.00},
                {'name': 'Enoki Mushroom', 'description': 'Fresh enoki mushrooms', 'category': 'Vegetables', 'price': 4.00},
                {'name': 'Wood Ear Mushroom', 'description': 'Rehydrated wood ear mushrooms', 'category': 'Vegetables', 'price': 4.00},

                # Tofu Items
                {'name': 'Silken Tofu', 'description': 'Soft silken tofu', 'category': 'Tofu', 'price': 3.00},
                {'name': 'Fried Tofu', 'description': 'Golden fried tofu cubes', 'category': 'Tofu', 'price': 3.00},
                {'name': 'Fried Bean Curd Rolls', 'description': 'Crispy bean curd rolls', 'category': 'Tofu', 'price': 4.00},

                # Specialty Items
                {'name': 'Beef Dumplings', 'description': 'Handmade beef dumplings', 'category': 'Specialty', 'price': 5.00},
                {'name': 'Lobster Balls', 'description': 'Premium lobster balls', 'category': 'Specialty', 'price': 5.00},
                {'name': 'Beef Meatballs', 'description': 'Seasoned beef meatballs', 'category': 'Specialty', 'price': 7.00},
                {'name': 'Fried Fish Tofu', 'description': 'Fish paste stuffed tofu', 'category': 'Specialty', 'price': 7.00},

                # Meats
                {'name': 'Sliced Beef Brisket', 'description': 'Thinly sliced beef brisket', 'category': 'Meats', 'price': 8.00},
                {'name': 'Sliced Lamb', 'description': 'Premium sliced lamb', 'category': 'Meats', 'price': 10.00},
                {'name': 'Marinated Sirloin', 'description': 'House marinated beef sirloin', 'category': 'Meats', 'price': 9.00},

                # Seafood
                {'name': 'Shrimp', 'description': 'Fresh tiger shrimp', 'category': 'Seafood', 'price': 8.00},
                {'name': 'Calamari', 'description': 'Sliced fresh squid', 'category': 'Seafood', 'price': 8.00},
                {'name': 'Mussels', 'description': 'Fresh black mussels', 'category': 'Seafood', 'price': 9.00},
                {'name': 'Scallops', 'description': 'Fresh sea scallops', 'category': 'Seafood', 'price': 12.00},

                # Premium Items
                {'name': 'Ribeye', 'description': 'Premium thick-cut ribeye (GF)', 'category': 'Premium', 'price': 13.00},
                {'name': 'Filet Mignon', 'description': 'Premium filet mignon (GF)', 'category': 'Premium', 'price': 13.00},
                {'name': 'Salmon', 'description': 'Fresh Atlantic salmon (GF)', 'category': 'Premium', 'price': 9.00}
            ]
            
            for item in menu_items:
                menu_item = MenuItem(
                    name=item['name'],
                    description=item['description'],
                    category=item['category'],
                    price=item['price']
                )
                db.session.add(menu_item)
            
            db.session.commit()
            print("Database initialized with menu items!")

if __name__ == '__main__':
    init_db()
