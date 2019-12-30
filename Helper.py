from Log import logger

MAX_LENGTH_PER_WORD = 15
IMAGES_FOLDER = 'images'
USER_FILE = 'ConnectionDetails.txt'


def add_to_clipboard(text: str):
    import clipboard
    clipboard.copy(text)


def capitalize(text: str) -> str:
    return text.capitalize()


def clean_part_number(text: str) -> str:
    text = text.replace(" ", "")
    text = text.splitlines()[-1]
    text = text.split("RP")[-1]
    text = text.rstrip()
    return text


def retries(num_of_tries: int = 3):
    def try_execute(f, *args, **kwargs):
        try:
            result = f(*args, **kwargs)
            return True, result
        except Exception as e:
            logger.error(str(e))
            return False, None

    def retry_deco(func):
        from functools import wraps
        @wraps(func)
        def wrapper(*args, **kwargs):
            for try_number in range(num_of_tries):
                success, result = try_execute(func, *args, **kwargs)
                if success:
                    return success
                logger.error(f'{func.__name__} failed in try number {try_number + 1}')
            raise Exception(f"Failed after {num_of_tries} times!")

        return wrapper

    return retry_deco
