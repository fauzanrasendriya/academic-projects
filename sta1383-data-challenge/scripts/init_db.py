from src.db import get_engine
from src.schema import init_db


def main():
    """Initialize the PostgreSQL database schema."""
    engine = get_engine()
    init_db(engine)
    print("Database initialized successfully.")


if __name__ == "__main__":
    main()
