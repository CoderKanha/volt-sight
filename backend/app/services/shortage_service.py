def calculate_shortage(
    demand_mw: float,
    available_supply_before_outages_mw: float,
    predicted_outage_mw: float,
) -> dict:
    """Estimate unmet demand after subtracting predicted forced outages.

    available_supply_before_outages_mw MUST be a supply estimate before
    subtracting this predicted outage. Do not pass supply already net of outage.
    """
    if demand_mw <= 0:
        raise ValueError("demand_mw must be greater than zero.")
    if available_supply_before_outages_mw < 0 or predicted_outage_mw < 0:
        raise ValueError("Supply and predicted outage must be non-negative.")

    adjusted_supply = max(
        available_supply_before_outages_mw - predicted_outage_mw, 0.0
    )
    shortage_mw = max(demand_mw - adjusted_supply, 0.0)
    return {
        "demand_mw": float(demand_mw),
        "available_supply_before_outages_mw": float(available_supply_before_outages_mw),
        "predicted_outage_mw": float(predicted_outage_mw),
        "estimated_supply_after_outages_mw": float(adjusted_supply),
        "shortage_mw": float(shortage_mw),
        "shortage_percentage": float(shortage_mw / demand_mw * 100.0),
        "outage_burden_percentage_of_demand": float(predicted_outage_mw / demand_mw * 100.0),
    }
