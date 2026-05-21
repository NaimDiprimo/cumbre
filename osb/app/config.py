"""Configuración del OSB. Lee de variables de entorno."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="OSB_", extra="ignore")

    # Base de datos
    database_url: str = "postgresql+psycopg2://cumbre:cumbre@postgres:5432/cumbre"

    # Cola de tareas
    redis_url: str = "redis://redis:6379/0"

    # API
    api_title: str = "Cumbre OSB"
    api_version: str = "0.1.0"
    api_description: str = (
        "Open Service Broker de Cumbre. Permite a developers internos "
        "aprovisionar balanceadores, rutas y servicios sin tickets."
    )

    # Operaciones
    log_level: str = "INFO"
    environment: str = "dev"
    anthropic_api_key: str = ""


settings = Settings()
