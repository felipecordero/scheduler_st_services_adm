import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import matplotlib

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


st.set_page_config(layout="wide")

# cmap = plt.cm.get_cmap('RdYlGn')

def init_firestore():

    # Inicializar la aplicación de Firebase
    cred = credentials.Certificate(st.secrets["lasalleDB"].to_dict())
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firestore()

# Función para recuperar todos los documentos de una colección
def get_collection_as_json(collection_name):
    collection_ref = db.collection(collection_name)
    documents = collection_ref.stream()

    # Convertir los documentos a una lista de diccionarios
    collection_data = []
    for doc in documents:
        doc_dict = doc.to_dict()
        doc_dict['student_id'] = doc.id  # Agregar el ID del documento al diccionario
        collection_data.append(doc_dict)
    return collection_data

# Ejemplo de uso
collection_name = 'scheduler_student_services'
data = get_collection_as_json(collection_name)

times = ['08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00', '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00']

days = ["monday", "tuesday", "wednesday", "thursday", "friday"]

new_data = []

for student in data:
    for day in days:
        for hour in student[day]:
            new_data.append({day: student["name"], "hour": hour}) 

df = pd.DataFrame(new_data)


names = set()
for col in days:
    names.update(df[col].dropna().unique())

names = list(names)
names.sort()

cmap = matplotlib.colormaps["RdYlGn"]

df_count = df.groupby("hour").count().reset_index().style.background_gradient(cmap=cmap,vmin=0,vmax=5)

new_df = df.groupby("hour")[days].agg(lambda x: '<br>'.join(x.dropna().astype(str))).reset_index()

tab1, tab2 = st.tabs(["Specific Student", "All Students"])

name = tab1.selectbox("Select One Student", options=names)

especific_student = []
especific_students_days = []
for student in data:
    if student["name"] == name:
        for day in days:
            if len(student[day]) > 0:
                especific_students_days.append(day)
                for hour in student[day]:
                    especific_student.append({day: "✓", "hour": hour})

student_df = pd.DataFrame(especific_student, columns=["hour"].extend(especific_students_days))



tab1.write(student_df.groupby("hour")[especific_students_days].agg(lambda x: '<br>'.join(x.dropna().astype(str))).reset_index().to_html(index=False), unsafe_allow_html=True)

col1, col2 = tab2.columns(2)

col1.write(df_count.to_html(index=False, escape=False), unsafe_allow_html=True)

# Display the DataFrame in Streamlit with HTML line breaks rendered correctly
col2.write(new_df.to_html(escape=False, index=True), unsafe_allow_html=True)
