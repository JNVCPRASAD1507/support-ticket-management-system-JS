
import uuid


def generate_ticket_number() -> str:
    return f"TKT-{uuid.uuid4().hex[:10].upper()}"

