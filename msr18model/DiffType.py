from sqlalchemy import Column, ForeignKey, BigInteger, String

from .Base import Base


class DiffType(Base):
    __tablename__ = "diff_type"

    diff_type_id = Column(BigInteger, primary_key=True)
    diff_id = Column(BigInteger, ForeignKey("diff.diff_id"))

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
