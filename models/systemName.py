class System():
    def __init__(self, name, results=None):
        self.name = name
        self.results = results if results is not None else []

    def __str__(self):
        return f"System: {self.name} {len(self.results)}"