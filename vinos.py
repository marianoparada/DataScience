import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Análisis de Encuesta de Vinos",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': 'https://www.example.com/bug',
        'About': "Esta es una aplicación para el análisis de una encuesta sobre consumo de vinos."
    }
)

st.title("Análisis de Encuesta de Vinos")
sheet_name = 'datos_compra_colectiva_analisis' # replace with your own sheet name
sheet_id = '1eQAemgGkOkFA-982dcBtVYG1bvzPRUNrxCHXIYl2Ils' # replace with your sheet's ID
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
df = pd.read_csv(url)

# Diccionario de mapeo de columnas
column_mapping = {
    'Rango etario': 'rango_etario',
    'Género': 'genero',
    '¿Dónde residís?': 'zona',
    '¿En qué barrio?': 'barrio_caba',
    '¿En qué municipio?': 'municipio1',
    '¿En qué municipio?.1': 'municipio2',
    '¿En qué municipio?.2': 'municipio3',
    'Marca Temporal': 'fecha',
    '¿Cuáles estilos de vino consumís con regularidad? ': 'gustos',
    '¿Cuál es tu estilo preferido? ': 'preferido',
    '¿Cuántos vinos abrís en la semana? ': 'vinos_semana',
    '¿Dónde solés comprar?': 'proveedor',
    '¡ÚLTIMA! Si tuvieses que comprar HOY una botella para vos o para compartir con amigos ¿Cuánto gastarías?': 'precio',
    '¿En qué provincia residís?': 'prov_residencia',
    '¿En qué ciudad?': 'ciudad_residencia',
    'Unnamed: 14': 'Unnamed: 15',
    '¡ÚLTIMA! Si tuvieses que comprar HOY una botella para vos o para compartir con amigos ¿Cuánto gastarías?.1': 'Unnamed: 17',
    'Unnamed: 16': 'Unnamed: 16'
}

# Renombrar las columnas del DataFrame de Excel
df.rename(columns=column_mapping, inplace=True)

# Estadísticas generales
total_respuestas = len(df)
total_hombres = df[df['genero'] == 'Masculino'].shape[0]
total_mujeres = df[df['genero'] == 'Femenino'].shape[0]
total_caba = df[df['zona'] == 'CABA'].shape[0]
total_resto = total_respuestas - total_caba

# Presentar las estadísticas generales en formato de texto
st.header("Estadísticas Generales")
st.write(f"**Respuestas :** {total_respuestas}")
st.write(f"**Sexo Masculino:** 👨 {total_hombres} | **Sexo Femenino:** 👩 {total_mujeres}")
st.write(f"**CABA:** 📍 {total_caba} | **Resto:** 🌍 {total_resto}")

# Paso 1: Municipio y Barrio
df['municipio'] = df['municipio1'].fillna(df['municipio2']).fillna(df['municipio3'])
df.drop(['municipio1', 'municipio2', 'municipio3'], axis=1, inplace=True)
df['barrio_caba'].fillna(df['municipio'], inplace=True)
df.rename(columns={'barrio_caba': 'barrio'}, inplace=True)
df.drop('municipio', axis=1, inplace=True)

# Paso 2: El precio
df['precio_numerico'] = pd.to_numeric(df['precio'], errors='coerce')
precio_promedio = df['precio_numerico'].mean()
df['precio_numerico'].fillna(precio_promedio, inplace=True)
df['precio_numerico'] = df['precio_numerico'].astype(int)

# Paso 3: La cantidad
df['cantidad_numerico'] = pd.to_numeric(df['vinos_semana'], errors='coerce')
cantidad_promedio = df['cantidad_numerico'].mean()
df['cantidad_numerico'].fillna(cantidad_promedio, inplace=True)

# Paso 4: Nuevas características
df['gasto_mensual'] = df['precio_numerico'] * df['cantidad_numerico'] * 4

# Paso 5: Rango válido de precio
rango_min = 3000
rango_max = 20000
promedio_rango = df.loc[(df['precio_numerico'] >= rango_min) & (df['precio_numerico'] <= rango_max), 'precio_numerico'].mean().astype(int)
df.loc[(df['precio_numerico'] < rango_min) | (df['precio_numerico'] > rango_max), 'precio_numerico'] = promedio_rango

descriptive_stats = df.describe()

