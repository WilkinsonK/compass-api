from models.bases import HistoricalModel, VarCharField, UUIDField, \
    DateTimeField, UUIDField
from models.tickets import ServiceTicketM
from orm.users import UserRoleEnum, UserStatusEnum


class UserM(HistoricalModel):
    id: UUIDField
    role: UserRoleEnum
    status: UserStatusEnum
    is_active: bool
    hashed_password: bytes
    user_contacts: "UserContactM"
    user_sessions: list["UserSessionM"]
    service_tickets: list["ServiceTicketM"]


class UserSessionM(HistoricalModel):
    id: VarCharField(bytes, 128)
    owner_id: UUIDField
    ipaddress: VarCharField(str, 15)
    invalid_on: DateTimeField


class UserContactM(HistoricalModel):
    owner_id: UUIDField
    user_email_addresses: list["UserEmailM"]
    username: VarCharField(str, 128)
    first_name: VarCharField(str, 64)
    last_name: VarCharField(str, 64)
    phone_number: VarCharField(str, 10)


class UserEmailM(HistoricalModel):
    id: UUIDField
    owner_id: UUIDField
    contact_id: UUIDField
    user_contacts: UserContactM
    value: VarCharField(str, 128)


UserM.update_forward_refs()
UserContactM.update_forward_refs()

if __name__ == "__main__":
    import dataclasses, hashlib, pprint, uuid
    import orm

    ADMIN_UUID = uuid.uuid4()
    ADMIN_USERNAME = "compass-admin"
    ADMIN_HASHED_PASSWORD = hashlib.sha1(b"HumpDay", usedforsecurity=True).digest()

    orm_user_contact = orm.users.UserContact\
    (
        owner_id=ADMIN_UUID,
        username=ADMIN_USERNAME,
        first_name="",
        last_name="",
        phone_number="",
        user_email_addresses=[],
        created_at=DateTimeField.now(),
        updated_on=DateTimeField.now(),
    )

    orm_user = orm.users.User\
    (
        id=ADMIN_UUID,
        role="administrator",
        status="enabled",
        is_active=True,
        hashed_password=ADMIN_HASHED_PASSWORD,
        user_contacts=orm_user_contact,
        user_sessions=[],
        service_tickets=[],
        created_at=DateTimeField.now(),
        updated_on=DateTimeField.now()
    )

    pyd_user = UserM(**dataclasses.asdict(orm_user))
    pprint.pp(pyd_user)

    orm_user = pyd_user.dict()
    orm_user["user_contacts"] = orm.users.UserContact(**orm_user["user_contacts"])
    orm_user = orm.users.User(**orm_user)
    pprint.pp(orm_user)
