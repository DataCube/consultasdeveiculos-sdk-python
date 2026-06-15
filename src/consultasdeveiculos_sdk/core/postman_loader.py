"""Carregador de coleções Postman."""

import json
from pathlib import Path

from consultasdeveiculos_sdk.errors import SpecificationError


class PostmanLoader:
    """Carrega a especificação Postman de diferentes fontes."""

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def load(self) -> dict:
        """Carrega a coleção Postman."""
        if self.config_manager.has_local_cache():
            try:
                return self._load_from_cache()
            except Exception:
                pass

        return self._load_from_package()

    def _load_from_cache(self) -> dict:
        """Carrega a coleção do cache local."""
        postman_path = self.config_manager.get_cached_postman_path()
        manifest_path = self.config_manager.get_cached_manifest_path()

        if not Path(postman_path).exists():
            raise SpecificationError("Arquivo postman.json não encontrado no cache")
        if not Path(manifest_path).exists():
            raise SpecificationError("Arquivo manifest.json não encontrado no cache")

        postman = json.loads(Path(postman_path).read_text(encoding="utf-8"))
        manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))

        self._validate_postman(postman)
        self._validate_manifest(manifest)

        return {"postman": postman, "manifest": manifest, "source": "cache"}

    def _load_from_package(self) -> dict:
        """Carrega a coleção do diretório spec/ do pacote."""
        spec_dir = str(Path(__file__).resolve().parent.parent.parent.parent / "spec")

        postman_path = self.config_manager.find_postman_file(spec_dir)
        manifest_path = str(Path(spec_dir) / "manifest.json")

        if not postman_path:
            raise SpecificationError(
                'Arquivo Postman não encontrado (padrão: Consultas - V*.postman_collection.json). '
                'Execute "consultasdeveiculos-sdk update" para baixar a especificação.'
            )

        if not Path(manifest_path).exists():
            raise SpecificationError(
                'Arquivo manifest.json não encontrado. '
                'Execute "consultasdeveiculos-sdk update" para baixar a especificação.'
            )

        postman = json.loads(Path(postman_path).read_text(encoding="utf-8"))
        manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))

        if not manifest.get("specVersion"):
            filename = Path(postman_path).name
            manifest["specVersion"] = self.config_manager.extract_version_from_filename(filename) or "1.0.0"

        self._validate_postman(postman)
        self._validate_manifest(manifest)

        return {"postman": postman, "manifest": manifest, "source": "package", "postman_path": postman_path}

    def save_to_cache(self, postman: dict, manifest: dict):
        """Salva a coleção no cache local."""
        postman_path = self.config_manager.get_cached_postman_path()
        manifest_path = self.config_manager.get_cached_manifest_path()

        Path(postman_path).write_text(json.dumps(postman, indent=2, ensure_ascii=False), encoding="utf-8")
        Path(manifest_path).write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    def _validate_postman(self, postman: dict):
        """Valida a estrutura da coleção Postman."""
        if not postman:
            raise SpecificationError("Coleção Postman vazia")
        if "info" not in postman:
            raise SpecificationError("Coleção Postman sem informações (info)")
        if "item" not in postman or not isinstance(postman["item"], list):
            raise SpecificationError("Coleção Postman sem itens")

    def _validate_manifest(self, manifest: dict):
        """Valida a estrutura do manifest."""
        if not manifest:
            raise SpecificationError("Manifest vazio")
        if not manifest.get("specVersion"):
            raise SpecificationError("Manifest sem versão da especificação (specVersion)")
        if not manifest.get("minRuntimeVersion"):
            raise SpecificationError("Manifest sem versão mínima do runtime (minRuntimeVersion)")
