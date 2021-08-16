from .Base import Base
from sqlalchemy import Column, BigInteger, String


class FailedProjects(Base):
    __tablename__ = "failed_projects"

    project_id = Column(BigInteger, primary_key=True)
    project_name = Column(String)
