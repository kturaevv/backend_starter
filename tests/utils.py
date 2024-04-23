import uuid


def generate_database_name() -> str:
    """Generate a unique database name."""
    return f"test_db_{uuid.uuid4()}".replace("-", "_")
