from flask_login import LoginManager
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Initialize Supabase Client
url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY") or os.environ.get("ANNON_KEY", "")

# Create client globally (this is thread-safe for reading mainly)
# For writing, it handles requests via HTTP
supabase: Client = create_client(url, key)
