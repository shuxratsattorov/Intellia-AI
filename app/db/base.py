from datetime import datetime
from sqlalchemy import func, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class IDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


    # def __repr__(self):
    #     return f"<{self.__class__.__name__} id={self.id}>"
    # def to_dict(self):
    #     return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    # def to_json(self):
    #     return json.dumps(self.to_dict())
    # def from_json(self, json_data):
    #     for key, value in json_data.items():
    #         setattr(self, key, value)
    # def from_dict(self, dict_data):
    #     for key, value in dict_data.items():
    #         setattr(self, key, value)
    # def from_obj(self, obj):
    #     for key, value in obj.__dict__.items():
    #         setattr(self, key, value)
    # def save(self):
    #     db.session.add(self)
    #     db.session.commit()
    # def delete(self):
    #     db.session.delete(self)
    #     db.session.commit()
    # def commit(self):
    #     db.session.commit()
    # def rollback(self):
    #     db.session.rollback()
    # def close(self):
    #     db.session.close()
    # def refresh(self):
    #     db.session.refresh(self)
    # def expire(self):
    #     db.session.expire(self)
    # def flush(self):
    #     db.session.flush()
    