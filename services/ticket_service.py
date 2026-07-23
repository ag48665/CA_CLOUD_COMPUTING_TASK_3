import secrets
from datetime import datetime


class TicketService:

    @staticmethod
    def generate_ticket_number():
        random_part = secrets.token_hex(4).upper()
        date_part = datetime.now().strftime("%Y%m%d")

        return f"BUS-{date_part}-{random_part}"