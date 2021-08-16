from sqlalchemy import Integer, Column, String, BigInteger
from sqlalchemy.orm import relationship

from . import Dockerfile
from .Base import Base


class Project(Base):
    __tablename__ = "project"

    dockerfiles: list[Dockerfile] = relationship("Dockerfile", back_populates="project", lazy="selectin")

    project_id = Column(BigInteger, primary_key=True)

    # .git url
    dotgiturl = Column("git_url", String)
    # https url
    giturl = Column(String)

    created_at = Column(BigInteger)

    repo_id = Column(BigInteger)

    repo_path = Column(String)

    i_forks = Column(Integer)
    i_network_count = Column(Integer)
    i_open_issues = Column(Integer)
    i_owner_type = Column(Integer)
    i_size = Column(Integer)
    i_stargazers = Column(Integer)
    i_subscribers = Column(Integer)
    i_watchers = Column(Integer)
