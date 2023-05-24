import typing

Scheduler = typing.Literal['synchronous', 'threads', 'processes']
scheduler_modes = typing.get_args(Scheduler)


def validate_scheduler(mode: str) -> None:
    if mode not in scheduler_modes:
        raise ValueError(f"Unsuported scheduler mode {mode}")
    return mode