# Presentar las estadísticas descriptivas en formato de texto
st.header("Estadísticas Descriptivas")
st.write(f"**Promedio de precios de vino:** {descriptive_stats['precio_numerico']['mean']:.2f}")
st.write(f"**Mediana de precios de vino:** {descriptive_stats['precio_numerico']['50%']:.2f}")
st.write(f"**Desviación estándar de precios de vino:** {descriptive_stats['precio_numerico']['std']:.2f}")
st.write(f"**Precio mínimo de vino:** {descriptive_stats['precio_numerico']['min']:.2f}")
st.write(f"**Precio máximo de vino:** {descriptive_stats['precio_numerico']['max']:.2f}")
st.write(f"**Promedio de vinos abiertos por semana:** {descriptive_stats['cantidad_numerico']['mean']:.2f}")
st.write(f"**Gasto mensual promedio en vino:** {descriptive_stats['gasto_mensual']['mean']:.2f}")

# Gráficos
st.subheader("Gráficos")

# Densidad según precio de referencia del vino
fig, ax = plt.subplots()
sns.kdeplot(df['precio_numerico'], shade=True, color='skyblue', ax=ax)
mediana = df['precio_numerico'].median()
promedio = df['precio_numerico'].mean()
ax.axvline(mediana, color='red', linestyle='--', label=f'Mediana: {mediana:.2f}')
ax.axvline(promedio, color='green', linestyle='--', label=f'Promedio: {promedio:.2f}')
ax.legend()
ax.set_title('Densidad según precio de referencia del vino')
ax.set_xlabel('Precio')
ax.set_ylabel('Densidad')
st.pyplot(fig)

# Dispersión de Precios por género y varietal
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(df[df['genero'] == 'Masculino'].preferido, df[df['genero'] == 'Masculino']['precio_numerico'], color='skyblue', label='Masculino')
ax.scatter(df[df['genero'] == 'Femenino'].preferido, df[df['genero'] == 'Femenino']['precio_numerico'], color='pink', label='Femenino')
ax.set_title('Dispersión de Precios por género y varietal')
ax.set_xlabel('Fecha')
ax.set_ylabel('Precio')
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Dispersión de Precios por Zona
fig, ax = plt.subplots(figsize=(18, 6))
zonas_unicas = df['zona'].unique()
colores = plt.cm.tab10.colors
for idx, zona in enumerate(zonas_unicas):
    ax.scatter(df[df['zona'] == zona].barrio, df[df['zona'] == zona]['precio_numerico'], color=colores[idx], label=zona)
ax.set_title('Dispersión de Precios por Barrio')
ax.set_xlabel('Índice de Filas')
ax.set_ylabel('Precio')
ax.legend()
ax.set_xticklabels(ax.get_xticklabels(), rotation=75)
ax.grid(True)
st.pyplot(fig)

# Distribución de Precios por Zona
fig, ax = plt.subplots(figsize=(10, 6))
violins = ax.violinplot(dataset=[df[df['zona'] == zona]['precio_numerico'] for zona in df['zona'].unique()], showmeans=False, showmedians=True)
for i, violin in enumerate(violins['bodies']):
    median = df[df['zona'] == df['zona'].unique()[i]]['precio_numerico'].median()
    ax.text(i + 1, median, f'{median:.2f}', horizontalalignment='center', verticalalignment='bottom', fontsize=10, color='black')
ax.set_title('Distribución de Precios por Zona')
ax.set_xlabel('Zona')
ax.set_ylabel('Precio')
ax.set_xticks(range(1, len(df['zona'].unique()) + 1))
ax.set_xticklabels(df['zona'].unique())
ax.grid(True)
st.pyplot(fig)

# Preferencias de estilos de vino por rango etario
fig, ax = plt.subplots(figsize=(10, 6))
pd.crosstab(df['rango_etario'], df['preferido']).plot(kind='bar', stacked=True, ax=ax)
ax.set_title('Preferencias de estilos de vino por rango etario')
ax.set_xlabel('Rango etario')
ax.set_ylabel('Frecuencia')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
ax.legend(title='Estilo de Vino Preferido')
st.pyplot(fig)

# Proveedor elegido por segmento de precio
percentiles = df['precio_numerico'].quantile([0.33, 0.66])
cut_labels = ['bajo', 'medio', 'alto']
cut_bins = [float('-inf'), percentiles.iloc[0], percentiles.iloc[1], float('inf')]
df['precio_categoria'] = pd.cut(df['precio_numerico'], bins=cut_bins, labels=cut_labels, include_lowest=True)
fig, ax = plt.subplots(figsize=(10, 6))
pd.crosstab(df['precio_categoria'], df['proveedor']).plot(kind='barh', stacked=True, ax=ax)
ax.set_title('Proveedor elegido por segmento de precio')
ax.set_xlabel('Frecuencia')
ax.set_ylabel('Rango Etario')
ax.legend(title='Proveedor', bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, axis='x')
plt.tight_layout()
st.pyplot(fig)

