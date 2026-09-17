import os
import re

# ==============================================================================
# 1. DICCIONARIO EXACTO PARA COUNTRY.SQL
# ==============================================================================
CAMPOS_COUNTRY = {
    # Nombres de países y territorios
    "Cte dIvoire": "Côte d'Ivoire",
    "Rpublique Dmocratique du Congo": "République Démocratique du Congo",
    "Bnin": "Bénin",
    "Centrafrique/B-Afrka": "Centrafrique/Bê-Afrîka",
    "Froyar": "Føroyar",
    "Bouvetya": "Bouvetøya",
    "Kalaallit Nunaat/Grnland": "Kalaallit Nunaat/Grønland",
    "esko": "Česko",
    "Kpros/Kibris": "Kýpros/Kıbrıs",
    "Espaa": "España",
    "YeItyopiya": "YeItyop'iya",
    "Hati/Dayti": "Haïti/Dayti",
    "sland": "Ísland",
    "Yisrael/Israil": "Yisra'el/Isrā'īl",
    "Al-Iraq": "Al-'Irāq",
    "Kpucha": "Kâmpŭchéa",
    "Taehan Minguk (Namhan)": "Taehan Min'guk (Namhan)",
    "Choson Minjujuui Inmin Konghwaguk (Bukhan)": "Choson Minjujuui In'min Konghwaguk (Bukhan)",
    "Mxico": "México",
    "Moambique": "Moçambique",
    "Nouvelle-Caldonie": "Nouvelle-Calédonie",
    "Per/Piruw": "Perú/Piruw",
    "Repblica Dominicana": "República Dominicana",
    "Romnia": "România",
    "Sngal/Sounougal": "Sénégal/Sounougal",
    "So Tom e Prncipe": "São Tomé e Príncipe",
    "So Tom e Prncipe": "São Tomé e Príncipe",
    "Tshad/Tchad": "Tchad/Tšad",
    "Trkmenostan": "Türkmenostan",
    "Trkiye": "Türkiye",
    "Tai-wan": "T'ai-wan",
    "zbekiston": "Oʻzbekiston",
    "Zhongquo": "Zhongguo",
    "Shqipria": "Shqipëria",
    "Azrbaycan": "Azərbaycan",
    "Belgi/Belgique": "België/Belgique",
    "sterreich": "Österreich",
    "Al-Jazair/Algrie": "Al-Jazā'ir/Algérie",
    "Terres australes franaises": "Terres australes françaises",
    "Guyane franaise": "Guyane française",
    "Polynsie franaise": "Polynésie française",
    "Runion": "Réunion",

    # Jefes de Estado / Gobernantes
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
    "Abdelaziz Bouteflika": "Abdelaziz Bouteflika",
    "Lansana Cont": "Lansana Conté",
    "Kumba Ial": "Kumba Ialá",
    "Carlos Roberto Flores Facuss": "Carlos Roberto Flores Facussé",
    "tipe Mesic": "Stipe Mesić",
    "Ferenc Mdl": "Ferenc Mádl",
    "mary McAleese": "Mary McAleese",
    "lafur Ragnar Grmsson": "Ólafur Ragnar Grímsson",
    "mile Lahoud": "Émile Lahoud",
    "Maaouiya Ould SidAhmad Taya": "Maaouiya Ould Sid'Ahmad Taya",
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
    "Jos Alexandre Gusmo": "José Alexandre Gusmão",

    # Regiones / Formas de gobierno
    "People''sRepublic": "People's Republic"
}

# ==============================================================================
# 2. DICCIONARIO EXACTO PARA COUNTRYLANGUAGE.SQL
# ==============================================================================
CAMPOS_LANGUAGE = {
    "Aimar": "Aymara",
    "Guaran": "Guaraní",
    "Ketua": "Quechua",
    "Mantu": "Manchu",
    "Kekch": "K'ekchi",
    "Quich": "K'iche'",
    "Tam": "Cham",
    "Nhuatl": "Nahuatl",
    "Otom": "Otomí",
    "Guaym": "Guaymí",
    "Mahor": "Mahoré"
}

def procesar_country(archivo_in, archivo_out):
    if not os.path.exists(archivo_in):
        print(f"[-] No se encontró: {archivo_in}")
        return

    with open(archivo_in, 'r', encoding='utf-8', errors='replace') as f:
        lineas = f.readlines()

    lineas_ok = []
    for l in lineas:
        l = l.replace("`", "")
        l = l.replace(r"\'", "''")
        l = l.replace('\ufffd', '')

        for k, v in CAMPOS_COUNTRY.items():
            l = l.replace(f"'{k}'", f"'{v}'")

        # Restaurar nombre de la Antártida si quedó como comillas vacías
        l = re.sub(r",\s*'',\s*'Co-administrated'", ", 'Antarctica', 'Co-administrated'", l)
        lineas_ok.append(l)

    with open(archivo_out, 'w', encoding='utf-8') as f:
        f.writelines(lineas_ok)
    print(f"[OK] Generado: {archivo_out}")

def procesar_language(archivo_in, archivo_out):
    if not os.path.exists(archivo_in):
        print(f"[-] No se encontró: {archivo_in}")
        return

    with open(archivo_in, 'r', encoding='utf-8', errors='replace') as f:
        lineas = f.readlines()

    lineas_ok = []
    for l in lineas:
        l = l.replace("`", "")
        l = l.replace(r"\'", "''")
        l = l.replace('\ufffd', '')

        for k, v in CAMPOS_LANGUAGE.items():
            l = l.replace(f"'{k}'", f"'{v}'")

        # Conversión de booleanos MySQL ('T'/'F' o 't'/'f') al estándar PostgreSQL
        l = re.sub(r",\s*'[Tt]',", ", TRUE,", l)
        l = re.sub(r",\s*'[Ff]',", ", FALSE,", l)

        lineas_ok.append(l)

    with open(archivo_out, 'w', encoding='utf-8') as f:
        f.writelines(lineas_ok)
    print(f"[OK] Generado: {archivo_out}")

# Ejecución sobre los dos archivos
procesar_country('country.sql', 'country_corregido.sql')
procesar_language('countrylanguage.sql', 'countrylanguage_corregido.sql')