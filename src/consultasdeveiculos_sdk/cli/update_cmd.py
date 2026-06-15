"""Comando: update - Atualiza especificação da API."""

import json
from pathlib import Path


def update_command(args) -> int:
    import os
    import requests

    from consultasdeveiculos_sdk.core.config_manager import ConfigManager

    cm = ConfigManager()
    download_url = os.environ.get("DOWNLOAD_URL", "https://painel.consultasdeveiculos.com/download-postman")
    spec_dir = Path(__file__).resolve().parent.parent.parent.parent / "spec"
    postman_path = spec_dir / "postman.json"

    print("🔄 Atualizando especificação da API...")
    print()

    # Verifica versão atual
    manifest_path = spec_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        print(f"   Versão atual: {manifest.get('specVersion', '?')}")
    else:
        print("   Versão atual: nenhuma")

    try:
        print("   Baixando do servidor...")
        response = requests.get(download_url, timeout=30, headers={"Accept": "application/json, */*"})
        response.raise_for_status()

        postman = response.json()

        # Valida estrutura
        print("   Validando estrutura...")
        if "info" not in postman or "item" not in postman:
            raise RuntimeError("Resposta não possui estrutura Postman válida")

        # Extrai versão
        collection_name = postman.get("info", {}).get("name", "")
        version = cm.extract_version_from_filename(collection_name + ".postman_collection.json") or "1.0.0"

        # Salva
        spec_dir.mkdir(parents=True, exist_ok=True)

        # Salva postman
        filename = f"Consultas - V{version}.postman_collection.json"
        target_path = spec_dir / filename
        target_path.write_text(json.dumps(postman, indent=2, ensure_ascii=False), encoding="utf-8")

        # Atualiza manifest
        new_manifest = {
            "specVersion": version,
            "minRuntimeVersion": "1.0.0",
            "generatedAt": postman.get("info", {}).get("_postman_id", ""),
        }
        manifest_path.write_text(json.dumps(new_manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        # Salva no cache também
        cm.clear_cache()
        cache_postman = Path(cm.get_cached_postman_path())
        cache_manifest = Path(cm.get_cached_manifest_path())
        cache_postman.write_text(json.dumps(postman, indent=2, ensure_ascii=False), encoding="utf-8")
        cache_manifest.write_text(json.dumps(new_manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        print(f"   ✅ Atualizado para v{version}")
        print(f"   Arquivo: {target_path}")
        print()

        return 0

    except Exception as e:
        print(f"   ❌ Erro: {e}")
        print()
        return 1
