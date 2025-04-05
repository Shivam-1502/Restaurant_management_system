from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.utils.access_control import admin_required
from app.models import db, Employee, MenuItem, Inventory, Orders, Payment
from app.forms.login_form import EmployeeForm, EditEmployeeForm, MenuItemForm, InventoryForm
from datetime import date, datetime, timedelta
from sqlalchemy import func
from sqlalchemy.sql import extract

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
@admin_required
@login_required
def admin_dashboard():
    """Admin dashboard route."""
    # Get statistics
    employee_count = Employee.query.count()
    menu_count = MenuItem.query.count()
    pending_orders = Orders.query.filter_by(status='Pending').count()
    
    # Calculate today's revenue
    today = date.today().strftime("%Y%m%d")
    today_orders = Orders.query.filter(
        Orders.orderID.like(f'ORD{today}%'),
        Orders.status == 'Completed'
    ).all()
    today_revenue = sum(order.totalAmount for order in today_orders)

    # Get recent orders (last 5)
    recent_orders = Orders.query.order_by(Orders.orderID.desc()).limit(5).all()

    stats = {
        'employee_count': employee_count,
        'menu_count': menu_count,
        'pending_orders': pending_orders,
        'today_revenue': today_revenue
    }

    return render_template("admin_dashboard.html", stats=stats, recent_orders=recent_orders)

# ✅ Manage Employees
@admin_bp.route("/dashboard/employees", methods=["GET"])
@admin_required
@login_required
def manage_employees():
    employees = Employee.query.all()
    return render_template("manage_employees.html", employees=employees)

