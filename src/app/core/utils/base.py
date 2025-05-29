import pathlib


class BaseUtils:
    """
    Base API utils class
    """

    async def remove_pycache(self) -> None:
        """
        Remove pycache folders
        """

        try:
            [p.unlink() for p in pathlib.Path(".").rglob("*.py[co]") if ".venv" not in p.parts]
            [p.rmdir() for p in pathlib.Path(".").rglob("__pycache__") if ".venv" not in p.parts]
        except:  # noqa
            pass
