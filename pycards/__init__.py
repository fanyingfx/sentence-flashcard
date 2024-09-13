# from .app import app as myapp
# from .models import init_db

# __all__ = ["myapp"]

# if __name__ == '__main__':
#     print("Initializing database...")
#     init_db()
#     print("Database initialized.")
#     myapp.run(debug=True)

from .app import app ,main

__all__ = ["app","main"]

# def main():
#     print("Initializing database...")
#     init_db()
#     print("Database initialized.")
#     myapp.run(debug=True)

if __name__ == '__main__':
    main()