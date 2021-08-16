from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from . import Project, Snapshot, SnapViolationDiff, Diff
from .Base import Base


class MapDiff(Base):
    __tablename__ = "map_diff"

    map_id = Column(BigInteger, primary_key=True)

    project_id = Column(BigInteger, ForeignKey("project.project_id"))
    old_snap_id = Column(BigInteger, ForeignKey("snapshot.snap_id"))
    new_snap_id = Column(BigInteger, ForeignKey("snapshot.snap_id"))
    diff_id = Column(BigInteger, ForeignKey("diff.diff_id"))
    viol_diff_id = Column(BigInteger, ForeignKey("snap_viol_diff.diff_id"))

    project: Project = relationship("Project")
    old_snap: Snapshot = relationship("Snapshot", foreign_keys=[old_snap_id])
    new_snap: Snapshot = relationship("Snapshot", foreign_keys=[new_snap_id])
    diff: Diff = relationship("Diff")
    viol_diff: SnapViolationDiff = relationship("SnapViolationDiff")
