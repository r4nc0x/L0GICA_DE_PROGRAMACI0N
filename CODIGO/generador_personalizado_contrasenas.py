#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generador_personalizado_contrasenas.py
Generador de contraseñas con opciones avanzadas orientadas a seguridad defensiva.
Uso responsable: sólo para pruebas autorizadas, tus propias contraseñas o entornos de auditoría.
"""
from __future__ import annotations
import secrets
import string
import argparse
import math
import json
import csv
import hashlib
import sys
from typing import Optional

# Intentamos importar requests para pwned; si no está, solo desactivamos esa función
try:
    import requests  # type: ignore
    REQUESTS_AVAILABLE = True
except Exception:
    REQUESTS_AVAILABLE = False

# ---------------------------
# Funciones de generación
# ---------------------------
def generar_contrasena(longitud: int = 12, minus: bool = True, mayus: bool = True,
                       digitos: bool = True, simbolos: bool = False) -> str:
    """
    Genera una contraseña aleatoria según los parámetros indicados.
    """
    pool = ''
    if minus:
        pool += string.ascii_lowercase
    if mayus:
        pool += string.ascii_uppercase
    if digitos:
        pool += string.digits
    if simbolos:
        pool += '!@#$%&*()-_=+[]{};:,.<>?/'
    if not pool:
        raise ValueError("Debes habilitar al menos un tipo de carácter.")
    return ''.join(secrets.choice(pool) for _ in range(longitud))


# ---------------------------
# Passphrase (Diceware-like)
# ---------------------------
DEFAULT_EMBEDDED_WORDLIST = [
    # Pequeña wordlist embebida como fallback (no sustituye una Diceware real)
    "sol", "luna", "estrella", "gato", "perro", "viento", "mar", "roca",
    "fuego", "río", "árbol", "montaña", "nube", "lluvia", "campo", "ciudad",
    "puerta", "libro", "camino", "puente", "reloj", "puñado", "llave", "cielo"
]

def generar_passphrase(palabras: int = 5, wordlist_path: Optional[str] = None) -> str:
    """
    Genera una passphrase de `palabras` palabras. Si se proporciona
    wordlist_path, la usa (una palabra por línea). Si no, usa la lista embebida.
    """
    words = []
    if wordlist_path:
        try:
            with open(wordlist_path, "r", encoding="utf-8") as f:
                words = [w.strip() for w in f if w.strip()]
        except Exception as e:
            raise RuntimeError(f"Error leyendo wordlist '{wordlist_path}': {e}")
    if not words:
        words = DEFAULT_EMBEDDED_WORDLIST
    return ' '.join(secrets.choice(words) for _ in range(palabras))


# ---------------------------
# Entropía y etiqueta
# ---------------------------
def shannon_entropy(s: str) -> float:
    """Calcula la entropía en bits (Shannon) de la cadena."""
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    entropy = 0.0
    length = len(s)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    # entropía total en bits = entropy por símbolo * longitud
    return entropy * length

def strength_label(entropy_bits: float) -> str:
    """
    Etiqueta simple basada en entropía:
    - <28 bits: Muy débil
    - 28-36: Débil
    - 36-60: Aceptable
    - 60-80: Fuerte
    - >=80: Muy fuerte
    """
    if entropy_bits < 28:
        return "Muy débil"
    if entropy_bits < 36:
        return "Débil"
    if entropy_bits < 60:
        return "Aceptable"
    if entropy_bits < 80:
        return "Fuerte"
    return "Muy fuerte"


# ---------------------------
# Pwned Passwords (k-anonymity)
# ---------------------------
def pwned_count(password: str) -> Optional[int]:
    """
    Consulta la API de Have I Been Pwned (Pwned Passwords) usando k-anonymity.
    Devuelve el número de veces que aparece la contraseña en brechas (0 si no aparece).
    Si requests no está disponible, devuelve None.
    """
    if not REQUESTS_AVAILABLE:
        return None
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        resp = requests.get(url, timeout=10)
    except Exception:
        return None
    if resp.status_code != 200:
        return None
    for line in resp.text.splitlines():
        if not line:
            continue
        try:
            suf, count = line.split(':')
        except ValueError:
            continue
        if suf == suffix:
            try:
                return int(count)
            except ValueError:
                return None
    return 0


# ---------------------------
# Utilidades de salida
# ---------------------------
def salida_texto(password: str, entropy: float, label: str, pwned: Optional[int]) -> None:
    print(password)
    print(f"Entropía: {entropy:.2f} bits — {label}")
    if pwned is None:
        print("Pwned: (no disponible / requests no instalado o fallo en la consulta)")
    else:
        if pwned > 0:
            print(f"Pwned: APARECE en {pwned} brechas públicas (cambia esta contraseña).")
        else:
            print("Pwned: No aparece en la base de datos conocida.")


def salida_json(record: dict) -> str:
    return json.dumps(record, ensure_ascii=False, indent=2)


def salida_csv(records: list[dict], path: Optional[str]) -> None:
    if not records:
        return
    # Si path es None -> escribimos a stdout
    fieldnames = list(records[0].keys())
    if path:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in records:
                writer.writerow(r)
        print(f"CSV escrito en: {path}")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)


# ---------------------------
# CLI principal
# ---------------------------
def main():
    banner = (
        "USO RESPONSABLE: Esta herramienta es para pruebas autorizadas y evaluación de seguridad.\n"
        "No la uses para atacar sistemas o cuentas ajenas.\n"
    )
    parser = argparse.ArgumentParser(
        description="Generador personalizado de contraseñas (con análisis de entropía y opciones de export)."
    )
    # Generación básica
    parser.add_argument("-n", "--longitud", type=int, default=12,
                        help="Cantidad de caracteres para contraseñas (por defecto 12)")
    parser.add_argument("--no-minus", action="store_true",
                        help="Desactivar letras minúsculas")
    parser.add_argument("--no-mayus", action="store_true",
                        help="Desactivar letras mayúsculas")
    parser.add_argument("--no-digitos", action="store_true",
                        help="Desactivar números")
    parser.add_argument("--simbolos", action="store_true",
                        help="Incluir símbolos")
    parser.add_argument("-c", "--count", type=int, default=1,
                        help="Cantidad de contraseñas a generar")

    # Passphrase
    parser.add_argument("--passphrase", action="store_true",
                        help="Generar passphrase (frase) en lugar de password")
    parser.add_argument("--words", type=int, default=5,
                        help="Número de palabras para passphrase (por defecto 5)")
    parser.add_argument("--wordlist", type=str, default=None,
                        help="Ruta a fichero con wordlist (una palabra por línea) para passphrase")

    # Salida e informes
    parser.add_argument("--entropy", action="store_true",
                        help="Calcular y mostrar entropía y etiqueta de fuerza")
    parser.add_argument("--check-pwned", action="store_true",
                        help="Consultar Have I Been Pwned (si requests está disponible) — solo para tus contraseñas")
    parser.add_argument("--json", action="store_true",
                        help="Salida JSON por cada ítem (uno por línea)")
    parser.add_argument("--csv", type=str, default=None,
                        help="Guardar salida en CSV (ruta de archivo). Si no indica ruta, escribe CSV en stdout si --csv se usa como '--csv -'")

    args = parser.parse_args()

    # Banner de responsabilidad
    print(banner)

    # Compatibilidad CSV: si args.csv == '-' lo enviaremos a stdout
    csv_path = None
    if args.csv is not None:
        if args.csv.strip() == '-':
            csv_path = None
        else:
            csv_path = args.csv.strip()

    results = []

    for _ in range(max(1, args.count)):
        if args.passphrase:
            try:
                value = generar_passphrase(palabras=args.words, wordlist_path=args.wordlist)
            except Exception as e:
                print(f"Error generando passphrase: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            try:
                value = generar_contrasena(
                    longitud=args.longitud,
                    minus=not args.no_minus,
                    mayus=not args.no_mayus,
                    digitos=not args.no_digitos,
                    simbolos=args.simbolos
                )
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)

        entry = {
            "value": value,
        }

        if args.entropy or args.json or args.csv or args.check_pwned:
            ent = shannon_entropy(value)
            entry["entropy_bits"] = round(ent, 2)
            entry["strength_label"] = strength_label(ent)
        else:
            entry["entropy_bits"] = None
            entry["strength_label"] = None

        if args.check_pwned:
            if not REQUESTS_AVAILABLE:
                entry["pwned_count"] = None
            else:
                try:
                    entry["pwned_count"] = pwned_count(value)
                except Exception:
                    entry["pwned_count"] = None
        else:
            entry["pwned_count"] = None

        results.append(entry)

        # Salida por ítem (si no estamos guardando CSV y no pedimos JSON)
        if not args.json and args.csv is None:
            salida_texto(value,
                         entry["entropy_bits"] if entry["entropy_bits"] is not None else 0.0,
                         entry["strength_label"] or "",
                         entry["pwned_count"])

    # Salidas colectivas
    if args.json:
        # imprimimos un JSON por línea (ndjson)
        for r in results:
            print(salida_json(r))

    if args.csv is not None:
        salida_csv(results, csv_path)

if __name__ == "__main__":
    main()
