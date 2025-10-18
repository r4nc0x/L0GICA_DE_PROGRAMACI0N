Uso básico

```bash
python generador_personalizado_contrasenas.py [OPCIONES]
```

Ayuda rápida

```bash
python generador_personalizado_contrasenas.py -h
```

Opciones principales

Generación básica de contraseñas

```
-n, --longitud INT - Longitud de caracteres (por defecto: 12)

--no-minus - Desactivar letras minúsculas

--no-mayus - Desactivar letras mayúsculas

--no-digitos - Desactivar números

--simbolos - Incluir símbolos

-c, --count INT - Cantidad de contraseñas a generar (por defecto: 1)
```

Passphrases (frases de palabras)

```
--passphrase - Generar passphrase en lugar de password

--words INT - Número de palabras (por defecto: 5)

--wordlist PATH - Ruta a archivo con wordlist personalizada
```

Salida e informes

```
--entropy - Calcular y mostrar entropía y etiqueta de fuerza

--check-pwned - Consultar Have I Been Pwned (requiere requests)

--json - Salida en formato JSON (una línea por ítem)

--csv PATH_OR_DASH - Guardar salida en CSV (usar - para stdout)
```

Ejemplos de uso

Generar 1 contraseña con análisis completo

```bash
python generador_personalizado_contrasenas.py -n 12 --entropy --check-pwned
```

Generar múltiples contraseñas con símbolos

```bash
python generador_personalizado_contrasenas.py -n 16 -c 3 --simbolos --entropy --json
```

Generar 50 contraseñas y guardar en CSV

```bash
python generador_personalizado_contrasenas.py -n 12 -c 50 --entropy --csv salida.csv
```

Generar passphrases con wordlist personalizada

```bash
python generador_personalizado_contrasenas.py --passphrase --words 4 --wordlist diceware.txt -c 2 --entropy
```

Salida JSON para passphrase

```bash
python generador_personalizado_contrasenas.py --passphrase --words 6 --json
```

Formatos de salida

Campos devueltos

```
value - La contraseña o passphrase generada

entropy_bits - Entropía Shannon estimada en bits

strength_label - Etiqueta de fuerza basada en entropía

pwned_count - Número de apariciones en brechas (si --check-pwned)
```

Formato CSV

Las columnas corresponden a las claves del diccionario:

```csv
value,entropy_bits,strength_label,pwned_count
```

Códigos de salida (exit codes)

```
0 - Ejecución correcta

1 - Error en argumentos / error controlado

>1 - Excepciones no previstas
```

Seguridad y ética

Consideraciones importantes

```
✅ USO AUTORIZADO: Solo para pruebas propias, auditorías autorizadas o contraseñas personales

✅ k-anonymity: --check-pwned envía solo 5 caracteres del SHA-1

❌ NO USAR para atacar sistemas sin autorización explícita

🔒 Protege los archivos: No subas CSV con contraseñas a repositorios públicos
```

Configuración de .gitignore

Si generas archivos CSV, añade esto a tu .gitignore:

```text
*.csv
passwords/
output/
```

Resolución de problemas

requests no encontrado

Síntoma: Error al importar requests

Solución:

```bash
pip install requests
# o
sudo apt install python3-requests

Verificación:

python -c "import requests; print(requests.__version__)"
```

--check-pwned devuelve "no disponible"

Causas posibles:

```
Falta la librería requests

Problemas de red (proxy/firewall)

Rate limits del servicio
```

Diagnóstico:

```bash
curl -i "https://api.pwnedpasswords.com/range/ABCDE"
```

CSV vacío / sin salida

Solución:

```
Verificar que se usan --csv y/o --json correctamente

Por defecto la herramienta imprime salida legible por pantalla

Para CSV en stdout: --csv -
```

Estructura del proyecto

```text
generador_personalizado_contrasenas.py
├── Generación de contraseñas
├── Generación de passphrases  
├── Cálculo de entropía
├── Verificación HIBP (opcional)
└── Exportación JSON/CSV
```

Nota: Esta herramienta se proporciona con fines educativos y de seguridad. El uso indebido es responsabilidad del usuario.

