import sys
import os

# Add root folder to python path so Vercel finds main.py & services/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app