import sqlalchemy
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm

DB_URL = "sqlite:///./dbfile.db"
engine = sqlalchemy.create_engine(
    DB_URL, connect_args={"check_same_thread": False})

SessionLocal = orm.sessionmaker(autocommit=False, bind=engine)

Base = declarative.declarative_base()
