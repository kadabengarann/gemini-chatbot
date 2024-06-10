from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit

DB_URI = "mysql://uj1qnl4rlq8uzsk2:k8BXQj9UHy2OnC8B4GKy@botkgkqmgyoiovycsvln-mysql.services.clever-cloud.com:3306/botkgkqmgyoiovycsvln"

db = SQLDatabase.from_uri(DB_URI)

def get_toolkit(model):
  toolkit = SQLDatabaseToolkit(db=db,llm=model)
  return toolkit