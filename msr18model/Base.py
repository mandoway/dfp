from sqlalchemy.ext.declarative import declarative_base


class Base(declarative_base()):
    __abstract__ = True

    def __repr__(self) -> str:
        return str(self.__dict__)
