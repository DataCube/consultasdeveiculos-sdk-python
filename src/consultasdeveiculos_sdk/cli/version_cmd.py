"""Comando: version - Mostra versão da SDK."""


def version_command(args) -> int:
    from consultasdeveiculos_sdk import __version__
    from consultasdeveiculos_sdk.core.sdk import ConsultadeveiculosSDK

    try:
        sdk = ConsultadeveiculosSDK(sandbox=True)
        info = sdk.get_info()
        spec_version = info["specVersion"]
    except Exception:
        spec_version = "?"

    print()
    print(f"   consultasdeveiculos-sdk v{__version__}")
    print(f"   Spec: v{spec_version}")
    print()

    return 0
