from sqlalchemy import Column, Integer, String, Boolean

from dfp.DockerInstruction import DockerInstruction
from dfp.model.Base import Base

TRANSFORM_BEFORE = "before"
PARAM_MATCHER = r"(\s\S+)*"


class Patch2(Base):
    __tablename__ = "patch"

    id = Column(Integer, primary_key=True)

    before = Column(String, nullable=False)
    after = Column(String, nullable=False)

    is_combinable = Column(Boolean, nullable=False)

    # Transformations are only for custom patches for now
    # Every param will be transformed with single_transform
    single_transform = Column(String)
    # All parameters will be transformed once with group transform and delimited with group_delimiter if present (else " ")
    group_transform = Column(String)
    group_delimiter = Column(String)

    def transformSingle(self, param: str) -> str:
        if self.single_transform:
            return self.single_transform.replace(TRANSFORM_BEFORE, param)
        else:
            return param

    def transformGroup(self, group: list[str]) -> str:
        if self.group_transform:
            instruction = group[0] if group[0] in DockerInstruction.names() else None
            delim = self.group_delimiter or " "
            if instruction:
                return f"{instruction} {self.group_transform.replace(TRANSFORM_BEFORE, delim.join(group[1:]))}"
            else:
                return self.group_transform.replace(TRANSFORM_BEFORE, delim.join(group))
        else:
            return " ".join(group)

    def __eq__(self, other):
        if isinstance(other, Patch2):
            return other.before == self.before \
                   and other.after == self.after \
                   and other.is_combinable == self.is_combinable \
                   and other.single_transform == self.single_transform \
                   and other.group_transform == self.group_transform
        else:
            return False

    def __hash__(self):
        return hash((self.before,
                     self.after,
                     self.is_combinable,
                     self.single_transform,
                     self.group_transform))
