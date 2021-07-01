import validators
from validators.utils import validator


@validator
def validate_year(y: str) -> bool:
    """Validate y as a valid year

    :param y: the year as a string
    :return: if the year is valid or not
    """
    try:
        y = int(y)
    except ValueError:
        return False

    return validators.between(y, min=2010, max=2050)


@validator
def validate_year_month(ym: str) -> bool:
    """Validate ym as a valid year_month string

    :param ym: the year_month as a string (YYYY_MM format)
    :return: if the year_month is made out of a valid year and month
    """

    try:
        y, m = ym.split("_")
        y = int(y)
        m = int(m)
    except ValueError:
        return False

    return validators.between(y, min=2010, max=2050) and validators.between(m, min=1, max=12)
