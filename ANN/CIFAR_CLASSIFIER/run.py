import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "127.0.0.1")
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")

    print("\n" + "=" * 60)
    print("  CIFAR-10 Neural Classifier Web Application")
    print(f"  Running locally on: http://{host}:{port}")
    print("=" * 60 + "\n")

    app.run(host=host, port=port, debug=debug)
