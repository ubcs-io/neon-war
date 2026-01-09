import sys
import os

# Add the app directory to the python path
sys.path.insert(0, '/var/www/neon_war')

# Activate the virtual environment
# Note: Depending on your mod_wsgi version, activation might be automatic 
# or require specific paths. This is the manual activation method.
activate_game = '/var/www/neon_war/venv/bin/activate.py'
if os.path.exists(activate_game):
    with open(activate_game) as f:
        exec(f.read(), dict(__file__=activate_game))

from app import app as application