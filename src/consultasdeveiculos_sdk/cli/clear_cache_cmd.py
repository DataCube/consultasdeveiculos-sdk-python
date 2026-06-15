"""Comando: clear-cache - Limpa cache local."""

from pathlib import Path


def clear_cache_command(args) -> int:
    from consultasdeveiculos_sdk.core.config_manager import ConfigManager

    cm = ConfigManager()
    cache_dir = Path(cm.get_cache_dir())

    if not args.force:
        print(f"   Diretório de cache: {cache_dir}")
        answer = input("   Deseja limpar? [s/N] ").strip().lower()
        if answer not in ("s", "sim", "y", "yes"):
            print("   Cancelado.")
            return 0

    cm.clear_cache()
    print(f"   ✅ Cache limpo: {cache_dir}")
    print()

    return 0
