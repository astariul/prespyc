"""Mutable state of the ActionScript 2 virtual machine."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class State:
    """
    The current state of the AVM.

    `Processor` is stateless, so an instance of this class is threaded through every `run()` call
    and holds everything the executed bytecode can observe or change.
    """

    __slots__ = ("constants", "functions", "stack", "variables")

    def __init__(self) -> None:
        self.constants: list[str] = []
        """Constant pool, as set by the last `ActionConstantPool`."""

        self.stack: list[Any] = []
        """The execution stack."""

        self.variables: dict[str, Any] = {}
        """Current global variables."""

        self.functions: dict[str, Callable[..., Any]] = {}
        """
        Global functions the bytecode may call by name.

        Only reachable when the processor was built with `allow_function_call=True`.
        """
