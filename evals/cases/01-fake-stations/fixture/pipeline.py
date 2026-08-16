def validate(rec):
    if "id" not in rec: raise ValueError("no id")
    return rec

def enrich(rec):
    rec["score"] = rec["value"] * 2      # BUG: KeyError when 'value' absent
    return rec

def save(rec):
    raise RuntimeError("real save not implemented")

def process(rec):
    return save(enrich(validate(rec)))
