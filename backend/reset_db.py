"""Development helper to reset the database schema.

WARNING: This is destructive — it drops all tables defined by the ORM.
Only run in development and only when you explicitly set `FORCE_RESET_DB=1`.
"""
import os
import sys

from database import engine, Base


def main():
    if os.getenv("FORCE_RESET_DB") != "1":
        print("Refusing to reset DB. Set FORCE_RESET_DB=1 to confirm.")
        sys.exit(1)

    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Reset complete.")


if __name__ == "__main__":
    main()
