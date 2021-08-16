from sqlalchemy import Column, BigInteger, String

from .Base import Base


class FixChange(Base):
    """
    Same data as DiffType, but can't reuse the class due to the missing FK relation here
    Represents a view with the given tablename in the Database
    These changes (diffType's) contain only fixing changes (at least one violation was deleted)
    The changes are filtered from moved changes, where the line was only moved but not modified in any way
    """
    __tablename__ = "fixes_without_moved"

    diff_type_id = Column(BigInteger, primary_key=True)
    diff_id = Column(BigInteger)

    before = Column(String(255))
    after = Column(String(255))
    change_type = Column(String(255))
    executable = Column(String(255))
    instruction = Column(String(255))

    @property
    def beforeFull(self):
        return self._fullCmd(self.before)

    @property
    def afterFull(self):
        return self._fullCmd(self.after)

    def _fullCmd(self, params):
        return f"{self.instruction} {self.executable + ' ' if self.executable is str else ''}{params or ''}"

    def __eq__(self, other):
        if isinstance(other, FixChange):
            return other.before == self.before \
                   and other.after == self.after \
                   and other.change_type == self.change_type \
                   and other.executable == self.executable \
                   and other.instruction == self.instruction
        else:
            return False

    def __hash__(self):
        return hash((self.before, self.after, self.change_type, self.executable, self.instruction))
