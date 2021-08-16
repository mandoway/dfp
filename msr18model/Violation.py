from sqlalchemy import Integer, Column, ForeignKey, BigInteger, String
from sqlalchemy.orm import relationship

from . import Snapshot
from .Base import Base


class Violation(Base):
    __tablename__ = "snap_violation"

    viol_id = Column(BigInteger, primary_key=True)
    snap_id = Column(BigInteger, ForeignKey("snapshot.snap_id"))

    snapshot: Snapshot = relationship("Snapshot", back_populates="violations")

    line = Column(Integer)
    level = Column(String)
    rule = Column(String)

    def __eq__(self, other):
        if isinstance(other, Violation):
            return self.rule == other.rule and self.line == other.line
        return False

    def __hash__(self):
        return hash((self.rule, self.line))
