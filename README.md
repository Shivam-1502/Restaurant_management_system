# Restaurant Management System

A modern, full-featured restaurant management system built with Flask, featuring a responsive UI and comprehensive management tools for both administrators and employees.

## Features

### Admin Dashboard
- Employee Management
  - Add, edit, and remove employees
  - Manage employee roles and permissions
  - View employee performance metrics

- Menu Management
  - Add, edit, and remove menu items
  - Set prices and categories
  - Add item descriptions and details

- Inventory Management
  - Track stock levels
  - Set reorder points
  - Monitor inventory usage

- Sales Reports
  - View daily, weekly, and monthly sales
  - Track revenue metrics
  - Generate detailed reports

### Employee Dashboard
- Order Management
  - Create new orders
  - Process payments (Cash, Card, UPI)
  - Generate bills
  - View order history

- Real-time Updates
  - Track order status
  - Monitor pending orders
  - View completed orders

## Technical Features
- Secure authentication system
- Role-based access control
- Responsive design
- Modern UI with animations
- QR code generation for payments
- Form validation
- Flash messages for user feedback

## Technologies Used
- Backend: Python Flask
- Database: SQLAlchemy
- Frontend: HTML5, CSS3, JavaScript
- UI Framework: Bootstrap 4
- Icons: Font Awesome
- Animations: Custom CSS3

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/restaurant-management-system.git
cd restaurant-management-system
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Initialize the database
```bash
python reset_db.py
```

5. Run the application
```bash
python run.py
```

## Environment Variables
Create a `.env` file in the root directory with the following variables:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///restaurant.db
PAYMENT_UPI_ID=your_upi_id
PAYMENT_MERCHANT_NAME=your_restaurant_name
```

## Project Structure
```
Flask_rms/
├── app/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   ├── routes/
│   ├── models.py
│   └── forms/
├── instance/
├── venv/
├── requirements.txt
├── run.py
└── README.md
```

## Usage

### Admin Access
1. Login with admin credentials
2. Access the admin dashboard
3. Manage employees, menu items, and inventory
4. View sales reports and analytics

### Employee Access
1. Login with employee credentials
2. Create and manage orders
3. Process payments
4. Generate bills

## Security Features
- Password hashing
- Session management
- CSRF protection
- Input validation
- Role-based access control

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Acknowledgments
- Flask documentation
- Bootstrap team
- Font Awesome
- Animate.css

## Support
For support, email shivamuod@gmail.com or open an issue on GitHub. 
