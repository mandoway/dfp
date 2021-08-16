import enum

from sqlalchemy import Integer, Column, ForeignKey, BigInteger, String, Enum
from sqlalchemy.orm import relationship

from . import SnapViolationDiff
from .Base import Base


class DiffItemType(enum.Enum):
    ADD = "ADD"
    DEL = "DEL"
    MOV = "MOV"


class SnapViolDiffItem(Base):
    __tablename__ = "snap_viol_diff_item"

    item_id = Column(BigInteger, primary_key=True)
    diff_id = Column(BigInteger, ForeignKey("snap_viol_diff.diff_id"))

    diff: SnapViolationDiff = relationship("SnapViolationDiff", back_populates="diff_items")

    type = Column(Enum(DiffItemType))
    old_line = Column(Integer)
    new_line = Column(Integer)
    rule = Column(String)

    def __eq__(self, other):
        if isinstance(other, SnapViolDiffItem):
            return other.type == self.type \
                   and other.old_line == self.old_line \
                   and other.new_line == self.new_line \
                   and other.rule == self.rule
        return False

    def __hash__(self):
        return hash((self.type, self.old_line, self.new_line, self.rule))
