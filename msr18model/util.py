from sqlalchemy import Column, ForeignKey, BigInteger, Table
from .Base import Base

snapdiff_table = Table("snap_diff", Base.metadata,
                       Column("snap_id", BigInteger, ForeignKey("snapshot.snap_id")),
                       Column("diff_id", BigInteger, ForeignKey("diff.diff_id"))
                       )
