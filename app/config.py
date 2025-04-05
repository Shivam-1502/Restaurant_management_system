class Config:
    # Payment Settings
    PAYMENT_UPI_ID = "shivamiit2023-1@okicici"  # Replace with your actual UPI ID
    PAYMENT_MERCHANT_NAME = "Restaurant"  # Replace with your restaurant name
    
    # Other configuration settings can be added here
    SECRET_KEY = 'your-secret-key'  # Replace with your actual secret key
    SQLALCHEMY_DATABASE_URI = 'sqlite:///restaurant.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 