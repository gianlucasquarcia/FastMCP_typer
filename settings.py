import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    MCP_SERVER_DEFAULT_PORT: int = field(
        default_factory=lambda: int(os.environ.get("MCP_SERVER_DEFAULT_PORT", "8000"))
    )
    MCP_SERVER_DEFAULT_TRANSPORT: str = field(
        default_factory=lambda: os.environ.get("MCP_SERVER_DEFAULT_TRANSPORT", "stdio")
    )
    LONG_RUNNING_TASK_FAKE_DELAY: int = field(
        default_factory=lambda: int(os.environ.get("LONG_RUNNING_TASK_FAKE_DELAY", "5"))
    )


settings = Settings()
