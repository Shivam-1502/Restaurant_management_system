from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Email

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=100)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class EmployeeForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    contact_details = StringField("Contact Number", validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField("Add Employee")

class EditEmployeeForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    contact_details = StringField("Contact Number", validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField("Update Employee")

class MenuItemForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=3, max=255)])
    description = TextAreaField("Description")
    price = DecimalField("Price", validators=[DataRequired(), NumberRange(min=0)], places=2)
    category = SelectField("Category", choices=[
        ("Main Course", "Main Course"), 
        ("Starter", "Starter"), 
        ("Dessert", "Dessert"), 
        ("Beverage", "Beverage")
    ], validators=[DataRequired()])
    submit = SubmitField("Save")    

class InventoryForm(FlaskForm):
    name = StringField("Item Name", validators=[DataRequired(), Length(min=2, max=255)])
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=0)])
    unit = SelectField("Unit", choices=[
        ('pieces', 'Pieces'),
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('l', 'Liters'),
        ('ml', 'Milliliters')
    ], validators=[DataRequired()])
    reorder_level = IntegerField("Reorder Level", validators=[DataRequired(), NumberRange(min=1)])
    supplier = StringField("Supplier", validators=[DataRequired(), Length(min=2, max=255)])
    submit = SubmitField("Save Inventory Item")    