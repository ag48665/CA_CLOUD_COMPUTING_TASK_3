from datetime import datetime
from extensions import db


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(50), unique=True, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    route_id = db.Column(
        db.Integer,
        db.ForeignKey("route.id"),
        nullable=False
    )

    passenger_name = db.Column(db.String(100), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    booking_date = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = db.relationship("User", backref="bookings")
    route = db.relationship("Route", backref="bookings")

    def __repr__(self):
        return f"<Booking {self.ticket_number}>"