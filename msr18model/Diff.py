from sqlalchemy import Integer, Column, BigInteger, String
from sqlalchemy.orm import relationship

from . import DiffType, Snapshot
from .util import snapdiff_table
from .Base import Base


class Diff(Base):
    __tablename__ = "diff"

    diff_id = Column(BigInteger, primary_key=True)

    snapshots: list[Snapshot] = relationship("Snapshot", secondary=snapdiff_table, back_populates="diffs")

    diff_items: list[DiffType] = relationship("DiffType")

    commit_date = Column(BigInteger)
    deleted = Column("del", Integer)
    inserts = Column("ins", Integer)
    modified = Column("mod", Integer)
    diff_state = Column(String(255))
