
from config import DB_ENGINE,DB_HOST,DB_USER,DB_PASSWD,DB_NAME
from lib.database import Database

db = Database({'db':DB_NAME,'engine':DB_ENGINE})