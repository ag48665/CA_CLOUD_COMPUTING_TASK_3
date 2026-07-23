from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from config import Config
from extensions import db, bcrypt


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)

from models import User

from models import Route, Booking
from services.ticket_service import TicketService


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not full_name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash(
                "Password must contain at least 8 characters.",
                "danger"
            )
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash(
                "An account with this email already exists.",
                "danger"
            )
            return redirect(url_for("register"))

        password_hash = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash
        )

        db.session.add(user)
        db.session.commit()

        flash(
            "Registration successful. You can now log in.",
            "success"
        )
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        if not bcrypt.check_password_hash(
            user.password_hash,
            password
        ):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session["user_name"] = user.full_name

        flash("Login successful.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        user_name=session["user_name"]
    )


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))
@app.route("/routes")
def routes():
    if "user_id" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    available_routes = Route.query.all()

    return render_template(
        "routes.html",
        routes=available_routes
    )


@app.route("/book/<int:route_id>", methods=["GET", "POST"])
def book_route(route_id):
    if "user_id" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    selected_route = Route.query.get_or_404(route_id)

    if request.method == "POST":
        passenger_name = request.form.get(
            "passenger_name",
            ""
        ).strip()

        if not passenger_name:
            flash("Passenger name is required.", "danger")
            return redirect(
                url_for("book_route", route_id=route_id)
            )

        if selected_route.available_seats <= 0:
            flash("No seats are available.", "danger")
            return redirect(url_for("routes"))

        booking = Booking(
            ticket_number=TicketService.generate_ticket_number(),
            user_id=session["user_id"],
            route_id=selected_route.id,
            passenger_name=passenger_name,
            total_price=selected_route.price
        )

        selected_route.available_seats -= 1

        db.session.add(booking)
        db.session.commit()

        flash("Ticket booked successfully.", "success")

        return redirect(
            url_for("ticket", booking_id=booking.id)
        )

    return render_template(
        "booking.html",
        route=selected_route
    )


@app.route("/ticket/<int:booking_id>")
def ticket(booking_id):
    if "user_id" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != session["user_id"]:
        flash("You cannot view this ticket.", "danger")
        return redirect(url_for("dashboard"))

    return render_template(
        "ticket.html",
        booking=booking
    )


def create_sample_routes():
    if Route.query.count() == 0:
        routes = [
            Route(
                origin="London",
                destination="Manchester",
                departure_time="08:00",
                price=24.99,
                available_seats=40
            ),
            Route(
                origin="London",
                destination="Birmingham",
                departure_time="10:30",
                price=18.50,
                available_seats=35
            ),
            Route(
                origin="Leeds",
                destination="Liverpool",
                departure_time="12:15",
                price=16.75,
                available_seats=30
            ),
            Route(
                origin="Glasgow",
                destination="Edinburgh",
                departure_time="15:00",
                price=12.99,
                available_seats=50
            )
        ]

        db.session.add_all(routes)
        db.session.commit()
@app.route("/my-bookings")
def my_bookings():
    if "user_id" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )



@app.route("/cancel-booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    if "user_id" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != session["user_id"]:
        flash("You cannot cancel this booking.", "danger")
        return redirect(url_for("my_bookings"))

    booking.route.available_seats += 1

    db.session.delete(booking)
    db.session.commit()

    flash("Booking cancelled successfully.", "success")
    return redirect(url_for("my_bookings"))
@app.route("/admin", methods=["GET", "POST"])

def admin():

    if "user_id" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":

        origin = request.form["origin"]
        destination = request.form["destination"]
        departure = request.form["departure"]
        price = float(request.form["price"])
        seats = int(request.form["seats"])

        route = Route(
            origin=origin,
            destination=destination,
            departure_time=departure,
            price=price,
            available_seats=seats
        )

        db.session.add(route)
        db.session.commit()

        flash("Route added successfully.", "success")

        return redirect(url_for("admin"))

    routes = Route.query.all()

    return render_template(
        "admin.html",
        routes=routes
    )
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_sample_routes()

    app.run(debug=True)


