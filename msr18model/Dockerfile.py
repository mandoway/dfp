from sqlalchemy import Integer, Column, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from . import Project, Snapshot
from .Base import Base


class Dockerfile(Base):
    __tablename__ = "dockerfile"

    dock_id = Column(BigInteger, primary_key=True)
    project_id = Column("project_project_id", BigInteger, ForeignKey("project.project_id"))
    project: Project = relationship("Project", back_populates="dockerfiles", lazy="selectin")

    snapshots: list[Snapshot] = relationship("Snapshot", back_populates="dockerfile", lazy="selectin")

    repo_id = Column(BigInteger)
    commits = Column(Integer)
    docker_path = Column(String)
    created_at = Column(BigInteger)
    first_docker_commit = Column(Integer)

    @property
    def repoDockerPath(self):
        index = self.docker_path.find("/")
        index = self.docker_path.find("/", index+1)
        return self.docker_path[index+1:]

    @property
    def filename(self):
        index = self.docker_path.rfind("/")
        return self.docker_path[index+1:]
