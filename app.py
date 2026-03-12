from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
import datetime
import razorpay
from flask import Flask, render_template, jsonify
from datetime import date


app = Flask(__name__)
app.secret_key = "salon_secret"

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Pranathi@14",
    database="sallon_booking"
)

cursor = db.cursor(dictionary=True)

#-------RAZORPAY---------------
razorpay_client = razorpay.Client(auth=("rzp_test_xxxxxxx","xxxxxxx"))#PUT YOUR KEY ID AND KEY SECRECT CODE
# -----------------------------
# HOME PAGE
# -----------------------------
@app.route('/')
def home():
    return render_template("index.html")


# -----------------------------
# LOGIN REQUIRED PAGE
# -----------------------------
@app.route('/login_required')
def login_required():
    return render_template("login_required.html")


# -----------------------------
# MEN SERVICES
# -----------------------------
@app.route('/men_services')
def men_services():

    if "user_id" not in session:
        return redirect("/login_required")

    cursor.execute("SELECT * FROM services WHERE gender='men'")
    services = cursor.fetchall()

    return render_template("dashboard_men.html", services=services)


# -----------------------------
# WOMEN SERVICES
# -----------------------------
@app.route('/women_services')
def women_services():

    if "user_id" not in session:
        return redirect("/login_required")

    cursor.execute("SELECT * FROM services WHERE gender='women'")
    services = cursor.fetchall()

    return render_template("dashboard_women.html", services=services)

# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        # ADMIN LOGIN
        if email == "admin@gmail.com" and password == "admin123":
            session["admin"] = True
            return redirect("/admin")

        # USER LOGIN
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect("/")

        return "Invalid Login"

    return render_template("login.html")
# -----------------------------
# REGISTER
# -----------------------------
@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cursor.execute(
            "INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",
            (name,email,password)
        )

        db.commit()

        return redirect('/login')

    return render_template("register.html")


# -----------------------------
# CUSTOMER DASHBOARD
# -----------------------------
@app.route('/dashboard')
def dashboard():

    return render_template(
        "dashboard.html",
        current_date=datetime.date.today()
    )

#-------------ADMIN LOGIN------------

@app.route("/admin_login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin_dashboard")

        return "Invalid Admin Login"

    return render_template("admin_dashboard.html")



#-----------ADMIN 

@app.route('/admin')
def admin_dashboard():

    cursor.execute("SELECT * FROM bookings")
    bookings = cursor.fetchall()

    cursor.execute("SELECT * FROM payments")
    payments = cursor.fetchall()

    cursor.execute("SELECT * FROM staff")
    staff = cursor.fetchall()

    cursor.execute("SELECT * FROM services")
    services = cursor.fetchall()

    return render_template(
        "admin_dashboard.html",
        bookings=bookings,
        payments=payments,
        staff=staff,
        services=services
    )

# -----------------------------
# GALLERY
# -----------------------------
@app.route('/gallery')
def gallery():

    return render_template("gallery.html")


# -----------------------------
# REVIEWS
# -----------------------------
@app.route('/review', methods=['GET','POST'])
def review():

    if request.method == "POST":

        name = request.form['name']
        rating = request.form['rating']
        comment = request.form['comment']

        print(name, rating, comment)

    return render_template("review.html")


