"""Script de pós-instalação."""

import sys
from pathlib import Path


def main():
    spec_dir = Path(__file__).resolve().parent.parent / "spec"
    manifest_path = spec_dir / "manifest.json"

    print()
    print("📦 consultasdeveiculos-sdk instalado com sucesso!")
    print()

    if manifest_path.exists():
        import json
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        print(f"   Spec: v{manifest.get('specVersion', '?')}")
    else:
        print("   ⚠️  Execute 'consultasdeveiculos-sdk update' para baixar a especificação")

    print()
    print("   Uso:")
    print("     from consultasdeveiculos_sdk import ConsultadeveiculosSDK")
    print('     client = ConsultadeveiculosSDK(auth_token="SEU_TOKEN")')
    print()
    print("   CLI:")
    print("     consultasdeveiculos-sdk endpoints")
    print("     consultasdeveiculos-sdk doctor")
    print()


if __name__ == "__main__":
    main()
