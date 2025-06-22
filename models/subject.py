class Subject:
    """Representa una materia o curso del usuario."""
    def __init__(self, user_id, name, color, _id=None):
        self.user_id = user_id
        self.name = name
        self.color = color  # Color en formato hexadecimal, ej: "#FF0000"
        self._id = _id

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "color": self.color
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data.get("user_id"),
            name=data.get("name"),
            color=data.get("color"),
            _id=data.get("_id")
        )