# ✅ Add Employee
@admin_bp.route("/dashboard/employees/add", methods=["GET", "POST"])
@admin_required
@login_required
def add_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        # Check if username already exists
        if Employee.query.filter_by(username=form.username.data).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('admin.add_employee'))
        
        # Check if email already exists
        if Employee.query.filter_by(email=form.email.data).first():
            flash('Email already exists. Please use a different email.', 'danger')
            return redirect(url_for('admin.add_employee'))

        employee = Employee(
            username=form.username.data,
            email=form.email.data,
            contact_details=form.contact_details.data,
            role='Employee'
        )
        employee.set_password(form.password.data)
        
        try:
            db.session.add(employee)
            db.session.commit()
            flash('Employee added successfully!', 'success')
            return redirect(url_for('admin.manage_employees'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the employee. Please try again.', 'danger')
            return redirect(url_for('admin.add_employee'))

    return render_template("add_employee.html", form=form)

# ✅ Edit Employee
@admin_bp.route("/dashboard/employees/edit/<int:employee_id>", methods=["GET", "POST"])
@admin_required
@login_required
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    form = EditEmployeeForm(obj=employee)

    if form.validate_on_submit():
        employee.username = form.username.data
        employee.email = form.email.data
        employee.contact_details = form.contact_details.data
        db.session.commit()
        flash("Employee updated successfully!", "success")
        return redirect(url_for("admin.manage_employees"))

    return render_template("edit_employee.html", form=form, employee=employee)

# ✅ Delete Employee
@admin_bp.route("/dashboard/employees/delete/<int:employee_id>", methods=["POST"])
@admin_required
@login_required
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    flash("Employee deleted successfully!", "success")
    return redirect(url_for("admin.manage_employees"))

# ✅ Manage Menu Items (Display all items)
@admin_bp.route("/dashboard/menu", methods=["GET"])
@admin_required
@login_required
def manage_menu():
    menu_items = MenuItem.query.all()  # Get all menu items from the database
    return render_template("manage_menu.html", menu_items=menu_items)

# ✅ Add Menu Item
@admin_bp.route("/dashboard/menu/add", methods=["GET", "POST"])
@admin_required
@login_required
def add_menu_item():
    form = MenuItemForm()
    if form.validate_on_submit():
        menu_item = MenuItem(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data
        )
        try:
            db.session.add(menu_item)
            db.session.commit()
            flash("Menu item added successfully!", "success")
            return redirect(url_for("admin.manage_menu"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding menu item: {str(e)}", "error")
            return redirect(url_for("admin.add_menu_item"))
    
    return render_template("add_menu_item.html", form=form)

# ✅ Edit Menu Item
@admin_bp.route("/dashboard/menu/edit/<int:menuItemID>", methods=["GET", "POST"])
@admin_required
@login_required
def edit_menu_item(menuItemID):
    menu_item = MenuItem.query.get_or_404(menuItemID)
    form = MenuItemForm(obj=menu_item)

    if form.validate_on_submit():
        try:
            menu_item.name = form.name.data
            menu_item.description = form.description.data
            menu_item.price = form.price.data
            menu_item.category = form.category.data
            db.session.commit()
            flash("Menu item updated successfully!", "success")
            return redirect(url_for("admin.manage_menu"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating menu item: {str(e)}", "error")
            return redirect(url_for("admin.edit_menu_item", menuItemID=menuItemID))
    
    return render_template("edit_menu_item.html", form=form, menu_item=menu_item)

# ✅ Delete Menu Item
@admin_bp.route("/dashboard/menu/delete/<int:menuItemID>", methods=["POST"])
@admin_required
@login_required
def delete_menu_item(menuItemID):
    menu_item = MenuItem.query.get_or_404(menuItemID)
    db.session.delete(menu_item)
    db.session.commit()
    flash("Menu item deleted successfully!", "success")
    return redirect(url_for("admin.manage_menu"))

# ✅ Add Inventory Item
@admin_bp.route("/dashboard/inventory/add", methods=["GET", "POST"])
@admin_required
@login_required
def add_inventory():
    form = InventoryForm()
    if form.validate_on_submit():
        inventory_item = Inventory(
            name=form.name.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            reorder_level=form.reorder_level.data,
            supplier=form.supplier.data
        )
        try:
            db.session.add(inventory_item)
            db.session.commit()
            flash("Inventory item added successfully!", "success")
            return redirect(url_for("admin.manage_inventory"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding inventory item: {str(e)}", "error")
            return redirect(url_for("admin.add_inventory"))

    return render_template("add_inventory.html", form=form)

# ✅ Edit Inventory Item
@admin_bp.route("/dashboard/inventory/edit/<int:item_id>", methods=["GET", "POST"])
@admin_required
@login_required
def edit_inventory(item_id):
    inventory_item = Inventory.query.get_or_404(item_id)
    form = InventoryForm(obj=inventory_item)

    if form.validate_on_submit():
        try:
            inventory_item.name = form.name.data
            inventory_item.quantity = form.quantity.data
            inventory_item.unit = form.unit.data
            inventory_item.reorder_level = form.reorder_level.data
            inventory_item.supplier = form.supplier.data
            db.session.commit()
            flash("Inventory item updated successfully!", "success")
            return redirect(url_for("admin.manage_inventory"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating inventory item: {str(e)}", "error")
            return redirect(url_for("admin.edit_inventory", item_id=item_id))

    return render_template("edit_inventory.html", form=form, inventory_item=inventory_item)

# ✅ Delete Inventory Item
@admin_bp.route("/dashboard/inventory/delete/<int:item_id>", methods=["POST"])
@admin_required
@login_required
def delete_inventory(item_id):
    inventory_item = Inventory.query.get_or_404(item_id)
    db.session.delete(inventory_item)
    db.session.commit()
    flash("Inventory item deleted successfully!", "success")
    return redirect(url_for("admin.manage_inventory"))

# ✅ Manage Inventory
@admin_bp.route("/dashboard/inventory", methods=["GET"])
@admin_required
@login_required
def manage_inventory():
    inventory_items = Inventory.query.all()
    return render_template("manage_inventory.html", inventory_items=inventory_items)

# ✅ View Orders
@admin_bp.route("/dashboard/orders", methods=["GET"])
@admin_required
@login_required
def view_orders():
    # Fetch pending and completed orders
    pending_orders = Orders.query.filter_by(status='Pending').all()
    completed_orders = Orders.query.filter_by(status='Completed').all()

    return render_template("view_orders.html", pending_orders=pending_orders, completed_orders=completed_orders)

# ✅ Mark Order as Completed
@admin_bp.route("/dashboard/orders/mark_completed/<string:order_id>", methods=["GET"])
@admin_required
@login_required
def mark_order_completed(order_id):
    order = Orders.query.get_or_404(order_id)
    order.status = 'Completed'
    db.session.commit()
    flash("Order marked as completed.", "success")
    return redirect(url_for('admin.view_orders'))

# ✅ View Order Details
@admin_bp.route("/dashboard/orders/details/<string:order_id>", methods=["GET"])
@admin_required
@login_required
def view_order_details(order_id):
    order = Orders.query.get_or_404(order_id)
    return render_template("view_order_details.html", order=order)

# ✅ Sales Management
@admin_bp.route("/dashboard/sales", methods=["GET"])
@admin_required
@login_required
def view_sales():
    # Get filter parameters
    start_date = request.args.get('start_date', date.today().strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
    
    # Convert string dates to date objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Query sales data
    sales_data = db.session.query(
        func.strftime('%Y-%m-%d', func.substr(Orders.orderID, 4, 8)).label('date'),
        func.count(Orders.orderID).label('order_count'),
        func.sum(Orders.totalAmount).label('total_sales')
    ).filter(
        func.substr(Orders.orderID, 4, 8).between(
            start_date.strftime('%Y%m%d'),
            end_date.strftime('%Y%m%d')
        )
    ).group_by(
        func.strftime('%Y-%m-%d', func.substr(Orders.orderID, 4, 8))
    ).all()
    
    # Calculate summary statistics
    total_orders = sum(sale.order_count for sale in sales_data)
    total_revenue = sum(sale.total_sales for sale in sales_data)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Get payment method distribution
    payment_stats = db.session.query(
        Payment.paymentMethod,
        func.count(Payment.paymentID).label('count'),
        func.sum(Payment.amount).label('total')
    ).join(Orders).filter(
        func.substr(Orders.orderID, 4, 8).between(
            start_date.strftime('%Y%m%d'),
            end_date.strftime('%Y%m%d')
        )
    ).group_by(Payment.paymentMethod).all()
    
    return render_template(
        "sales_report.html",
        sales_data=sales_data,
        start_date=start_date,
        end_date=end_date,
        total_orders=total_orders,
        total_revenue=total_revenue,
        avg_order_value=avg_order_value,
        payment_stats=payment_stats
    )
