SYSTEM_CONFIG = {
    (True,  True,  True):  {"system": "NEXSA_MAGCIS_ISS", "rows": 37},
    (True,  True,  False): {"system": "NEXSA_MAGCIS",     "rows": 35},
    (True,  False, True):  {"system": "NEXSA_EX06_ISS",   "rows": 23},
    (True,  False, False): {"system": "NEXSA_EX06",       "rows": 17},
    (False, True,  False): {"system": "ESQ_MAGCIS",       "rows": 33},
    (False, False, False): {"system": "ESQ_EX06",         "rows": 17},
}

def get_system_config(system_var, ionGun_var, isISS):
    return SYSTEM_CONFIG.get((system_var, ionGun_var, isISS))
