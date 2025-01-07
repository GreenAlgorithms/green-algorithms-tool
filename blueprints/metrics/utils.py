def format_energy_text(energy_needed: float):
    """
    Adapt the value and unit of the energy based on the raw value.
    Args:
        energy_needed (float): in kWh.
    """
    energyNeeded_unit = "kWh"
    if energy_needed >= 1e3:
        energy_needed /= 1e3
        energyNeeded_unit = "MWh"
    elif energy_needed < 1:
        energy_needed *= 1e3
        energyNeeded_unit = "Wh"
    if (energy_needed != 0) & ((energy_needed >= 1e3) | (energy_needed < 1)):
        text_energy = f"{energy_needed:,.2e} {energyNeeded_unit}"
    else:
        text_energy = f"{energy_needed:,.2f} {energyNeeded_unit}"
    return text_energy

def format_CE_text(carbon_emissions: float):
    """
    Adapt the value and unit of the carbon emissions based on the raw value.
    Args:
        carbon_emissions (float): in g CO2e
    """
    carbonEmissions_unit = "g"
    if carbon_emissions >= 1e6:
        carbon_emissions /= 1e6
        carbonEmissions_unit = "T"
    elif carbon_emissions >= 1e3:
        carbon_emissions /= 1e3
        carbonEmissions_unit = "kg"
    elif carbon_emissions < 1:
        carbon_emissions *= 1e3
        carbonEmissions_unit = "mg"
    if (carbon_emissions != 0)&((carbon_emissions >= 1e3)|(carbon_emissions < 1)):
        text_CE = f"{carbon_emissions:,.2e} {carbonEmissions_unit}CO2e"
    else:
        text_CE = f"{carbon_emissions:,.2f} {carbonEmissions_unit}CO2e"
    return text_CE

def write_tree_months_equivalent(carbon_emissions: float, ref_values: dict):
    """
    Compute the tree-month equivalent and format unit along with value.
    Args:
        carbon_emissions (float): in g CO2e
        ref_values (dict): a versioned dictionary containing ref values for equivalents
    """
    treeTime_value = carbon_emissions / ref_values['treeYear'] * 12   # in tree-months
    treeTime_unit = "tree-months"
    if treeTime_value >= 24:
        treeTime_value /= 12
        treeTime_unit = "tree-years"
    if (treeTime_value != 0) & ((treeTime_value >= 1e3) | (treeTime_value < 0.1)):
        text_ty = f"{treeTime_value:,.2e} {treeTime_unit}"
    else:
        text_ty = f"{treeTime_value:,.2f} {treeTime_unit}"
    return text_ty

def write_driving_equivalent(carbon_emissions: float, ref_values: dict):
    """
    Compute the driving equivalent and format unit along with value.
    Args:
        carbon_emissions (float): in g CO2e
        ref_values (dict): a versioned dictionary containing ref values for equivalents
    """
    nkm_drivingEU = carbon_emissions / ref_values['passengerCar_EU_perkm']  # in km
    if (nkm_drivingEU != 0) & ((nkm_drivingEU >= 1e3) | (nkm_drivingEU < 0.1)):
        text_car = f"{nkm_drivingEU:,.2e} km"
    else:
        text_car = f"{nkm_drivingEU:,.2f} km"
    return text_car

def write_plane_trip_equivalent(carbon_emissions: float, ref_values: dict):
    """
    Pick the most appropriate plane trip and compute the proportion
    of it giving equivalent emissions to the input one.
    Args:
        carbon_emissions (float): in g CO2e
        ref_values (dict): a versioned dictionary containing ref values for equivalents
    """
    if carbon_emissions < 0.5 * ref_values['flight_NY-SF']:
        trip_proportion = carbon_emissions / ref_values['flight_PAR-DUB']
        flying_label = "Paris-Dublin"
    elif carbon_emissions < 0.5 * ref_values['flight_NYC-MEL']:
        trip_proportion = carbon_emissions / ref_values['flight_NY-SF']
        flying_label = "NYC-San Francisco"
    else:
        trip_proportion = carbon_emissions / ref_values['flight_NYC-MEL']
        flying_label = "NYC-Melbourne"
    if trip_proportion == 0:
        text_trip_proportion = "0"
    elif trip_proportion > 1e6:
        text_trip_proportion = f"{trip_proportion:,.0e}"
    elif trip_proportion >= 1:
        text_trip_proportion = f"{trip_proportion:,.1f}"
    elif trip_proportion >= 0.01:
        text_trip_proportion = f"{trip_proportion:,.0%}"
    elif trip_proportion >= 1e-4:
        text_trip_proportion = f"{trip_proportion:,.2%}"
    else:
        text_trip_proportion = f"{trip_proportion*100:,.0e} %"
    if (trip_proportion >= 1) | (trip_proportion == 0):
        flying_text = f"flights {flying_label}"
    else:
        flying_text = f"of a flight {flying_label}"
    return text_trip_proportion, flying_text

    
    