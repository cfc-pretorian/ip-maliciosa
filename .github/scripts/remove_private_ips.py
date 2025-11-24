#!/usr/bin/env python3
import sys
import ipaddress
import shutil
from pathlib import Path

def main():
    if len(sys.argv) > 1:
        path_str = sys.argv[1]
    else:
        path_str = "malignas.txt"  # cambia el nombre si tu archivo es otro

    path = Path(path_str)

    if not path.exists():
        print(f"❌ El archivo '{path}' no existe.", file=sys.stderr)
        sys.exit(1)

    # Backup antes de modificar
    backup_path = path.with_suffix(path.suffix + ".private.bak")
    shutil.copy2(path, backup_path)
    print(f"📝 Backup creado: {backup_path}")

    private_ips = set()
    kept_ips = []

    with path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            raw = line.strip()

            if not raw:
                continue

            parts = raw.split()
            if len(parts) != 1:
                # No tocamos estas líneas aquí, las puedes manejar con el validador general
                kept_ips.append(raw)
                continue

            ip_str = parts[0]
            try:
                ip = ipaddress.ip_address(ip_str)
            except ValueError:
                # No es IP válida, no la tratamos como privada
                kept_ips.append(raw)
                continue

            if ip.is_private:
                private_ips.add(ip_str)
            else:
                kept_ips.append(ip_str)

    # Reescribimos el archivo SIN IPs privadas
    with path.open("w", encoding="utf-8") as f:
        for ip_str in kept_ips:
            f.write(ip_str + "\n")

    # Guardamos listado de IPs privadas encontradas
    report_path = Path("private_ips_found.txt")
    if private_ips:
        with report_path.open("w", encoding="utf-8") as f:
            for ip_str in sorted(private_ips, key=lambda x: ipaddress.ip_address(x)):
                f.write(ip_str + "\n")

        print(f"⚠️ Se encontraron {len(private_ips)} IPs privadas. Se han eliminado del archivo.")
        print(f"📄 Detalle guardado en: {report_path}")
    else:
        # Si no hay privadas, aseguramos que no quede un archivo viejo dando vueltas
        if report_path.exists():
            report_path.unlink()
        print("✅ No se encontraron IPs privadas en el archivo.")

if __name__ == "__main__":
    main()
