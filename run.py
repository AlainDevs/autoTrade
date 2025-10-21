# File: run.py

from src import create_app

app = create_app()

if __name__ == "__main__":
    # For production, it's highly recommended to use a WSGI server like Gunicorn instead of app.run()
    # Example: poetry run gunicorn --bind 0.0.0.0:28791 "run:app"
    app.run(host='0.0.0.0', port=28791)