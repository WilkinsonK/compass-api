import enum
from datetime import datetime as datetime_t

from sqlalchemy import BINARY, Boolean, DateTime, ForeignKey, String

from models.bases import ORMBase
from models.orm.bases import mapped_column, relationship
from models.orm.bases import EnumMixIn, HistoricalMixIn, IdMixIn
from models.orm.bases import UserOwnerMixIn, MappedUUID, MappedStr, Mapped


# --------------------------------------------- #
# User Objects.
# --------------------------------------------- #
class UserRole(EnumMixIn, ORMBase):
    __tablename__ = "user_role"
    # Kinds:
    # AUTHORIZED
    # ADMINISTRATOR
    # SERVICE


class UserRoleEnum(enum.StrEnum):
    AUTHORIZED = enum.auto()
    ADMINISTRATOR = enum.auto()
    SERVICE = enum.auto()


class UserStatus(EnumMixIn, ORMBase):
    __tablename__ = "user_status"
    # Kinds:
    # DISABLED
    # UNVERIFIED
    # BLOCKED
    # ENABLED


class UserStatusEnum(enum.StrEnum):
    DISABLED = enum.auto()
    UNVERIFIED = enum.auto()
    BLOCKED = enum.auto()
    ENABLED = enum.auto()


class UserSession(HistoricalMixIn, UserOwnerMixIn, ORMBase):
    __tablename__ = "user_sessions"

    id: Mapped[bytes] = mapped_column("id", BINARY(128), primary_key=True)
    ipaddress: MappedStr = mapped_column("ipaddress", String(15))
    invalid_on: Mapped[datetime_t] = mapped_column\
    (
        "invalid_on",
        DateTime(False)
    )


class UserEmail(ORMBase, IdMixIn, HistoricalMixIn):
    __tablename__ = "user_email_addresses"

    is_primary: Mapped[bool] = mapped_column("is_primary", Boolean(), default=False, primary_key=True)
    owner_id: MappedUUID = mapped_column("owner_id", ForeignKey("users.id"))
    contact_id: MappedUUID = mapped_column("contact_id", ForeignKey("user_contacts.owner_id"))
    value: MappedStr = mapped_column("value", String(128))

    # Object relationships
    user_contacts: Mapped["UserContact"] = relationship( #type: ignore
        "UserContact",
        back_populates=__tablename__
    )


class UserContact(ORMBase, UserOwnerMixIn, HistoricalMixIn):
    __tablename__ = "user_contacts"

    owner_id: MappedUUID = mapped_column\
    (
        "owner_id",
        ForeignKey("users.id"),
        primary_key=True
    )
    username: MappedStr = mapped_column("username", String(128))
    first_name: MappedStr = mapped_column("first_name", String(64))
    last_name: MappedStr = mapped_column("last_name", String(64))
    phone_number: MappedStr = mapped_column("phone_number", String(10))

    # Object relationships.
    user_email_addresses: Mapped[list["UserEmail"]] = relationship\
    (
        UserEmail,
        collection_class=list,
        back_populates=__tablename__,
        cascade="all, delete-orphan"
    )
    

class User(ORMBase, IdMixIn, HistoricalMixIn):
    __tablename__ = "users"

    role: Mapped["UserRole"] = mapped_column(ForeignKey("user_role.name"))
    status: Mapped["UserStatus"] = mapped_column("status", ForeignKey("user_status.name"))
    is_active: Mapped[bool] = mapped_column("is_active", Boolean())
    hashed_password: Mapped[bytes] = mapped_column("hashed_password", BINARY(512))

    # Object relationsips
    user_contacts: Mapped["UserContact"] = relationship\
    (
        "UserContact",
        back_populates=__tablename__,
        cascade="all, delete-orphan"
    )

    user_sessions: Mapped[list["UserSession"]] = relationship\
    (
        UserSession,
        collection_class=list,
        back_populates=__tablename__,
        cascade="all, delete-orphan"
    )

    service_tickets: Mapped[list["ServiceTicket"]] = relationship( #type: ignore
        "ServiceTicket",
        collection_class=list,
        back_populates="users"
    )
