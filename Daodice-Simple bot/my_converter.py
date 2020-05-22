def int_to_bigint(num):
    return num * (10 ** 18)


def float_value(num):
    num = int(format(num * (10 ** 18), ".0f"))
    return num


def from_hex(num):
    return int(num, 16)


def from_bigint(num):
    if isinstance(num, int):
        return num / (10 ** 18)
    elif isinstance(num, float):
        return num / 10 ** 18
