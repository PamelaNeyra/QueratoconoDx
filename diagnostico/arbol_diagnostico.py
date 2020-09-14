import pandas as pd
import numpy as np
import joblib as job
from sklearn.tree import  DecisionTreeClassifier

class Diagnostico:
    tiene_enfermedad = ''
    clasificacion = ''
    causas = []

def diagnostico_queratocono(fileName):
    df = pd.read_csv('C:/Users/Pamela/Documents/UNMSM/Tesis II/Sistema/diagnostico/'+fileName)
    x = np.array(df[["Rv F (mm)","Astig F (D)","Asph. Q F","Rh B (mm)","Rv B (mm)","K2 B (D)","Astig B (D)","Asph. Q B","Pachy Apex","Pachy Min","ISV","IVA","IHA","IHD","K1 (D)","K2 (D)","Astig","RPI Max","K max","I-S","AC Depth","AC Depth","Ecc Inf","Cor.Vol.","KPD","Ecc (Front)","Ecc (Back)","Sag. Height Mean [µm]","ACD Apex"]])
    modelo_arbol= job.load('C:/Users/Pamela/Documents/UNMSM/Tesis II/Sistema/diagnostico/modelo_arbol_decision9702.sav')

    prediccion = modelo_arbol.predict(x[0:1])
    resultado = prediccion.tolist()

    clasificacion = ''
    diagnostico = Diagnostico()

    if resultado[0] == 0:
        diagnostico.tiene_enfermedad = 'Con enfermedad'
        diagnostico.clasificacion = 'Queratocono Subclínico'
    elif resultado[0] == 1:
        diagnostico.tiene_enfermedad = 'Con enfermedad'
        diagnostico.clasificacion = 'Queratocono'
    elif resultado[0] == 2:
        diagnostico.tiene_enfermedad = 'Con enfermedad'
        diagnostico.clasificacion = 'Queratocono avanzado'
    elif resultado[0] == 3:
        diagnostico.tiene_enfermedad = 'Sin enfermedad'
        diagnostico.clasificacion = 'Ojo sano'
        
    return diagnostico
