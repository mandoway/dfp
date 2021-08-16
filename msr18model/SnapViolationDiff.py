from sqlalchemy import Integer, Column, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm import relationship

from . import Snapshot, SnapViolDiffItem
from .Base import Base


class SnapViolationDiff(Base):
    __tablename__ = "snap_viol_diff"

    diff_id = Column(BigInteger, primary_key=True)
    old_snap_id = Column(BigInteger, ForeignKey("snapshot.snap_id"))
    new_snap_id = Column(BigInteger, ForeignKey("snapshot.snap_id"))

    old_snapshot: Snapshot = relationship("Snapshot", foreign_keys=[old_snap_id], lazy="joined")
    new_snapshot: Snapshot = relationship("Snapshot", foreign_keys=[new_snap_id], lazy="joined")

    added = Column(Integer)
    removed = Column(Integer)
    moved = Column(Integer)

    # A diff is only valid when there is no syntax error violation, i.e. no violation with rule "unexpected"
    valid = Column(Boolean)

    diff_items: list[SnapViolDiffItem] = relationship("SnapViolDiffItem", back_populates="diff")
