"""
WSGI Entry Point for Production Deployment.
Compatible with Gunicorn, uWSGI, Waitress, and other WSGI application servers.
Example:
    gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
