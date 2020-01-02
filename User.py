from Helper import USER_FILE


class User:

    def __init__(self):
        self._is_login = False

    @property
    def connected(self) -> bool:
        return self._is_login

    @connected.setter
    def connected(self, value: bool):
        self._is_login = value

    @staticmethod
    def get_user_details():
        configuration_dict = {}
        with open(USER_FILE) as file:
            for line in file:
                key, value = [item.strip() for item in line.strip().split(":")]
                configuration_dict[key] = value
        return configuration_dict
