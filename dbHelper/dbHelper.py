import configparser
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from utils.utility import getPathFromRoot


def initSessionMaker(config_section: str) -> sessionmaker:
    return _initSessionMaker(config_section)


def _initSessionMaker(config_section: str = "msr18") -> sessionmaker:
    """
    Starts db connection to msr18 db

    :return: sessionmaker bound to current db
    """
    config = configparser.ConfigParser()
    config.read(getPathFromRoot("config.ini"))
    dbconfig = config[config_section]

    engine = sqlalchemy.create_engine(
        f"postgresql://{dbconfig['username']}:{dbconfig['password']}@{dbconfig['host']}/{dbconfig['db']}")

    return sessionmaker(bind=engine, autoflush=True)


Sessionmaker = _initSessionMaker()
