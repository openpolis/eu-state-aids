import validators


def validate_year(y: str) -> bool:
    """Validate y as a valid year

    :param y: the year as a string
    :return: if the year is valid or not
    """
    try:
        y = int(y)
    except ValueError:
        raise validators.ValidationFailure

    return validators.between(y, min=2010, max=2050)
