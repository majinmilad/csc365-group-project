import os
import dotenv
import sqlalchemy
from sqlalchemy import create_engine

def database_connection_url():
    dotenv.load_dotenv()
    return os.environ.get("POSTGRES_URI")

DATABASE_URL = "postgresql://postgres.nqueeijmuxlkmckrcxst:weresocookedbro@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
engine = create_engine(database_connection_url(), pool_pre_ping=True)

metadata_obj = sqlalchemy.MetaData()