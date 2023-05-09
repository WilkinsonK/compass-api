import dataclasses 
import typing

import common, models, orm


def consume_orm_object(obj: orm.bases.BaseObject):
    """
    Breaks down an ORM object into a python
    mapping.
    """

    return dataclasses.asdict(obj)


def consume_pyd_object(
        obj: models.bases.CompassModel | typing.Any,
        *,
        blacklist: typing.Iterable[str] | None = None) -> dict[str, typing.Any]:
    """
    Breaks down a Pydantic model object into a
    python mapping.
    """

    obj = obj.dict()
    for name, value in obj.items():
        if isinstance(value, models.bases.CompassModel):
            obj[name] = consume_pyd_object(value)
    return common.sanitize_dict(obj, blacklist or [])


def consume_orm2pyd(
        obj: orm.bases.BaseObject,
        pyd_cls: type[models.bases.CompassModel]):
    """Digests some ORM into a model instance."""

    return pyd_cls(**consume_orm_object(obj))


def consume_pyd2orm(
        obj: models.bases.CompassModel,
        orm_cls: type[orm.bases.BaseObject]):
    """
    Digests some model into an ORM instance.
    """

    return orm_cls(**consume_pyd_object(obj))


def consume_user2orm(user: models.users.UserM):
    """Consume some User model into User ORM."""

    user = consume_pyd_object(user)
    user["user_contacts"] = orm.users.UserContact(**user["user_contacts"])

    # Iter through sessions and ensure all are
    # consumed into ORM objects.
    for idx, session in enumerate(user["user_sessions"]):
        user["user_sessions"][idx] = orm.users.UserSession(**session)

    # Iter through service_tickets and do the
    # same as sessions.
    for idx, ticket in enumerate(user["service_tickets"]):
        user["service_tickets"][idx] = orm.tickets.ServiceTicket(**ticket)

    return orm.users.User(**user)


def consume_user2pyd(user: orm.users.User):
    """Consume some User ORM into User model."""

    return models.users.UserM(**consume_orm_object(user))
