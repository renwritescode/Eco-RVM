import os
import sys

# Add the project root to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app import create_app

app = create_app()

# Vercel needs this for serverless function
if __name__ == '__main__':
    app.run()
