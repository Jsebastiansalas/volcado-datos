import os
import re

archivo_in = 'country.sql'
archivo_out = 'country_corregido.sql'

if not os.path.exists(archivo_in):
    print(f"[-] No se encontró {archivo_in}")
    exit()

with open(archivo_in, 'r', encoding='utf-8', errors='replace') as f:
    contenido = f.read()

# 1. Eliminar comillas invertidas de MySQL
contenido = contenido.replace("`", "")

# 2. Quitar caracteres Unicode rotos residuales (\ufffd)
contenido = contenido.replace('\ufffd', '')

# 3. Normalizar comillas triples o cuádruples accidentales a una sola comilla escapada estándar ('')
contenido = contenido.replace("''''", "''")
contenido = contenido.replace("'''", "''")

# 4. Corregir casos específicos de nombres en country con apóstrofe interno
nombres_apostrofe = {
    "Côte d'Ivoire": "Côte d''Ivoire",
    "Cote d'Ivoire": "Côte d''Ivoire",
    "Cte dIvoire": "Côte d''Ivoire",
    "Cte d'Ivoire": "Côte d''Ivoire",
    "People's Republic": "People''s Republic",
    "People''sRepublic": "People''s Republic",
    "Al-Iraq": "Al-''Iraq",
    "YeItyopiya": "YeItyop''iya",
    "Taehan Minguk (Namhan)": "Taehan Min''guk (Namhan)",
    "Choson Minjujuui Inmin Konghwaguk (Bukhan)": "Choson Minjujuui In''min Konghwaguk (Bukhan)",
    "Maaouiya Ould SidAhmad Taya": "Maaouiya Ould Sid''Ahmad Taya",
    "Maaouiya Ould Sid'Ahmad Taya": "Maaouiya Ould Sid''Ahmad Taya"
}

# 5. Diccionario de normalización ortográfica para Country
REEMPLAZOS_PAISES = {
    "Rpublique Dmocratique du Congo": "République Démocratique du Congo",
    "Bnin": "Bénin",
    "Centrafrique/B-Afrka": "Centrafrique/Bê-Afrîka",
    "Froyar": "Føroyar",
    "Bouvetya": "Bouvetøya",
    "Kalaallit Nunaat/Grnland": "Kalaallit Nunaat/Grønland",
    "esko": "Česko",
    "Kpros/Kibris": "Kýpros/Kıbrıs",
    "Espaa": "España",
    "Hati/Dayti": "Haïti/Dayti",
    "sland": "Ísland",
    "Mxico": "México",
    "Moambique": "Moçambique",
    "Nouvelle-Caldonie": "Nouvelle-Calédonie",
    "Per/Piruw": "Perú/Piruw",
    "Repblica Dominicana": "República Dominicana",
    "Romnia": "România",
    "Sngal/Sounougal": "Sénégal/Sounougal",
    "So Tom e Prncipe": "São Tomé e Príncipe",
    "Tshad/Tchad": "Tchad/Tšad",
    "Trkmenostan": "Türkmenostan",
    "Trkiye": "Türkiye",
    "Tai-wan": "T'ai-wan",
    "Shqipria": "Shqipëria",
    "Azrbaycan": "Azərbaycan",
    "Belgi/Belgique": "België/Belgique",
    "sterreich": "Österreich",
    "Al-Jazair/Algrie": "Al-Jazā'ir/Algérie",
    "Terres australes franaises": "Terres australes françaises",
    "Guyane franaise": "Guyane française",
    "Polynsie franaise": "Polynésie française",
    "Runion": "Réunion",
    "Jos Eduardo dos Santos": "José Eduardo dos Santos",
    "Fernando de la Ra": "Fernando de la Rúa",
    "Robert Kotarjan": "Robert Kotšarjan",
    "Heydr liyev": "Heydər Əliyev",
    "Mathieu Krkou": "Mathieu Kérékou",
    "Blaise Compaor": "Blaise Compaoré",
    "Aljaksandr Lukaenka": "Aljaksandr Lukašenka",
    "Hugo Bnzer Surez": "Hugo Bánzer Suárez",
    "Andrs Pastrana Arango": "Andrés Pastrana Arango",
    "Antnio Mascarenhas Monteiro": "António Mascarenhas Monteiro",
    "Miguel ngel Rodrguez Echeverra": "Miguel Ángel Rodríguez Echeverría",
    "Vclav Havel": "Václav Havel",
    "Hiplito Meja Domnguez": "Hipólito Mejía Domínguez",
    "Lansana Cont": "Lansana Conté",
    "Kumba Ial": "Kumba Ialá",
    "Carlos Roberto Flores Facuss": "Carlos Roberto Flores Facussé",
    "tipe Mesic": "Stipe Mesić",
    "Ferenc Mdl": "Ferenc Mádl",
    "lafur Ragnar Grmsson": "Ólafur Ragnar Grímsson",
    "mile Lahoud": "Émile Lahoud",
    "Joaqum A. Chissano": "Joaquim A. Chissano",
    "Mireya Elisa Moscoso Rodrguez": "Mireya Elisa Moscoso Rodríguez",
    "Jorge Sampaio": "Jorge Sampaio",
    "Luis ngel Gonzlez Macchi": "Luis Ángel González Macchi",
    "Jorge Batlle Ibez": "Jorge Batlle Ibáñez",
    "Hugo Chvez Fras": "Hugo Chávez Frías",
    "Trn Duc Luong": "Trần Đức Lương",
    "Vojislav Kotunica": "Vojislav Koštunica",
    "Leonid Kutma": "Leonid Kutšma",
    "Eduard evardnadze": "Eduard Ševardnadze",
    "Idriss Dby": "Idriss Déby",
    "Gnassingb Eyadma": "Gnassingbé Eyadéma",
    "France-Albert Ren": "France-Albert René",
    "Jos Alexandre Gusmo": "José Alexandre Gusmão"
}

# Aplicar reemplazos ortográficos asegurando el delimitador de celda
for k, v in REEMPLAZOS_PAISES.items():
    contenido = contenido.replace(f"'{k}'", f"'{v}'")

# Aplicar los nombres que llevan comilla interna escapada
for k, v in nombres_apostrofe.items():
    contenido = contenido.replace(f"'{k}'", f"'{v}'")

# Restaurar nombre de la Antártida si quedó vacío
contenido = re.sub(r",\s*'',\s*'Co-administrated'", ", 'Antarctica', 'Co-administrated'", contenido)

# Limpieza final de comillas cuádruples o triples residuales
contenido = re.sub(r"'{3,}", "''", contenido)

with open(archivo_out, 'w', encoding='utf-8') as f:
    f.write(contenido)

print(f"[OK] {archivo_out} generado sin comillas de más y con la sintaxis exacta de PostgreSQL.")