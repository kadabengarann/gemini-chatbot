import warnings
import os
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit

warnings.filterwarnings("ignore")
load_dotenv()
DB_URI = os.environ.get('DB_URI')

def connect_to_database(uri):
    try:
        db = SQLDatabase.from_uri(uri)
        print("Database connection successful")
        return db
    except SQLAlchemyError as e:
        print(f"Failed to connect to the database: {e}")
        return None

db = connect_to_database(DB_URI)

def get_toolkit(model):
  if db is None:
      raise RuntimeError("Database connection not available. Cannot create toolkit.")
  toolkit = SQLDatabaseToolkit(db=db, llm=model)
  return toolkit