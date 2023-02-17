def make_list(val: str):
    val = ','.join(val.splitlines())
    val = ','.join(val.split(';'))
    val = ''.join(val.split(' '))
    return [x for x in val.split(',') if len(x) > 0]