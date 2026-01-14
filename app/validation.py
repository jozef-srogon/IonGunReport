from reportlab.lib import colors

def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def in_range(value, min_v, max_v):
    val = to_float(value)
    return val is not None and min_v <= val <= max_v

def apply_red(style, col, row):
    style.add('TEXTCOLOR', (col, row), (col, row), colors.red)
    style.add('FONTNAME', (col, row), (col, row), 'Helvetica-Bold')

def validate_row(m, rules):
    idx = str(m.index)
    issues = []

    for param, idx_map in rules.items():
        rng = idx_map.get(idx)
        if not rng:
            continue
        min_v, max_v = rng
        value = getattr(m, param, None)

        if not in_range(value, min_v, max_v):
            issues.append((param, (min_v, max_v)))

    return issues
