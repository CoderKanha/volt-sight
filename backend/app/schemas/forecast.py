from pydantic import BaseModel
from datetime import date
from typing import Optional


class DailyHistoryRecord(BaseModel):
    date: date

    gen_total_mu: Optional[float] = None
    gen_coal_mu: Optional[float] = None
    gen_lignite_mu: Optional[float] = None
    gen_hydro_mu: Optional[float] = None
    gen_nuclear_mu: Optional[float] = None
    gen_gas_mu: Optional[float] = None
    gen_res_mu: Optional[float] = None

    energy_met_total_mu: Optional[float] = None
    solar_gen_total_mu: Optional[float] = None
    wind_gen_total_mu: Optional[float] = None
    ie_actual_total_mu: Optional[float] = None

    freq_fvi: Optional[float] = None
    share_res_pct: Optional[float] = None


class ForecastRequest(BaseModel):
    latest_record: DailyHistoryRecord