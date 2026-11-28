from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class RawHistoryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    records: list[dict[str, Any]] = Field(min_length=1)

class ShortageInput(BaseModel):
    demand_mw: float = Field(gt=0)
    available_supply_before_outages_mw: float = Field(ge=0)

class OutageForecastRequest(RawHistoryRequest):
    # Keys: all_india, nr, wr, sr, er, ner
    shortage_inputs: dict[str, ShortageInput] | None = None

class FrequencyForecastRequest(RawHistoryRequest):
    pass

class DatabaseOutageRequest(BaseModel):
    shortage_inputs: dict[str, ShortageInput] | None = None
