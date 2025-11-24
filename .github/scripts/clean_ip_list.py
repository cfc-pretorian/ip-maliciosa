#!/usr/bin/env python3
import sys
import ipaddress
import shutil
from pathlib import Path

def clean_ip_file(path_str: str):
    path = Path(path_str)

    if not path.exists():
        print(f"❌ El archivo '{path}' no existe.", file=sys.stderr)
        sys.exit(1)

    backup_path = path.with_suffix(path.suffix + ".bak")

    # Backup antes de tocar nada
    shutil.copy2(path, backup_path)
    print(f"📝 Backup creado: {backup_path}")

    seen_ips = set()
    valid_lines = []
    invalid_entries = []
    duplicate_entries = []

    with path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            raw = line.strip()

            # Saltar líneas vacías
            if not raw:
                continue

            parts = raw.split()
            if len(parts) != 1:
                invalid_entries.append(
                    f"Línea {lineno}: se esperaba 1 valor, encontrado {len(parts)} → '{raw}'"
                )
                continue

            ip_str = parts[0]

            # Validar IP
            try:
                ip = ipaddress.ip_address(ip_str)
            except ValueError:
                invalid_entries.append(
                    f"Línea {lineno}: valor no es una IP válida → '{raw}'"
                )
                continue

            # Duplicados
            if ip_str in seen_ips:
                duplicate_entries.append(
                    f"Línea {lineno}: IP duplicada → '{ip_str}'"
                )
                continue

            seen_ips.add(ip_str)
            valid_lines.append(ip_str)

    # Reescribir archivo solo con IPs válidas y únicas
    with path.open("w", encoding="utf-8") as f:
        for ip_str in valid_lines:
            f.write(ip_str + "\n")

    print("✅ Limpieza completada.")
    print(f"   IPs válidas y únicas: {len(valid_lines)}")

    if invalid_entries:
        print("\n⚠️ Entradas inválidas eliminadas:")
        for e in invalid_entries:
            print(" - " + e)

    if duplicate_entries:
        print("\n⚠️ Entradas duplicadas eliminadas:")
        for e in duplicate_entries:
            print(" - " + e)


def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "malignas.txt"  # cambia el nombre si tu archivo es otro

    clean_ip_file(file_path)


if __name__ == "__main__":
    main()
