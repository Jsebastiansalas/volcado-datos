# Limpieza y Normalización de Base de Datos Geográfica (World / Países)

Este repositorio contiene un conjunto de herramientas y scripts en **Python** desarrollados para sanear, reparar y normalizar los volcados SQL de la clásica base de datos geográfica (*World*: `city`, `country`, `countrylanguage`), dejándolos 100% compatibles con el estándar ANSI SQL / PostgreSQL y con su integridad ortográfica restaurada en codificación **UTF-8**.

---

## 📌 Contexto y Diagnóstico del Problema

Los archivos originales (`city.sql`, `country.sql` y `countrylanguage.sql`) presentaban múltiples problemas de compatibilidad y corrupción de datos originados por exportaciones previas de MySQL y fallos en la codificación de caracteres:

1. **Sintaxis propietaria de MySQL**:
   - Uso de comillas invertidas (*backticks* `` ` ``) para nombres de tablas y columnas (incompatibles por defecto en PostgreSQL).
   - Secuencias de escape de comillas mediante barra invertida (`\'`), cuando el estándar SQL exige duplicar la comilla simple (`''`).

2. **Corrupción de caracteres y pérdida de acentos (Mojibake / Encoding mismatch)**:
   - Presencia masiva del carácter Unicode de reemplazo `\ufffd` (carácter de interrogación o rombo ``), producto de conversiones incorrectas entre ISO-8859-1 (Latin-1) y UTF-8.
   - Pérdida de tildes, cedillas, virgulillas y diéresis en nombres de países, capitales, distritos, ciudades, lenguas y mandatarios (ej. *Mxico* en vez de *México*, *So Paulo* en vez de *São Paulo*, *Belgi/Belgique* en vez de *België/Belgique*, *Espaa* en vez de *España*).
   - Nombres distorsionados por capturas o reemplazos defectuosos (ej. *Poááta Grossa*, *Macaééáá*, *Rio de Jaúúeiro*, *Jund.a..*).

3. **Conflicto con apóstrofes internos**:
   - Nombres propios con apóstrofes legítimos (como *Côte d'Ivoire*, *People's Republic*, *Al-Iraq*, *'s-Hertogenbosch*) provocaban cierres prematuros de cadenas SQL, generando errores de sintaxis (`syntax error at or near...`) al ejecutar los `INSERT`.

4. **Incompatibilidad de tipos booleanos**:
   - En `countrylanguage.sql`, la columna `isofficial` venía exportada como caracteres `'t'` y `'f'`, los cuales no se mapean limpiamente en entornos donde se espera el tipo booleano nativo (`TRUE` o `FALSE`).

5. **Campos nulos o vacíos indebidos**:
   - Casos como la Antártida (`ATA`), donde el nombre local (`localname`) había quedado reducido a comillas vacías `''` tras la pérdida del carácter original.

---

## 🛠️ ¿Cómo se logró limpiar bien los archivos SQL?

Para resolver estos problemas sin alterar la integridad referencial ni dañar palabras que contuvieran secuencias similares, se aplicó una **estrategia de limpieza controlada en múltiples etapas**:

### 1. Reemplazo seguro delimitado por celdas (`f"'{k}'" -> f"'{v}'"`)
Un error común al usar expresiones o reemplazos globales es sustituir subcadenas dentro de palabras que no corresponden (por ejemplo, reemplazar `Par` por `Pará` alteraría palabras como `Paris` o `Part`). 

**Solución aplicada**: Los scripts buscan la celda SQL completa entre comillas simples:
```python
# Se delimita con comillas simples para asegurar que sólo se reemplaza el valor exacto del campo
for k, v in CAMPOS_EXACTOS.items():
    linea = linea.replace(f"'{k}'", f"'{v}'")
```

### 2. Conversión al estándar SQL ANSI / PostgreSQL
- Se eliminaron todos los backticks `` ` ``.
- Se convirtieron los escapes de MySQL `\'` al estándar de comilla simple doble `''`.
- Se normalizaron comillas redundantes triples o cuádruples (`''''` o `'''`) a `''`.
- Los valores de bandera `'t'` y `'f'` de `countrylanguage` se convirtieron a literales booleanos reales:
  ```python
  linea = re.sub(r",\s*'[Tt]',", ", TRUE,", linea)
  linea = re.sub(r",\s*'[Ff]',", ", FALSE,", linea)
  ```

### 3. Diccionarios de reparación ortográfica y toponimia
Se investigó la correspondencia geográfica real de cada término afectado para construir diccionarios exhaustivos:
- **Brasil y Sudamérica**: Corrección de estados (`Goiás`, `Paraná`, `Espírito Santo`) y más de 80 municipios brasileños (`São Paulo`, `Ribeirão Preto`, `São José dos Campos`, `Nova Iguaçu`, etc.).
- **Topónimos y mandatarios internacionales**: Restauración de nombres históricos y actuales (`Fernando de la Rúa`, `Heydər Əliyev`, `Václav Havel`, `Hipólito Mejía Domínguez`, `José Eduardo dos Santos`, etc.).
- **Idiomas oficiales y regionales**: Normalización de nombres como `Aymara`, `Guaraní`, `Quechua`, `K'iche'`, `Nahuatl`, `Otomí`, etc.

### 4. Reglas regex para casos borde
- **Restauración de la Antártida**: Mediante regex se detectó el registro específico con campo vacío antes de `'Co-administrated'` y se restauró `'Antarctica'`.
- **Corrección de cierres de comillas rotas**: Aseguramiento de delimitadores en casos anómalos (por ejemplo, el registro de *Jundiaí* en Brasil).

---

## 📁 Estructura del Repositorio

```text
├── city.sql                         # Archivo original de ciudades (con errores y caracteres rotos)
├── city_corregido.sql               # Archivo saneado listo para importación
├── country.sql                      # Archivo original de países (con errores de encoding y sintaxis)
├── country_corregido.sql            # Archivo de países corregido
├── countrylanguage.sql              # Archivo original de idiomas por país
├── countrylanguage_corregido.sql    # Archivo de idiomas corregido (con booleanos nativos)
├── reparar_geografia.py             # Script de corrección para city.sql
├── reparar_country.py               # Script de corrección avanzada para country.sql
├── reparar_country_language.py      # Script para procesar country.sql y countrylanguage.sql
└── README.md                        # Documentación técnica del proyecto
```

---

## ⚙️ Descripción de los Scripts

### 🔹 [`reparar_geografia.py`](file:///c:/Users/USUARIO/OneDrive/Documents/paises/reparar_geografia.py)
- **Objetivo**: Sanear `city.sql` y generar `city_corregido.sql`.
- **Acciones principales**:
  1. Elimina backticks y traduce escapes `\'` a `''`.
  2. Suprime el carácter `\ufffd`.
  3. Mapea mediante el diccionario `CAMPOS_EXACTOS` más de 120 distritos y municipios de Brasil y otros países.
  4. Resuelve irregularidades ortográficas específicas como `'s-Hertogenbosch` y `Curaçao`.

### 🔹 [`reparar_country.py`](file:///c:/Users/USUARIO/OneDrive/Documents/paises/reparar_country.py)
- **Objetivo**: Limpieza especializada de `country.sql` para generar `country_corregido.sql`.
- **Acciones principales**:
  1. Tratamiento detallado de apóstrofes internos (`Côte d''Ivoire`, `People''s Republic`, `YeItyop''iya`, etc.).
  2. Corrección de nombres de estados, regiones y formas de gobierno con acentos y caracteres especiales (`Česko`, `España`, `México`, `São Tomé e Príncipe`, etc.).
  3. Corrección de nombres de jefes de estado.
  4. Recuperación del campo `localname` de la Antártida.

### 🔹 [`reparar_country_language.py`](file:///c:/Users/USUARIO/OneDrive/Documents/paises/reparar_country_language.py)
- **Objetivo**: Procesamiento combinado de países e idiomas.
- **Acciones principales sobre idiomas**:
  1. Reemplaza nombres de lenguas indígenas y tradicionales con caracteres especiales (`K'ekchi`, `K'iche'`, `Guaraní`, `Quechua`, etc.).
  2. Transforma los valores de cadena `'t'` y `'f'` en constantes booleanas de SQL `TRUE` y `FALSE`.

---

## 🚀 Cómo Ejecutar los Scripts

Para regenerar o aplicar la limpieza a nuevos volcados con la misma estructura, asegúrate de contar con **Python 3.8+** y ejecuta los scripts desde la raíz del proyecto:

```bash
# 1. Reparar datos de ciudades
python reparar_geografia.py

# 2. Reparar datos de países (con normalización de apóstrofes y nombres)
python reparar_country.py

# 3. Reparar lenguas e idiomas (y conversión booleana)
python reparar_country_language.py
```

Al finalizar la ejecución, se habrán generado los archivos:
- `city_corregido.sql`
- `country_corregido.sql`
- `countrylanguage_corregido.sql`

---

## 📊 Tabla Comparativa de Ejemplos

| Caso / Entidad | Entrada Original (`.sql`) | Salida Corregida (`_corregido.sql`) | Motivo de la Corrección |
| :--- | :--- | :--- | :--- |
| **Comillas invertidas** | ``INSERT INTO `city` (`name`)`` | `INSERT INTO "public"."city" ("name")` / `INSERT INTO city (name)` | Incompatibilidad de backticks fuera de MySQL. |
| **Escapes de comillas** | `'C\''te d\'Ivoire'` | `'Côte d''Ivoire'` | Estándar SQL exige duplicar comillas simples (`''`). |
| **Booleanos** | `('COL', 'Spanish', 't', 99.0)` | `('COL', 'Spanish', TRUE, 99.0)` | Mapeo al tipo nativo `BOOLEAN` de PostgreSQL. |
| **Ciudad (Brasil)** | `'So Paulo'` | `'São Paulo'` | Pérdida de tilde diacrítica (~). |
| **Distrito** | `'Esprito Santo'` | `'Espírito Santo'` | Pérdida de vocal acentuada (í). |
| **País / Jefe de Estado** | `'Fernando de la Ra'` | `'Fernando de la Rúa'` | Corrupción por byte `\ufffd`. |
| **Caribe / Países Bajos** | `'Curaao'` | `'Curaçao'` | Pérdida de la cedilla (ç). |
| **Antártida** | `('', 'Co-administrated')` | `('Antarctica', 'Co-administrated')` | Nombre local vacío tras corrupción de datos. |

---

## 🎯 Conclusión y Resultados

Con este proceso:
- Se garantiza la **ejecución limpia y sin errores** en motores relacionales modernos como PostgreSQL.
- Se preserva la **fidelidad ortográfica y cultural** de nombres propios y lenguas de todo el mundo.
- Se asegura que los scripts sean **idempotentes y seguros**, evitando sobre-escrituras o efectos colaterales en los datos.
