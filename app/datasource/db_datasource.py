import warnings
from sqlalchemy.exc import SQLAlchemyError
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit

warnings.filterwarnings("ignore")

DB_URI = "mysql://uj1qnl4rlq8uzsk2:k8BXQj9UHy2OnC8B4GKy@botkgkqmgyoiovycsvln-mysql.services.clever-cloud.com:3306/botkgkqmgyoiovycsvln"

try:
  db = SQLDatabase.from_uri(DB_URI)
  print("Database connection successful")
except SQLAlchemyError as e:
  print(f"Failed to connect to the database: {e}")
  db = None

def get_toolkit(model):
  if db is None:
      raise RuntimeError("Database connection not available. Cannot create toolkit.")
  toolkit = SQLDatabaseToolkit(db=db, llm=model)
  return toolkit