# Porcentaje de cada tipo de vino
fig, ax = plt.subplots(figsize=(8, 6))
conteo_vinos = df['preferido'].value_counts()
porcentaje_vinos = conteo_vinos / len(df) * 100
tipos_tintos = ['Tinto con cuerpo', 'Tinto ligero']
otros_vinos = [vino for vino in porcentaje_vinos.index if vino not in tipos_tintos]
colores = {
    'Tinto con cuerpo': '#7F0000',
    'Tinto ligero': '#FF7F50',
    'Dulce (tintos / blancos / rosados)': '#FFC0CB',
    'Rosado': '#FFC0CB',
    'Blanco ligero': '#FFFFE0',
    'Naranjo': '#FFA500',
    'Blanco con cuerpo': '#F0E68C',
    'Espumante': '#F5F5F5',
}
ax.bar(tipos_tintos, porcentaje_vinos[tipos_tintos], color=[colores[tipo] for tipo in tipos_tintos], label='Tintos')
ax.bar(otros_vinos, porcentaje_vinos[otros_vinos], color=[colores[tipo] for tipo in otros_vinos], label='Otros')
ax.set_title('Porcentaje de Tipos de Vino')
ax.set_xlabel('Tipo de Vino')
ax.set_ylabel('Porcentaje')
ax.set_xticklabels(ax.get_xticklabels(), rotation=75)
ax.legend()
st.pyplot(fig)

# Crear una tabla pivotante con la zona y el precio  
pivot_table = df.pivot_table(index='zona', columns='precio_numerico', aggfunc='size', fill_value=0)
# Graficar el mapa de calor  
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot_table, linewidths=1, linecolor='white', cmap='rocket_r', annot=True, fmt='d')
plt.title('Mapa de Calor de precio por botella / Zona')
plt.xlabel('Precio')
plt.ylabel('Zona')
# Mostrar el gráfico en Streamlit  
st.pyplot(fig)


# Crear una tabla pivotante con la zona y el precio  
pivot_table = df.pivot_table(index='cantidad_numerico', columns='genero', aggfunc='size', fill_value=0)
# Graficar el mapa de calor  
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot_table, linewidths=1, linecolor='white', cmap='rocket_r', annot=True, fmt='d')
plt.title('Mapa de calor: Género vs vinos por semana')
plt.xlabel('Precio')
plt.ylabel('Vinos por semana')
# Mostrar el gráfico en Streamlit  
st.pyplot(fig)


# Calcular la tabla de contingencia entre 'preferido' y 'genero'
contingency_table = pd.crosstab(df['preferido'], df['genero'])
custom_colors = {"Masculino": "skyblue", "Femenino": "pink"}
# Graficar la tabla de contingencia como un gráfico de barras apiladas  
fig, ax = plt.subplots(figsize=(10, 6))
contingency_table.plot(kind='bar', stacked=True, color=custom_colors, ax=ax)
plt.title('Relación entre vino preferido y Género')
plt.xlabel('Tipo de vino')
plt.ylabel('Frecuencia')
plt.xticks(rotation=75)
plt.legend(title='Género', bbox_to_anchor=(1.05, 1), loc='upper left')  # Agregar leyenda para el género
# Mostrar el gráfico en Streamlit  
st.pyplot(fig)

df['ubicacion'] = df['zona'] + ', ' + df['barrio']
frecuencia_zonas = df['ubicacion'].value_counts().reset_index()
frecuencia_zonas.columns = ['ubicacion', 'frecuencia']
st.write("Participantes de la encuesta por barrio:", frecuencia_zonas)




