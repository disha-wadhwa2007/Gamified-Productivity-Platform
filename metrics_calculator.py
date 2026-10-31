def calculate_conversion_rate(clicks, conversions):
    # BUG: When clicks is 0, throws ZeroDivisionError!
    rate = (conversions / clicks) * 100.0
    return round(rate, 2)
