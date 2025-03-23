import boto3
import json
from decimal import Decimal
import time

TIME_WINDOW = 999999  # ➤ Étendre la plage pour tester
TIME_REFERENCE = -1  # ➤ Timestamp trop ancien # ➤ Donne une vraie valeur correspondant à un timestamp de tes données
SENSORS_ID = ["mpu6050_sensor", "alarme_system"]

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, list):
        return [decimal_to_float(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: decimal_to_float(value) for key, value in obj.items()}
    else:
        return obj

def dynamodb_to_dict(obj):
    if isinstance(obj, dict):
        if 'M' in obj:
            return {key: dynamodb_to_dict(value) for key, value in obj['M'].items()}
        elif 'N' in obj:
            return float(obj['N'])
        elif 'S' in obj:
            return str(obj['S']).strip()
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

    sensor_ids = event.get('sensor_ids', SENSORS_ID)

    try:
        # Scan avec filtre sur l’intervalle de temps
        response = table.scan(
            FilterExpression='#t BETWEEN :start_val AND :end_val',
            ExpressionAttributeValues={
                ':start_val': time_lower_bound,
                ':end_val': time_upper_bound
            },
            ExpressionAttributeNames={'#t': 'timestamp'}
        )

        items = response.get('Items', [])

        # Transformation des formats DynamoDB vers Python natif
        converted_items = [dynamodb_to_dict(item) for item in items]
        final_items = [decimal_to_float(item) for item in converted_items]

        # ✅ Filtrer selon payload.sensor_id
        filtered_items = [
            item for item in final_items
            if item.get("payload", {}).get("sensor_id") in sensor_ids
        ]

        return {
            'statusCode': 200,
            'body': json.dumps(filtered_items)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }