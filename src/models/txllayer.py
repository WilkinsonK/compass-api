import dataclasses, typing

import common
from models import bases, orm, pyd

MTo = typing.TypeVar("MTo", bound=bases.ORMBase)
MTp = typing.TypeVar("MTp", bound=bases.PYDBase)

MToTxL = typing.Callable[[MTo], MTp]
MTpTxL = typing.Callable[[MTp], MTo]

orm2pyd_mapping: dict[bases.ORMBase, MToTxL] = {}
pyd2pyd_mapping: dict[bases.PYDBase, MTpTxL] = {}


@typing.overload
def translate(mt: MTo) -> bases.PYDBase:
    ...


@typing.overload
def translate(mt: MTp) -> bases.ORMBase:
    ...


def translate(mt: MTo | MTp) -> MTp | MTo:
    """
    From the given ORM or Pydantic model, get the
    registered callable and do the translation
    from `ORM to Pydantic` or `Pydantic to ORM`.
    """

    fn = retrieve_txl(mt)
    return fn(mt)


@typing.overload
def retrieve_txl(mt: MTo) -> MTpTxL:
    ...


@typing.overload
def retrieve_txl(mt: MTp) -> MToTxL:
    ...


def retrieve_txl(mt: MTo | MTp) -> MTpTxL | MToTxL:
    """
    Aquires the registered callable used to
    translate that type to the corresponding
    model type.
    """

    if isinstance(mt, bases.ORMBase):
        target_mapping = orm2pyd_mapping
    else:
        target_mapping = pyd2pyd_mapping #type: ignore[assignment]

    return target_mapping[mt] #type: ignore[index]


@typing.overload
def register_txl(mt: type[MTo]) -> MToTxL:
    ...


@typing.overload
def register_txl(mt: type[MTp]) -> MTpTxL:
    ...


def register_txl(mt: type[MTo | MTp]) -> MToTxL | MTpTxL:
    """
    Registers the wrapped function as a callable
    which translates the given instance into its
    corresponding model object.
    """

    if issubclass(mt, bases.ORMBase):
        target_mapping = orm2pyd_mapping
    else:
        target_mapping = pyd2pyd_mapping #type: ignore[assignment]

    def wrapper(fn: MToTxL | MTpTxL):
        target_mapping[mt] = fn #type: ignore[index]
        return fn
    
    return wrapper


def consume_orm_object(obj: bases.ORMBase):
    """
    Breaks down an ORM object into a python
    mapping.
    """

    return dataclasses.asdict(obj)


def consume_pyd_object(
        obj: bases.PYDBase | typing.Any,
        *,
        blacklist: typing.Iterable[str] | None = None) -> dict[str, typing.Any]:
    """
    Breaks down a Pydantic model object into a
    python mapping.
    """

    obj = obj.dict()
    for name, value in obj.items():
        if isinstance(value, bases.PYDBase):
            obj[name] = consume_pyd_object(value)
    return common.sanitize_dict(obj, blacklist or [])


def consume_orm2pyd(obj: bases.ORMBase, pyd_cls: type[bases.PYDBase]):
    """Digests some ORM into a model instance."""

    return pyd_cls(**consume_orm_object(obj))


def consume_pyd2orm(obj: bases.PYDBase, orm_cls: type[bases.ORMBase]):
    """
    Digests some model into an ORM instance.
    """

    return orm_cls(**consume_pyd_object(obj))


@register_txl(pyd.users.UserM)
def user2orm(obj: pyd.users.UserM):
    """Consume some User model into User ORM."""

    user = consume_pyd_object(obj)
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


@register_txl(orm.users.User)
def user2pyd(obj: orm.users.User):
    """Consume some User ORM into User model."""

    return pyd.users.UserM(**consume_orm_object(obj))
