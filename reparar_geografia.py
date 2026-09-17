import os
import re

# Diccionario de campos completos exactos (campo original -> campo corregido)
# Se reemplaza únicamente la celda completa, sin tocar letras dentro de otras palabras
CAMPOS_EXACTOS = {
    # Distritos / Estados de Brasil
    "Esprito Santo": "Espírito Santo",
    "Gois": "Goiás",
    "Paran": "Paraná",
    "Amap": "Amapá",
    "Par": "Pará",
    "Cear": "Ceará",
    "Maranho": "Maranhão",
    "Piau": "Piauí",
    "Paraba": "Paraíba",
    "Rondnia": "Rondônia",
    "Rio de Jaúúeiro": "Rio de Janeiro",
    
    # Ciudades de Brasil malformadas en la captura
    "Poááta Grossa": "Ponta Grossa",
    "Ponta Grossa": "Ponta Grossa",
    "Macaééáá": "Macapá",
    "Macap": "Macapá",
    "Jundiaí": "Jundiaí",
    "Jund.a..": "Jundiaí",
    "Junda": "Jundiaí",
    "Ja": "Jaú",
    "Po": "Poá",
    
    # Ciudades principales de Brasil
    "So Paulo": "São Paulo",
    "So Gonalo": "São Gonçalo",
    "Nova Iguau": "Nova Iguaçu",
    "Braslia": "Brasília",
    "Belm": "Belém",
    "Goinia": "Goiânia",
    "So Lus": "São Luís",
    "Macei": "Maceió",
    "So Bernardo do Campo": "São Bernardo do Campo",
    "Santo Andr": "Santo André",
    "Joo Pessoa": "João Pessoa",
    "Jaboato dos Guararapes": "Jaboatão dos Guararapes",
    "So Jos dos Campos": "São José dos Campos",
    "Uberlndia": "Uberlândia",
    "Ribeiro Preto": "Ribeirão Preto",
    "Niteri": "Niterói",
    "Cuiab": "Cuiabá",
    "So Joo de Meriti": "São João de Meriti",
    "Foz do Iguau": "Foz do Iguaçu",
    "Mau": "Mauá",
    "Carapicuba": "Carapicuíba",
    "Aparecida de Goinia": "Aparecida de Goiânia",
    "Maring": "Maringá",
    "Anpolis": "Anápolis",
    "Florianpolis": "Florianópolis",
    "Petrpolis": "Petrópolis",
    "Vitria": "Vitória",
    "Vitria da Conquista": "Vitória da Conquista",
    "Ilhus": "Ilhéus",
    "Santarm": "Santarém",
    "Guaruj": "Guarujá",
    "Ribeiro das Neves": "Ribeirão das Neves",
    "Taubat": "Taubaté",
    "Gravata": "Gravataí",
    "Mossor": "Mossoró",
    "Vrzea Grande": "Várzea Grande",
    "Viamo": "Viamão",
    "Taboo da Serra": "Taboão da Serra",
    "So Jos dos Pinhais": "São José dos Pinhais",
    "Mag": "Magé",
    "So Leopoldo": "São Leopoldo",
    "Marlia": "Marília",
    "So Carlos": "São Carlos",
    "Sumar": "Sumaré",
    "Divinpolis": "Divinópolis",
    "Jequi": "Jequié",
    "Itabora": "Itaboraí",
    "Santa Brbara dOeste": "Santa Bárbara d'Oeste",
    "Jacare": "Jacareí",
    "Araatuba": "Araçatuba",
    "Marab": "Marabá",
    "Cricima": "Criciúma",
    "Maracana": "Maracanaú",
    "Rondonpolis": "Rondonópolis",
    "So Jos": "São José",
    "Nilpolis": "Nilópolis",
    "Camaari": "Camaçari",
    "Itaja": "Itajaí",
    "Chapec": "Chapecó",
    "Hortolndia": "Hortolândia",
    "So Caetano do Sul": "São Caetano do Sul",
    "Parnaba": "Parnaíba",
    "Poos de Caldas": "Poços de Caldas",
    "Terespolis": "Teresópolis",
    "Paranagu": "Paranaguá",
    "Ibirit": "Ibirité",
    "Luzinia": "Luziânia",
    "Maca": "Macaé",
    "Tefilo Otoni": "Teófilo Otoni",
    "Moji-Guau": "Moji-Guaçu",
    "Bag": "Bagé",
    "Bragana Paulista": "Bragança Paulista",
    "Araguana": "Araguaína",
    "Vitria de Santo Anto": "Vitória de Santo Antão",
    "Sabar": "Sabará",
    "Guaratinguet": "Guaratinguetá",
    "Cod": "Codó",
    "Jaragu do Sul": "Jaraguá do Sul",
    "Cubato": "Cubatão",
    "So Jos de Ribamar": "São José de Ribamar",
    "Sertozinho": "Sertãozinho",
    "Eunpolis": "Eunápolis",
    "Tatu": "Tatuí",
    "Ji-Paran": "Ji-Paraná",
    "Camet": "Cametá",
    "Guaba": "Guaíba",
    "So Loureno da Mata": "São Lourenço da Mata",
    "Corumb": "Corumbá",
    "Palhoa": "Palhoça",
    "Barra do Pira": "Barra do Piraí",
    "Bento Gonalves": "Bento Gonçalves",
    "guas Lindas de Gois": "Águas Lindas de Goiás",
    "So Jos do Rio Preto": "São José do Rio Preto",
    "So Vicente": "São Vicente",
    
    # Willemstad / Curazao / Holanda
    "Curaao": "Curaçao",
    "s-Hertogenbosch": "'s-Hertogenbosch",
    "''s-Hertogenbosch": "'s-Hertogenbosch"
}

def limpiar_archivo(nombre_in, nombre_out):
    if not os.path.exists(nombre_in):
        print(f"No existe {nombre_in}")
        return

    with open(nombre_in, 'r', encoding='utf-8', errors='replace') as f:
        lineas = f.readlines()

    lineas_limpias = []
    for l in lineas:
        # 1. Quitar comillas invertidas de MySQL
        l = l.replace("`", "")
        # 2. Reemplazar escapes de MySQL por estándar PostgreSQL
        l = l.replace(r"\'", "''")
        # 3. Eliminar caracteres Unicode de reemplazo corruptos
        l = l.replace('\ufffd', '')
        
        # 4. Reemplazo seguro campo por campo usando delimitadores de comillas simples: 'campo'
        for k, v in CAMPOS_EXACTOS.items():
            l = l.replace(f"'{k}'", f"'{v}'")
            
        # 5. Asegurar que las comillas no queden abiertas
        l = re.sub(r"'Jundiaí\s*,\s*'BRA'", "'Jundiaí', 'BRA'", l)
        
        lineas_limpias.append(l)

    with open(nombre_out, 'w', encoding='utf-8') as f:
        f.writelines(lineas_limpias)

    print(f"[OK] Archivo generado sin colisiones: {nombre_out}")

# Ejecutar sobre city.sql (usa tu archivo de origen)
limpiar_archivo('city.sql', 'city_corregido.sql')