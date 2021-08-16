from sqlalchemy import Integer, Column, ForeignKey, Boolean, BigInteger, String
from sqlalchemy.orm import relationship

from . import Dockerfile, Violation, Diff
from .Base import Base
from .util import snapdiff_table


class Snapshot(Base):
    __tablename__ = "snapshot"

    snap_id = Column(BigInteger, primary_key=True)
    dock_id = Column(BigInteger, ForeignKey("dockerfile.dock_id"))
    dockerfile: Dockerfile = relationship("Dockerfile", back_populates="snapshots", lazy="joined")

    violations: list[Violation] = relationship("Violation", back_populates="snapshot", lazy="selectin")

    diffs: list[Diff] = relationship("Diff", secondary=snapdiff_table, back_populates="snapshots", lazy="selectin")

    repo_id = Column(BigInteger)
    instructions = Column(Integer)
    commit_date = Column(BigInteger)
    from_date = Column(BigInteger)
    to_date = Column(BigInteger)
    change_type = Column(String)
    del_ = Column("del", Integer)
    ins = Column(Integer)
    image_is_automated = Column(Boolean)
    image_is_official = Column("image_is_offical", Boolean)
    star_count = Column(Integer)
    commit_index = Column(Integer)
    current = Column(Boolean)
