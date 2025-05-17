import json
import joblib
import os
import numpy as np
from sklearn.ensemble import IsolationForest

# Diccionario para cachear modelos ya cargados
modelos_cache = {}

def lambda_handler(event, context):
    try:        # Extracción y validación de campos requeridos
        required_fields = ['cluster_id', 'presion', 'volumen', 'temperatura', 'mes', 'dia', 'hora']
        missing_fields = [field for field in required_fields if field not in event]

        if missing_fields:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Faltan campos requeridos',
                    'missing_fields': missing_fields
                })
            }
        # Obtener valores y convertirlos a float
        try:
            cluster_id = int(event['cluster_id'])
            presion = float(event['presion'])
            volumen = float(event['volumen'])
            temperatura = float(event['temperatura'])

            mes = int(event['mes'])
            dia = int(event['dia'])
            hora = int(event['hora'])
        except ValueError as ve:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Los valores deben ser numéricos',
                    'details': str(ve)
                })
            }

        # Crear vector de entrada (corregido: fuera del bloque try/except)
        X_nuevo = np.array([[presion, volumen, temperatura]])
            
        modelo_path = f"modelos/modelo_cluster_{cluster_id}.pkl"
        # Carga
        if cluster_id not in modelos_cache:
            if not os.path.exists(modelo_path):
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': f"Modelo para cluster_id={cluster_id} no encontrado"})
                }
            obj = joblib.load(modelo_path)
            modelos_cache[cluster_id] = obj
        else:
            obj = modelos_cache[cluster_id]
            
        model = obj['modelo']
        umbral = obj['umbral']

        scores = -model.decision_function(X_nuevo)
        y_pred = (scores > umbral).astype(int)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'prediccion': y_pred.tolist(),
                'scores': scores.tolist(),
                'umbral': float(umbral)
            })
        }

    except FileNotFoundError:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f"Modelo para cluster_id={cluster_id} no encontrado"
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'details': str(e)
            })
        }