import os
import json
import boto3
import traceback
from pydantic import BaseModel, Field
import google.generativeai as genai

raw_endpoint = os.environ.get('AWS_ENDPOINT_URL', os.environ.get('LOCALSTACK_ENDPOINT', 'http://localstack_main:4566'))

if not raw_endpoint.endswith('/'):
    endpoint_url = f"{raw_endpoint}/"
else:
    endpoint_url = raw_endpoint

s3_client = boto3.client(
    's3', 
    endpoint_url=endpoint_url,
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

class FacturaEstructurada(BaseModel):
    proveedor: str = Field(description="Nombre de la empresa que emite el documento")
    total: float = Field(description="Monto o importe total del documento")
    fecha: str = Field(description="Fecha del documento en formato YYYY-MM-DD")

def lambda_handler(event, context):
    print("📍 [PASO 1] Invocación de Lambda recibida")
    try:
        record = event['Records'][0]['s3']
        bucket_name = record['bucket']['name']
        file_key = record['object']['key']
        print(f"📍 [PASO 2] Evento: Bucket '{bucket_name}', Archivo '{file_key}'")

        download_path = f"/tmp/{os.path.basename(file_key)}"
        print(f"📍 [PASO 3] Descargando de S3 a {download_path}...")
        s3_client.download_file(bucket_name, file_key, download_path)
        print("✅ [PASO 3 OK] Descarga completada")

        with open(download_path, 'r', encoding='utf-8') as f:
            contenido_texto = f.read()
        print("📍 [PASO 4] Lectura de texto completada")

        print("📍 [PASO 5] Enviando a Gemini API...")
        model = genai.GenerativeModel('gemini-3.8-flash')
        prompt = f"""
        Extrae la información clave del siguiente texto y devuelve EXCLUSIVAMENTE
        un objeto JSON que cumpla estrictamente con este esquema:
        {FacturaEstructurada.model_json_schema()}
        
        Texto a procesar:
        {contenido_texto}
        """
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        print("✅ [PASO 5 OK] Respuesta de Gemini recibida")

        print("📍 [PASO 6] Validando con Pydantic...")
        datos_validados = FacturaEstructurada.model_validate_json(response.text)
        print("🎉 [PASO 6 OK] Resultado validado:")
        print(datos_validados.model_dump())

        return {
            'statusCode': 200,
            'body': json.dumps(datos_validados.model_dump())
        }

    except Exception as e:
        print("\n❌ ---------------- ERROR EN EJECUCIÓN ---------------- ❌")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        print(traceback.format_exc())
        print("❌ ------------------------------------------------------ ❌\n")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e), 'type': type(e).__name__})
        }
