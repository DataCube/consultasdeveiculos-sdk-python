"""Comando: endpoints - Lista endpoints disponíveis."""

import json


def endpoints_command(args) -> int:
    from consultasdeveiculos_sdk.core.sdk import ConsultadeveiculosSDK

    sdk = ConsultadeveiculosSDK(sandbox=True)
    all_endpoints = sdk.list_endpoints()
    info = sdk.get_info()

    if args.json:
        print(json.dumps(all_endpoints, indent=2, ensure_ascii=False))
        return 0

    print()
    print("📡 Endpoints Disponíveis")
    print()
    print(f"   Specification: v{info['specVersion']}")
    print(f"   Total: {len(all_endpoints)} endpoints")
    print(f"   Namespaces: {', '.join(info['namespaces'])}")
    print()
    print("   💡 Use o SLUG para chamar: client.SLUG(param='valor')")
    print()

    # Agrupa por namespace
    by_namespace: dict[str, list] = {}
    for ep in all_endpoints:
        parts = ep["slug"].split("_")
        ns = parts[0] if parts else "outros"
        by_namespace.setdefault(ns, []).append(ep)

    # Filtra por namespace se especificado
    if args.namespace:
        if args.namespace not in by_namespace:
            print(f"   ❌ Namespace \"{args.namespace}\" não encontrado.")
            print(f"   Namespaces disponíveis: {', '.join(by_namespace.keys())}")
            print()
            return 1
        namespaces_to_show = {args.namespace: by_namespace[args.namespace]}
    else:
        namespaces_to_show = by_namespace

    for ns, eps in namespaces_to_show.items():
        print("━" * 74)
        print(f"📁 {ns.upper()} ({len(eps)} endpoints)")
        print("━" * 74)
        print()

        for ep in eps:
            params = ""
            body = ep.get("body")
            if body and isinstance(body, dict):
                keys = [k for k in body.keys() if k != "auth_token"]
                params = ", ".join(keys)
            print(f"   📌 client.{ep['slug']}({params})")
            print(f"      Nome: {ep['name']}")

            if args.verbose and ep.get("description"):
                desc = ep["description"][:70]
                suffix = "..." if len(ep.get("description", "")) > 70 else ""
                print(f"      Desc: {desc}{suffix}")
            if args.verbose and ep.get("url"):
                print(f"      URL:  {ep['url']}")
            print()

    print("━" * 74)
    print()
    print("📝 Exemplo de uso:")
    print()
    print('   client = ConsultadeveiculosSDK(auth_token="TOKEN")')
    if all_endpoints:
        example = all_endpoints[0]
        print(f'   result = client.{example["slug"]}(param="valor")')
    print()
    print("💡 Dicas:")
    print("   • Use --verbose para ver descrições e URLs")
    print("   • Use --json para saída em JSON")
    print("   • Filtre por namespace: consultasdeveiculos-sdk endpoints veiculos")
    print()

    return 0
