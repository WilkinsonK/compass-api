from models.bases import HistoricalModel, VarCharField, UUIDField


class MessageM(HistoricalModel):
    id: UUIDField
    ticket_id: UUIDField
    owner_id: UUIDField
    content: VarCharField(str, 512)
