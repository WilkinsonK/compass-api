import pydantic
import sqlalchemy.orm


class ORMBase(sqlalchemy.orm.MappedAsDataclass, sqlalchemy.orm.DeclarativeBase):
    """
    Base ORM representation of objects in the
    Compass environment.
    """

    def __repr__(self):
        fields = self.__annotations__.keys()
        fields = " ".join([f"{f}={getattr(self, f)}" for f in fields])
        return f"{self.__class__.__name__}[{fields}]"


class PYDBase(pydantic.BaseModel):
    """
    Base representation of objects in the Compass
    environment as a `Pydantic` model.
    """

    class Config(pydantic.BaseConfig):
        orm_mode = True
        use_enum_values = True
