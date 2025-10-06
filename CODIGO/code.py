#!/usr/bin/env python3
"""
generador_personalizado_contrasenas.py
Generador de contraseñas con opciones desde consola
"""
import secrets
import string
import argparse


def generar_contrasena(longitud=12, minus=True, mayus=True,
                       digitos=True, simbolos=False):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generador personalizado de contraseñas"
    )
    parser.add_argument("-n", "--longitud", type=int, default=12,
                        help="Cantidad de caracteres (por defecto 12)")
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

    args = parser.parse_args()

    for _ in range(args.count):
        print(
            generar_contrasena(
                longitud=args.longitud,
                minus=not args.no_minus,
                mayus=not args.no_mayus,
                digitos=not args.no_digitos,
                simbolos=args.simbolos
            )
        )
