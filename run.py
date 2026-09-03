import os
from app import create_app

if __name__ == '__main__':
    app = create_app()
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5000, debug=debug)
