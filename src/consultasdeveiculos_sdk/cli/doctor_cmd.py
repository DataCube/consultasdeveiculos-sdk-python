"""Comando: doctor - Verifica status da instalação."""

import sys
from pathlib import Path


def doctor_command(args) -> int:
    print()
    print("🩺 SDK Doctor")
    print()

    issues = []

    # Verifica Python
    print(f"   ✅ Python: {sys.version.split()[0]}")

    # Verifica requests
    try:
        import requests
        print(f"   ✅ requests: {requests.__version__}")
    except ImportError:
        print("   ❌ requests: não instalado")
        issues.append("requests não instalado")

    # Verifica spec
    spec_dir = Path(__file__).resolve().parent.parent.parent.parent / "spec"
    manifest_path = spec_dir / "manifest.json"

    if manifest_path.exists():
        import json
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        print(f"   ✅ Spec: v{manifest.get('specVersion', '?')}")
    else:
        print("   ❌ Spec: não encontrada")
        issues.append("spec/manifest.json não encontrado")

    # Verifica Postman
    from consultasdeveiculos_sdk.core.config_manager import ConfigManager
    cm = ConfigManager()
    postman_file = cm.find_postman_file(str(spec_dir))
    if postman_file:
        print(f"   ✅ Postman: {Path(postman_file).name}")
    else:
        print("   ❌ Postman: arquivo não encontrado")
        issues.append("Arquivo Postman não encontrado")

    # Verifica SDK carrega
    try:
        from consultasdeveiculos_sdk.core.sdk import ConsultadeveiculosSDK
        sdk = ConsultadeveiculosSDK(sandbox=True)
        info = sdk.get_info()
        print(f"   ✅ SDK: {info['slugsCount']} endpoints carregados")
    except Exception as e:
        print(f"   ❌ SDK: {e}")
        issues.append(f"SDK não carrega: {e}")

    # Cache
    cache_dir = Path(cm.get_cache_dir())
    if cache_dir.exists():
        print(f"   ✅ Cache: {cache_dir}")
    else:
        print(f"   ⚠️  Cache: não existe ({cache_dir})")

    print()
    if issues:
        print(f"   ⚠️  {len(issues)} problema(s) encontrado(s)")
        for issue in issues:
            print(f"      • {issue}")
    else:
        print("   ✅ Tudo OK!")
    print()

    return 1 if issues else 0
