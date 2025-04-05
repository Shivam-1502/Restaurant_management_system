from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from app.utils.access_control import employee_required
from app.models import db, Orders, MenuItem, OrderItem, Payment, Customer
from datetime import datetime, date
import qrcode
import io
import base64
import os
from sqlalchemy import func
from app.config import Config

employee_bp = Blueprint("employee", __name__)

@employee_bp.route("/dashboard")
@login_required
def dashboard():
    # Get recent orders (last 5)
    recent_orders = Orders.query.order_by(Orders.orderID.desc()).limit(5).all()
    
    # Get statistics
    today = date.today().strftime("%Y%m%d")
    stats = {
        'pending_count': Orders.query.filter_by(status='Pending').count(),
        'completed_today': Orders.query.filter(
            Orders.status == 'Completed',
            Orders.orderID.like(f'ORD{today}%')
        ).count(),
        'total_sales_today': db.session.query(func.sum(Orders.totalAmount)).filter(
            Orders.status == 'Completed',
            Orders.orderID.like(f'ORD{today}%')
        ).scalar() or 0.0
    }
    
    return render_template('employee_dashboard.html', 
                         recent_orders=recent_orders,
                         stats=stats)

# Create New Order
@employee_bp.route("/dashboard/orders/create", methods=["GET", "POST"])
@employee_required
def create_order():
    if request.method == "POST":
        customer_name = request.form.get("customer_name")
        customer_email = request.form.get("customer_email")
        customer_phone = request.form.get("customer_phone")
        items = request.form.getlist("items[]")
        quantities = request.form.getlist("quantities[]")

        # Create or get customer
        customer = Customer.query.filter_by(email=customer_email).first()
        if not customer:
            customer = Customer(
                name=customer_name,
                email=customer_email,
                phone=customer_phone
            )
            db.session.add(customer)
            db.session.flush()  # Get customer ID without committing

        # Create order
        order_id = f'ORD{datetime.now().strftime("%Y%m%d%H%M%S")}'
        total_amount = 0

        order = Orders(
            orderID=order_id,
            employeeID=current_user.id,
            customerID=customer.id,
            status='Pending',
            totalAmount=0  # Will update after adding items
        )
        db.session.add(order)

        # Add order items
        for item_id, quantity in zip(items, quantities):
            menu_item = MenuItem.query.get(item_id)
            if menu_item:
                quantity = int(quantity)
                item_total = menu_item.price * quantity
                total_amount += item_total

                order_item = OrderItem(
                    orderID=order_id,
                    menuItemID=menu_item.menuItemID,
                    quantity=quantity,
                    price=menu_item.price
                )
                db.session.add(order_item)

        order.totalAmount = total_amount
        db.session.commit()
        flash("Order created successfully!", "success")
        return redirect(url_for('employee.dashboard'))

    # GET request - show order creation form
    menu_items = MenuItem.query.all()
    return render_template("create_order.html", menu_items=menu_items)

# View Orders
@employee_bp.route("/dashboard/orders", methods=["GET"])
@employee_required
def view_orders():
    print("Accessing view_orders route")
    pending_orders = Orders.query.filter_by(status='Pending').all()
    completed_orders = Orders.query.filter_by(status='Completed').all()
    
    # Generate payment QR code for pending orders
    payment_qr_codes = {}
    for order in pending_orders:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        # Use UPI ID from config
        qr_data = f"upi://pay?pa={Config.PAYMENT_UPI_ID}&pn={Config.PAYMENT_MERCHANT_NAME}&am={order.totalAmount}&tn=Order-{order.orderID}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert QR code to base64 string
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        payment_qr_codes[order.orderID] = base64.b64encode(buffered.getvalue()).decode()

    print(f"Found {len(pending_orders)} pending orders and {len(completed_orders)} completed orders")
    return render_template("view_orders.html", 
                         pending_orders=pending_orders, 
                         completed_orders=completed_orders,
                         payment_qr_codes=payment_qr_codes)

# Mark Order as Paid and Completed
@employee_bp.route("/dashboard/orders/mark_paid/<string:order_id>", methods=["POST"])
@employee_required
def mark_order_paid(order_id):
    try:
        order = Orders.query.get_or_404(order_id)
        payment_method = request.form.get("payment_method")
        
        if not payment_method:
            flash("Payment method is required.", "error")
            return redirect(url_for('employee.view_orders'))
        
        # Check if payment already exists
        existing_payment = Payment.query.filter_by(orderID=order.orderID).first()
        if existing_payment:
            flash("Payment already recorded for this order.", "warning")
            return redirect(url_for('employee.view_orders'))
        
        # Create payment record
        payment = Payment(
            orderID=order.orderID,
            amount=order.totalAmount,
            paymentMethod=payment_method
        )
        db.session.add(payment)
        
        # Mark order as completed
        order.status = 'Completed'
        
        try:
            db.session.commit()
            flash("Payment recorded and order marked as completed.", "success")
        except Exception as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")  # Debug log
            flash(f"Error processing payment: {str(e)}", "error")
            
    except Exception as e:
        print(f"General error: {str(e)}")  # Debug log
        flash(f"Error processing payment: {str(e)}", "error")
    
    return redirect(url_for('employee.view_orders'))

# Generate Bill
@employee_bp.route("/dashboard/orders/bill/<string:order_id>")
@employee_required
def generate_bill(order_id):
    order = Orders.query.get_or_404(order_id)
    return render_template("bill.html", order=order)

# View Order Details
@employee_bp.route("/dashboard/orders/details/<string:order_id>", methods=["GET"])
@employee_required
def view_order_details(order_id):
    print(f"Viewing details for order {order_id}")
    order = Orders.query.get_or_404(order_id)
    print(f"Order found: {order.orderID}, Status: {order.status}")
    return render_template("view_order_details.html", order=order)
