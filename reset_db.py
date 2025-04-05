from app import create_app, db
from app.models import Admin, Employee, MenuItem, Inventory, Orders, Payment, OrderItem, Customer

def reset_database():
    app = create_app()
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Add sample admin
        admin = Admin(
            username='admin',
            email='admin@restaurant.com',
            role='Admin',
            contact_details='1234567890'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Add sample employee
        employee = Employee(
            username='employee',
            email='employee@restaurant.com',
            role='Employee',
            contact_details='9876543210'
        )
        employee.set_password('employee123')
        db.session.add(employee)
        
        # Add sample customers
        customers = [
            Customer(name='John Doe', email='john@example.com', phone='1234567890'),
            Customer(name='Jane Smith', email='jane@example.com', phone='0987654321'),
            Customer(name='Bob Johnson', email='bob@example.com', phone='1122334455')
        ]
        db.session.add_all(customers)
        
        # Add sample menu items
        menu_items = [
            MenuItem(
                name='Burger',
                description='Juicy beef patty with fresh lettuce, tomatoes, and special sauce',
                price=9.99,
                category='Main Course'
            ),
            MenuItem(
                name='Pizza',
                description='Hand-tossed pizza with mozzarella cheese and your choice of toppings',
                price=12.99,
                category='Main Course'
            ),
            MenuItem(
                name='Salad',
                description='Fresh garden salad with mixed greens and house dressing',
                price=7.99,
                category='Appetizer'
            ),
            MenuItem(
                name='Ice Cream',
                description='Creamy vanilla ice cream with chocolate sauce',
                price=4.99,
                category='Dessert'
            )
        ]
        db.session.add_all(menu_items)
        
        # Add sample inventory
        inventory_items = [
            Inventory(name='Beef', quantity=100, unit='kg', reorder_level=20, supplier='Meat Co'),
            Inventory(name='Cheese', quantity=200, unit='kg', reorder_level=30, supplier='Dairy Co'),
            Inventory(name='Lettuce', quantity=50, unit='pieces', reorder_level=15, supplier='Veggie Co')
        ]
        db.session.add_all(inventory_items)
        
        # Commit all changes
        db.session.commit()
        
        print("Database reset and sample data added successfully!")

if __name__ == '__main__':
    reset_database() 