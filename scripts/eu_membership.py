"""EU membership by survey year, for correctly-scoped country rankings over time."""

EU15 = ["AT", "BE", "DE", "DK", "ES", "FI", "FR", "EL", "IE", "IT", "LU", "NL", "PT", "SE", "UK"]
EU_2004_ACCESSION = ["CY", "CZ", "EE", "HU", "LT", "LV", "MT", "PL", "SK", "SI"]
EU25 = EU15 + EU_2004_ACCESSION
EU_2007_ACCESSION = ["BG", "RO"]
EU27_PRE_HR = EU25 + EU_2007_ACCESSION
EU_2013_ACCESSION = ["HR"]
EU28 = EU27_PRE_HR + EU_2013_ACCESSION
EU27_2020 = [c for c in EU28 if c != "UK"]


def eu_members(year: int) -> list[str]:
    """Return the list of EU member geo codes as of the given EU-SILC survey year."""
    if year < 2004:
        return EU15
    if year < 2007:
        return EU25
    if year < 2013:
        return EU27_PRE_HR
    if year < 2020:
        return EU28
    return EU27_2020


def composition_label(year: int) -> str:
    if year < 2004:
        return "EU15"
    if year < 2007:
        return "EU25"
    if year < 2013:
        return "EU27 (pre-Croatia)"
    if year < 2020:
        return "EU28"
    return "EU27 (post-Brexit)"
