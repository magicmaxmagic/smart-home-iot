import boto3
import json
from decimal import Decimal
import time

TIME_WINDOW = 180  # Fenêtre temporelle en secondes
TIME_REFERENCE = 1742099300  # Temps de référence (-1 pour maintenant, sinon donner le timestamp)
SENSORS_ID = ["MPU6050_1", " _id"]  # ID des capteurs à récupérer

def decimal_to_float(obj):
    """Convertit récursivement Decimal en float."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, list):
        return [decimal_to_float(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: decimal_to_float(value) for key, value in obj.items()}
    else:
        return obj

def dynamodb_to_dict(obj):
    """Convertit un objet DynamoDB (M, N, S, L) en JSON normal."""
    if isinstance(obj, dict):
        if 'M' in obj:
            return {key: dynamodb_to_dict(value) for key, value in obj['M'].items()}
        elif 'N' in obj:
            return float(obj['N'])  # Convertit N en float
        elif 'S' in obj:
            return str(obj['S']).strip()  # Convertit S en string et enlève les espaces
        elif 'L' in obj:
            return [dynamodb_to_dict(item) for item in obj['L']]
        else:
            return {key: dynamodb_to_dict(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [dynamodb_to_dict(item) for item in obj]
    else:
        return obj

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('mpu6050_data')
    time_upper_bound = int(time.time()) if TIME_REFERENCE == -1 else TIME_REFERENCE
    time_lower_bound = time_upper_bound - TIME_WINDOW
    sensor_ids = event.get('sensor_ids')
    if sensor_ids is None or len(sensor_ids) == 0:
        sensor_ids = SENSORS_ID

    try:
        sensor_id_placeholders = [f":sensor_val_{i}" for i in range(len(sensor_ids))]
        sensor_id_expression = f"sensor_id IN ({', '.join(sensor_id_placeholders)})"

        expression_attribute_values = {
            ':start_val': time_lower_bound,
            ':end_val': time_upper_bound,
        }
        expression_attribute_values.update({sensor_id_placeholders[i]: sensor_ids[i] for i in range(len(sensor_ids))})

        query_expression = f'#t >= :start_val AND #t <= :end_val AND {sensor_id_expression}'

        print(f"Attempting to fetch data with query: {query_expression} and values: {expression_attribute_values}")

        response = table.scan(
            FilterExpression=query_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames={'#t': 'timestamp'}
        )

        # response = table.scan(Limit=50)  # Récupérer plus d'éléments pour s'assurer qu'on a des valeurs correctes
        items = response.get('Items', [])

        # Convertir DynamoDB JSON → Standard JSON
        converted_items = [dynamodb_to_dict(item) for item in items]

        # Convertir Decimal en float
        final_items = [decimal_to_float(item) for item in converted_items]

        # Filtrer uniquement `sensor_id="MPU6050_1"`
        # filtered_items = [item for item in final_items if item.get("sensor_id") == "MPU6050_1"]
        filtered_items = final_items

        return {
            'statusCode': 200,
            'body': json.dumps(filtered_items)  # ✅ Maintenant, uniquement les bonnes valeurs sont retournées !
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }