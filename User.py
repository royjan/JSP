class User:
    name = "14"
    password = "14"

    def __init__(self):
        self._is_login = False

    @property
    def connected(self) -> bool:
        return self._is_login

    @connected.setter
    def connected(self, value: bool):
        self._is_login = value
