class User:
    name = "da87217"
    password = "kb2851ru"

    def __init__(self):
        self._is_login = False

    @property
    def connected(self) -> bool:
        return self._is_login

    @connected.setter
    def connected(self, value: bool):
        self._is_login = value