# Diccionario de ubicaciones con sus respectivas coordenadas (latitud, longitud)
location_coordinates = {
    "GBA Norte, San Isidro": [-34.4733, -58.5276],
    "CABA, Palermo": [-34.5883, -58.4306],
    "CABA, Belgrano": [-34.5620, -58.4586],
    "CABA, Recoleta": [-34.5869, -58.3925],
    "GBA Norte, Vicente Lopéz": [-34.5291, -58.4824],
    "CABA, Caballito": [-34.6187, -58.4333],
    "CABA, Villa Urquiza": [-34.5686, -58.4879],
    "CABA, Colegiales": [-34.5711, -58.4486],
    "CABA, Nuñez": [-34.5534, -58.4715],
    "CABA, Almagro": [-34.6133, -58.4155],
    "GBA Norte, Tigre": [-34.4258, -58.5793],
    "GBA Sur, Avellaneda": [-34.6632, -58.3653],
    "CABA, Villa Crespo": [-34.5992, -58.4334],
    "CABA, Balvanera": [-34.6096, -58.4057],
    "GBA Norte, Pilar": [-34.4587, -58.9141],
    "CABA, Villa Devoto": [-34.6062, -58.5114],
    "CABA, Boedo": [-34.6301, -58.4135],
    "CABA, Saavedra": [-34.5627, -58.4885],
    "GBA Oeste, La Matanza": [-34.7578, -58.6222],
    "CABA, Coghlan": [-34.5713, -58.4862],
    "CABA, Flores": [-34.6248, -58.4606],
    "GBA Norte, Escobar": [-34.3491, -58.7966],
    "CABA, Chacarita": [-34.5883, -58.4606],
    "CABA, Mataderos": [-34.6545, -58.5038],
    "GBA Oeste, Tres de Febrero": [-34.6091, -58.6112],
    "CABA, Villa Luro": [-34.6391, -58.5167],
    "CABA, Villa Ortúzar": [-34.5833, -58.4717],
    "GBA Sur, Quilmes": [-34.7203, -58.2546],
    "GBA Oeste, Morón": [-34.6534, -58.6197],
    "CABA, Montserrat": [-34.6149, -58.3817],
    "CABA, Villa del Parque": [-34.6055, -58.4924],
    "CABA, Villa Pueyrredón": [-34.5805, -58.5146],
    "GBA Norte, San Miguel": [-34.5432, -58.7258],
    "GBA Sur, Lomas de Zamora": [-34.7597, -58.3996],
    "CABA, Barracas": [-34.6372, -58.3875],
    "GBA Norte, General San Martín": [-34.5769, -58.5306],
    "CABA, Floresta": [-34.6347, -58.4858],
    "GBA Oeste, Moreno": [-34.6346, -58.7918],
    "GBA Sur, Berazategui": [-34.7632, -58.2128],
    "GBA Oeste, Ituzaingó": [-34.6589, -58.6739],
    "GBA Norte, San Fernando": [-34.4442, -58.5611],
    "CABA, San Telmo": [-34.6219, -58.3735],
    "CABA, La Boca": [-34.6348, -58.3625],
    "GBA Sur, Esteban Echeverría": [-34.8185, -58.4594],
    "GBA Oeste, Merlo": [-34.6855, -58.7284],
    "CABA, Parque Chacabuco": [-34.6309, -58.4421],
    "CABA, Parque Chas": [-34.5753, -58.4808],
    "CABA, San Nicolás": [-34.6081, -58.3822],
    "GBA Sur, Florencio Varela": [-34.8321, -58.2763],
    "GBA Sur, Lanús": [-34.7025, -58.3965],
    "CABA, Parque Patricios": [-34.6345, -58.4005],
    "CABA, Liniers": [-34.6453, -58.5278],
    "CABA, La Paternal": [-34.6038, -58.4715],
    "GBA Sur, Almirante Brown": [-34.7904, -58.3958],
    "GBA Norte, Malvinas Argentinas": [-34.5037, -58.7352],
    "GBA Oeste, Hurlingham": [-34.5885, -58.6392],
    "CABA, Retiro": [-34.5944, -58.3747],
    "GBA Norte, José C. Paz": [-34.5177, -58.7746],
    "CABA, Versalles": [-34.6297, -58.5142],
    "GBA Sur, Ezeiza": [-34.8539, -58.5229],
    "CABA, Monte Castro": [-34.6229, -58.5000],
    "CABA, Villa Lugano": [-34.6721, -58.4782],
    "GBA Sur, Presidente Perón": [-34.9047, -58.3933],
    "CABA, San Cristóbal": [-34.6217, -58.4012],
    "CABA, Villa General Mitre": [-34.6061, -58.4671],
    "CABA, Puerto Madero": [-34.6175, -58.3625],
    "CABA, Vélez Sarsfield": [-34.6405, -58.5128]
}

# Participación correspondiente
participation = [
    58, 49, 34, 32, 30, 26, 22, 20, 17, 14, 14, 11, 10, 10, 9, 9, 9, 8, 8, 8,
    7, 6, 6, 6, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3,
    3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1
]

# Crear el mapa centrado en Buenos Aires
m = folium.Map(location=[-34.6037, -58.3816], zoom_start=10)

for i, (location, coords) in enumerate(location_coordinates.items()):
    if i < len(participation):  # Asegurarse de que no se exceda el índice
        lat, lon = coords
        folium.CircleMarker(
            location=[lat, lon],
            radius=participation[i] / 5,  # Escala del tamaño del círculo
            popup=f"{location}: {participation[i]}",
            color="blue",
            fill=True,
            fill_color="blue"
        ).add_to(m)

    # Mostrar el mapa en la aplicación de Streamlit
st.title("Mapa de Participación por Zonas/Barrios")
st_folium(m, width=700, height=500)
