"""CLI da SDK - ponto de entrada."""

import sys
import argparse

from consultasdeveiculos_sdk.cli.endpoints_cmd import endpoints_command
from consultasdeveiculos_sdk.cli.doctor_cmd import doctor_command
from consultasdeveiculos_sdk.cli.version_cmd import version_command
from consultasdeveiculos_sdk.cli.update_cmd import update_command
from consultasdeveiculos_sdk.cli.clear_cache_cmd import clear_cache_command


def main():
    """Ponto de entrada principal da CLI."""
    parser = argparse.ArgumentParser(
        prog="consultasdeveiculos-sdk",
        description="SDK Python para API Consultas de Veículos",
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # endpoints
    ep_parser = subparsers.add_parser("endpoints", help="Lista endpoints disponíveis")
    ep_parser.add_argument("namespace", nargs="?", help="Filtra por namespace")
    ep_parser.add_argument("--json", action="store_true", help="Saída em JSON")
    ep_parser.add_argument("-v", "--verbose", action="store_true", help="Modo verbose")

    # doctor
    subparsers.add_parser("doctor", help="Verifica status da instalação")

    # version
    subparsers.add_parser("version", help="Mostra versão da SDK")

    # update
    subparsers.add_parser("update", help="Atualiza especificação da API")

    # clear-cache
    cc_parser = subparsers.add_parser("clear-cache", help="Limpa cache local")
    cc_parser.add_argument("--force", action="store_true", help="Força limpeza sem confirmação")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "endpoints": endpoints_command,
        "doctor": doctor_command,
        "version": version_command,
        "update": update_command,
        "clear-cache": clear_cache_command,
    }

    cmd_func = commands.get(args.command)
    if cmd_func:
        try:
            sys.exit(cmd_func(args))
        except Exception as e:
            print(f"❌ Erro: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
