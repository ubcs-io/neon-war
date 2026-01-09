import sys
import os

# Add the app directory to the python path
sys.path.insert(0, '/var/www/my_flask_app')

# Activate the virtual environment
# Note: Depending on your mod_wsgi version, activation might be automatic 
# or require specific paths. This is the manual activation method.
activate_this = '/var/www/my_flask_app/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), dict(__file__=activate_this))

from app import app as application