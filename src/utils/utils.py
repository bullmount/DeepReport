


def get_config_value(value):
    """
    Helper function to handle both string and enum cases of configuration values
    """
    return value if isinstance(value, str) else value.value