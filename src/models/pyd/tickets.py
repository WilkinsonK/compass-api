from models.pyd.bases import HistoricalModel, VarCharField, UUIDField
from models.orm.tickets import TicketKindEnum, TicketStatusEnum


class ServiceTicketM(HistoricalModel):
    id: UUIDField
    owner_id: UUIDField
    short_description: VarCharField(str, 64) #type: ignore[valid-type]
    long_description: VarCharField(str, 512) #type: ignore[valid-type]
    kind: TicketKindEnum
    status: TicketStatusEnum
