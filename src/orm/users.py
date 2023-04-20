import enum, typing
from datetime import datetime as datetime_t

from sqlalchemy import BINARY, Boolean, DateTime, ForeignKey, String, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from orm.bases import BaseObject, EnumObject, HistoricalObject
from orm.bases import UUID, UUID_t

# Dummy types. We replace these in other object
# files.
ServiceTicket = typing.NewType("ServiceTicket", object)


# --------------------------------------------- #
# User Objects.
# --------------------------------------------- #
class User(HistoricalObject, BaseObject):
    __tablename__ = "users"

    id:        Mapped[UUID_t] = mapped_column(UUID(), primary_key=True)
    role:      Mapped[str] = mapped_column(ForeignKey("user_role.name"))
    status:    Mapped[str] = mapped_column(ForeignKey("user_status.name"))
    is_active: Mapped[bool] = mapped_column(Boolean())

    # Object relationsips
    user_contacts: Mapped["UserContact"] = relationship\
    (
        back_populates="users",
        cascade="all, delete-orphan"
    )
    user_sessions: Mapped[list["UserSession"]] = relationship\
    (
        back_populates="users",
        cascade="all, delete-orphan"
    )
    service_tickets: Mapped[list["ServiceTicket"]] = relationship\
    (back_populates="users")


class UserRole(EnumObject, BaseObject):
    __tablename__ = "user_role"
    # Kinds:
    # AUTHORIZED
    # ADMINISTRATOR
    # SERVICE


class UserRoleEnum(enum.StrEnum):
    AUTHORIZED = enum.auto()
    ADMINISTRATOR = enum.auto()
    SERVICE = enum.auto()


class UserStatus(EnumObject, BaseObject):
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


class UserSession(HistoricalObject, BaseObject):
    __tablename__ = "user_sessions"

    id:       Mapped[bytes] = mapped_column(BINARY(128), primary_key=True)
    owner_id: Mapped[UUID_t] = mapped_column(ForeignKey("users.id"))
    ipaddress:  Mapped[str] = mapped_column(String(15))

    invalid_on: Mapped[datetime_t] = mapped_column\
    (
        DateTime(False),
        insert_default=func.current_timestamp(),
        default=None
    )

    # Object relationships
    users: Mapped["User"] = relationship(back_populates="user_sessions")


class UserContact(HistoricalObject, BaseObject):
    __tablename__ = "user_contacts"

    owner_id: Mapped[UUID_t] = mapped_column\
    (
        ForeignKey("users.id"),
        primary_key=True
    )
    username: Mapped[str] = mapped_column(String(128))
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64))
    phone_number: Mapped[typing.Optional[str]] = mapped_column(String(10))

    # Object relationships.
    users: Mapped["User"] = relationship(back_populates="user_contacts")
    user_email_addresses: Mapped[list["UserEmail"]] = relationship\
    (back_populates="user_contacts", cascade="all, delete-orphan")


class UserEmail(HistoricalObject, BaseObject):
    __tablename__ = "user_email_addresses"

    id: Mapped[UUID_t] = mapped_column(UUID(), primary_key=True)
    owner_id: Mapped[UUID_t] = mapped_column(ForeignKey("users.id"))
    contact_id: Mapped[UUID_t] = mapped_column\
        (ForeignKey("user_contacts.owner_id"))
    value: Mapped[str] = mapped_column(String(128))

    # Object relationships>
    user_contacts: Mapped["UserContact"] = relationship\
    (back_populates="user_email_addresses")
