#!/usr/bin/env python3
import sys
import ipaddress

def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "malignas.txt"  
    errors = []
    seen_ips = set()

    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            raw = line.rstrip("\n")

            # Saltar líneas vacías
            if not raw.strip():
                continue

            # Dividir por espacios por si alguien mete "IP COMENTARIO"
            parts = raw.split()
            if len(parts) != 1:
                errors.append(
                    f"Línea {lineno}: se esperaba solo 1 valor, encontrado {len(parts)} → '{raw}'"
                )
                continue

            ip_str = parts[0]

            # Validar formato de IP
            try:
                ip = ipaddress.ip_address(ip_str)
            except ValueError:
                errors.append(
                    f"Línea {lineno}: valor no es una IP válida → '{raw}'"
                )
                continue

            # Detectar duplicados exactos
            if ip_str in seen_ips:
                errors.append(
                    f"Línea {lineno}: IP duplicada → '{ip_str}'"
                )
            else:
                seen_ips.add(ip_str)

    if errors:
        print("❌ Se detectaron problemas en el archivo de IPs:\n")
        for e in errors:
            print(" - " + e)
        print(f"\nTotal de errores: {len(errors)}")
        sys.exit(1)
    else:
        print(f"✅ Archivo '{path}' validado correctamente.")
        print(f"Total IPs únicas: {len(seen_ips)}")
        sys.exit(0)

if __name__ == "__main__":
    main()
