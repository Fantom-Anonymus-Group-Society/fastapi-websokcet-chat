import databases
import ormar
import sqlalchemy

from app.configs.environment import env

database: databases.Database = databases.Database(env.db_url)
metadata: sqlalchemy.MetaData = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    metadata: sqlalchemy.MetaData = metadata
    database: databases.Database = database
