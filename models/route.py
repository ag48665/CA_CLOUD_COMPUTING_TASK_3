from extensions import db


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False, default=40)

    def __repr__(self):
        return f"<Route {self.origin} to {self.destination}>"