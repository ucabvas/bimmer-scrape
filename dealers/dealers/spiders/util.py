def parse_msrp(msrp):
    if msrp is None:
        return None
    return msrp.replace('\n', '').replace('$', '').replace(',', '')

