class Measurement():
    def __init__(self, index, setup, ion_energy_eV, ion_energy_uA, electron_energy_eV, electron_energy_mA, fil, extractor, condensor, drift,
                 magnet, focus, X_shift, Y_shift, ratio, sample_current_work, sample_current_max, sample_current_aim, mode, date = None, specification = None):
        self.index = index
        self.setup = setup
        self.ion_energy_eV = ion_energy_eV
        self.ion_energy_uA = ion_energy_uA
        self.electron_energy_eV = electron_energy_eV
        self.electron_energy_mA = electron_energy_mA
        self.fil = fil
        self.extractor = extractor
        self.condensor = condensor
        self.drift = drift
        self.magnet = magnet
        self.focus = focus
        self.X_shift = X_shift
        self.Y_shift = Y_shift
        self.ratio = ratio
        self.sample_current_work = sample_current_work
        self.sample_current_max = sample_current_max
        self.sample_current_aim = sample_current_aim
        self.mode = mode
        self.date = date
        self.specification = specification

    def __str__(self):
        return (
            f"Index: {self.index}\n"
            f"Setup: {self.setup}\n"
            f"Ion_Energy_eV: {self.ion_energy_eV}\n"
            f"Ion_Energy_uA: {self.ion_energy_uA}\n"
            f"Electron_Energy_eV: {self.electron_energy_eV}\n"
            f"Electron_Energy_uA: {self.electron_energy_mA}\n"
            f"Fil: {self.fil}\n"
            f"Extractor: {self.extractor}\n"
            f"Condensor: {self.condensor}\n"
            f"Drift: {self.drift}\n"
            f"Magnet: {self.magnet}\n"
            f"Focus: {self.focus}\n"
            f"X_Shift: {self.X_shift}\n"
            f"Y_Shift: {self.Y_shift}\n"
            f"Ratio: {self.ratio}\n"
            f"Sample_Current_Work: {self.sample_current_work}\n"
            f"Sample_Current_Max: {self.sample_current_max}\n"
            f"Sample_Current_Aim: {self.sample_current_aim}\n"
            f"Mode: {self.mode}\n"
            f"Date: {self.date}\n"
            f"Spec: {self.specification}"
        )
