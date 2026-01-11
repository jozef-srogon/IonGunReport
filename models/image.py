class Image:
    def __init__(self, name, image_path):
        self.name = name
        self.image_path = image_path

    def __str__(self):
        return f"Photo: {self.name}, Path: {self.image_path}"