# -----------------------------
# CONTACT
# -----------------------------
@app.route('/contact', methods=['GET','POST'])
def contact():

    if request.method == "POST":

        email = request.form['email']
        message = request.form['message']

        print(email, message)

    return render_template("contact.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
# -----------------------------
# STAFF
# -----------------------------

@app.route('/staff_dashboard')
def staff_dashboard():

    cursor = db.cursor()

    cursor.execute("""
    SELECT id, customer_name, service, staff, time_slot
    FROM bookings
    ORDER BY id DESC
    """)

    bookings = cursor.fetchall()

    return render_template("staff_dashboard.html", bookings=bookings)
#-----------BOOK--------------

@app.route('/book', methods=['POST'])
def book():

    name = request.form['name']
    phone = request.form['phone']
    service = request.form['service']
    staff = request.form['staff']
    date = request.form['date']
    time = request.form['time']

    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO bookings
        (customer_name,customer_phone,service,staff_name,booking_date,booking_time)
        VALUES (%s,%s,%s,%s,%s,%s)
    """,(name,phone,service,staff,date,time))

    db.commit()

    return "Booking Successful!"


'''#--------BOOK LOGIC -------------

@app.route('/booking')
def booking():

    staff = request.args.get("staff")
    date = request.args.get("date")

    all_slots = [
        "10:00 AM","10:30 AM","11:00 AM","11:30 AM",
        "12:00 PM","01:00 PM","02:00 PM","03:00 PM","04:00 PM"
    ]

    cursor = db.cursor()

    cursor.execute(
        "SELECT booking_time FROM bookings WHERE staff_name=%s AND booking_date=%s",
        (staff,date)
    )

    booked = [row[0] for row in cursor.fetchall()]

    available = [slot for slot in all_slots if slot not in booked]

    return render_template("booking.html",
                           slots=available,
                           staff=staff,
                        date=date)
'''
#---------ADD STAFF-------------
from flask import request, jsonify

@app.route('/add_staff', methods=['POST'])
def add_staff():
    data = request.json
    name = data.get('name')
    qual = data.get('qual')
    exp = data.get('exp')
    gender = data.get('gender')

    # Check duplicate staff
    cursor.execute("SELECT * FROM staff WHERE name=%s", (name,))
    if cursor.fetchone():
        return jsonify({"status": "error", "message": "Staff already exists!"})

    cursor.execute("INSERT INTO staff (name, qual, exp, gender) VALUES (%s,%s,%s,%s)", (name, qual, exp, gender))
    db.commit()
    return jsonify({"status": "success", "message": "Staff added successfully!"})
#----------GET STAFF --------------
@app.route('/get_staff')
def get_staff():
    cursor.execute("SELECT * FROM staff")
    staff = cursor.fetchall()
    return jsonify({"staff": staff})

#-----------ADD SERVICES----------
@app.route('/add_service', methods=['POST'])
def add_service():

    name = request.form['service_name']
    price = request.form['price']
    category = request.form['category']

    cursor.execute(
        "INSERT INTO services (service_name,price,category) VALUES (%s,%s,%s)",
        (name,price,category)
    )

    db.commit()

    return redirect('/admin')

#----------PAYMENT------------
@app.route('/payment', methods=['POST'])
def payment():

    name = request.form['name']
    service = request.form['service']
    amount = request.form['amount']
    today = date.today()

    cursor.execute("""
        INSERT INTO payments
        (customer_name,service,amount,payment_date)
        VALUES (%s,%s,%s,%s)
    """,(name,service,amount,today))

    db.commit()

    return "Payment Successful"

# API to get booking and payment data
@app.route('/admin_data')
def admin_data():
    # Fetch bookings
    cursor.execute("SELECT * FROM bookings ORDER BY date DESC, time_slot ASC")
    bookings = cursor.fetchall()

    # Fetch payments
    cursor.execute("SELECT * FROM payments ORDER BY payment_date DESC")
    payments = cursor.fetchall()

    return jsonify({
        "bookings": bookings,
        "payments": payments
    })

#-BOOK_SERVICE---------------
@app.route('/book_service', methods=['POST'])
def book_service():
    data = request.json
    customer = data.get('customer_name')
    service = data.get('service_name')
    staff = data.get('staff_name')
    date = data.get('date')
    time_slot = data.get('time_slot')
    amount = data.get('amount')

    # Check double booking: same staff, same time
    cursor.execute("""
        SELECT * FROM bookings
        WHERE staff_name=%s AND date=%s AND time_slot=%s
    """, (staff, date, time_slot))
    existing = cursor.fetchone()

    if existing:
        return jsonify({"status": "error", "message": "This staff is already booked for the selected slot."})

    # Insert booking
    cursor.execute("""
        INSERT INTO bookings (customer_name, service_name, staff_name, date, time_slot, amount)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (customer, service, staff, date, time_slot, amount))
    
    # Insert payment
    cursor.execute("""
        INSERT INTO payments (customer_name, service_name, amount)
        VALUES (%s, %s, %s)
    """, (customer, service, amount))

    db.commit()
    return jsonify({"status": "success", "message": "Booking successful!"})
#------PAYMENT -------------
@app.route("/payment")
def payment_page():
    return render_template("payment.html")
#--------PAYMENT SUCCESS---------

@app.route("/payment-success", methods=["POST"])
def payment_success():

    data = request.json

    customer = data["customer"]
    service = data["service"]
    staff = data["staff"]
    time = data["time"]
    payment_id = data["payment_id"]
    amount = data["amount"]

    # Check if staff already booked
    cursor.execute(
        "SELECT * FROM bookings WHERE staff=%s AND time_slot=%s",
        (staff, time)
    )

    existing_booking = cursor.fetchone()

    if existing_booking:
        return {"status":"error","message":"This staff is already booked at this time"}

    # Insert booking if slot available
    cursor.execute(
        "INSERT INTO bookings(customer_name,service,staff,time_slot,payment_id,amount) VALUES(%s,%s,%s,%s,%s,%s)",
        (customer, service, staff, time, payment_id, amount)
    )

    db.commit()

    return {"status":"success"}
#--------BOOKING---------
@app.route("/booking")
def booking():
    return render_template("booking.html")
#---------CREATE ORDER-----------
@app.route("/create_order")
def create_order():

    amount = 20000   # ₹200 booking charge (amount in paise)

    order = razorpay_client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return jsonify(order)
#---------SUCCESS-----------
@app.route("/success")
def success():
    return "Payment Successful! Booking Confirmed."

# GET LOCKED SLOTS
@app.route("/get_slots")
def get_slots():

    conn = get_db()

    slots = conn.execute("SELECT slot FROM bookings").fetchall()

    conn.close()

    booked = [s["slot"] for s in slots]

    return jsonify(booked)


# SAVE BOOKING (PREVENT DOUBLE BOOKING)
@app.route("/save_booking", methods=["POST"])
def save_booking():

    data = request.json

    customer = data["customer"]
    service = data["service"]
    staff = data["staff"]
    slot = data["slot"]
    amount = data["amount"]

    conn = get_db()

    check = conn.execute(
        "SELECT * FROM bookings WHERE slot=?", (slot,)
    ).fetchone()

    if check:
        return jsonify({"status": "taken"})

    conn.execute(
        "INSERT INTO bookings(customer,service,staff,slot,amount) VALUES(?,?,?,?,?)",
        (customer, service, staff, slot, amount)
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

# CUSTOMER HISTORY
@app.route("/history/<name>")
def history(name):

    conn = get_db()

    data = conn.execute(
        "SELECT * FROM bookings WHERE customer=?", (name,)
    ).fetchall()

    conn.close()

    return render_template("history.html", bookings=data, name=name)
# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":

    app.run(debug=True)
