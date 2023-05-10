from models.pyd.bases import HistoricalModel, VarCharField, UUIDField


class MessageM(HistoricalModel):
    id: UUIDField
    ticket_id: UUIDField
    owner_id: UUIDField
    content: VarCharField(str, 512) #type: ignore[valid-type]
