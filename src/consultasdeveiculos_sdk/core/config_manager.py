"""Gerenciador de configurações da SDK."""

import os
import re
from pathlib import Path


class ConfigManager:
    """Gerencia todas as configurações da SDK de forma centralizada."""

    DEFAULT_CONFIG = {
        "cache_dir": str(Path.home() / ".consultasdeveiculos-sdk"),
        "download_url": os.environ.get("DOWNLOAD_URL", "https://painel.consultasdeveiculos.com/download-postman"),
        "timeout": 30000,
        "max_retries": 3,
        "retry_delay": 1000,
        "compression": True,
        "default_headers": {
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    }

    def __init__(self, user_config: dict | None = None):
        self.config = {**self.DEFAULT_CONFIG, **(user_config or {})}
        self._ensure_cache_dir()

    def get(self, key: str):
        """Obtém uma configuração."""
        return self.config.get(key)

    def set(self, key: str, value):
        """Define uma configuração."""
        self.config[key] = value

    def get_all(self) -> dict:
        """Obtém todas as configurações."""
        return dict(self.config)

    def get_cache_dir(self) -> str:
        """Caminho do diretório de cache."""
        return self.config["cache_dir"]

    def get_cached_postman_path(self) -> str:
        """Caminho do arquivo postman.json no cache."""
        return str(Path(self.config["cache_dir"]) / "postman.json")

    def get_cached_manifest_path(self) -> str:
        """Caminho do arquivo manifest.json no cache."""
        return str(Path(self.config["cache_dir"]) / "manifest.json")

    def get_response_cache_dir(self) -> str:
        """Caminho do diretório de cache de respostas."""
        return str(Path(self.config["cache_dir"]) / "cache")

    def find_postman_file(self, directory: str) -> str | None:
        """Encontra arquivo Postman pelo padrão de nome."""
        dir_path = Path(directory)
        if not dir_path.exists():
            return None

        pattern = re.compile(r"^Consultas\s*-\s*V[\d.]+\.postman_collection\.json$", re.IGNORECASE)
        for f in dir_path.iterdir():
            if f.is_file() and pattern.match(f.name):
                return str(f)
        return None

    def extract_version_from_filename(self, filename: str) -> str | None:
        """Extrai versão do nome do arquivo Postman."""
        match = re.search(r"V([\d.]+)\.postman_collection\.json$", filename, re.IGNORECASE)
        return match.group(1) if match else None

    def has_local_cache(self) -> bool:
        """Verifica se há cache local."""
        return (
            Path(self.get_cached_postman_path()).exists()
            and Path(self.get_cached_manifest_path()).exists()
        )

    def clear_cache(self):
        """Limpa todo o cache."""
        import shutil
        cache_dir = Path(self.config["cache_dir"])
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Garante que o diretório de cache existe."""
        cache_dir = Path(self.config["cache_dir"])
        cache_dir.mkdir(parents=True, exist_ok=True)
        response_cache = Path(self.get_response_cache_dir())
        response_cache.mkdir(parents=True, exist_ok=True)
