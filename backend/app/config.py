from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    unknown_threshold: float = 0.70
    max_upload_mb: int = 10
    checkpoint_dir: str = "checkpoints"
    models_json: str = "models.json"
    kb_path: str = "data/vn30_foods.csv"
    allowed_origins: str = "http://localhost:3000"
    device: str = "auto"
    model_cache_size: int = 4

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def resolve(self, value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else BACKEND_DIR / path

    @property
    def checkpoint_path(self) -> Path:
        return self.resolve(self.checkpoint_dir)

    @property
    def models_path(self) -> Path:
        return self.resolve(self.models_json)

    @property
    def kb_file(self) -> Path:
        return self.resolve(self.kb_path)

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    def torch_device(self) -> str:
        if self.device != "auto":
            return self.device
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"


settings = Settings()
