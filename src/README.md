# 🚀 Serverless Document Processing Pipeline (S3 + Lambda + Gemini AI + DynamoDB)

Un pipeline **Event-Driven y Serverless** desarrollado con **LocalStack** que automatiza la extracción de datos estructurados desde facturas y documentos no estructurados utilizando la API de **Google Gemini IA**, validación estricta de esquemas con **Pydantic** y almacenamiento persistente NoSQL en **Amazon DynamoDB**.

---

## 🏗️ Arquitectura del Sistema

```mermaid
flowchart TD
    subgraph LocalStack ["📦 LocalStack (Entorno Cloud Local)"]
        S3["🗄️ Amazon S3\n(test-bucket)"]
        Lambda["⚡ AWS Lambda\n(ProcesadorGemini)"]
        TMP["📂 /tmp Storage\n(Descarga temporal)"]
        DynamoDB[("🗄️ Amazon DynamoDB\n(FacturasProcesadas)")]
    end

    subgraph Externo ["☁️ Servicios Externos & Librerías"]
        Gemini["🧠 Google Gemini API\n(gemini-3.8-flash)"]
        Pydantic["🛡️ Pydantic Schema\n(FacturaEstructurada)"]
    end

    User[("📄 Subida de Documento\nfactura.txt")] -->|1. s3:ObjectCreated| S3
    S3 -->|2. S3 Event Trigger (Automático)| Lambda
    Lambda -->|3. Descarga local| TMP
    TMP -->|4. Contenido en texto| Lambda
    Lambda -->|5. Prompt + Texto| Gemini
    Gemini -->|6. JSON sin validar| Lambda
    Lambda -->|7. Validar esquema| Pydantic
    Pydantic -->|8. OK: Datos Validados| Lambda
    Lambda -->|9. Guardar Registro (put_item)| DynamoDB
    Lambda -->|10. Log / Response 200| Output[("🎉 Registro Persistido")]
🛠️ Tecnologías Utilizadas

    Cloud & Serverless: AWS Lambda, Amazon S3, Amazon DynamoDB, LocalStack v4.0.0.

    Lenguaje & Librerías: Python 3.10, Boto3 (AWS SDK), Pydantic v2 (validación de datos).

    AI Integration: Google Gemini API (gemini-3.8-flash).

    DevOps & Entorno: Docker, Linux (Ubuntu/Mint), Git, AWS CLI / awslocal.

🎯 Características Clave

    Arquitectura Orientada a Eventos (Event-Driven): La función Lambda se activa automáticamente al subir un archivo al Bucket de S3 mediante S3 Event Notifications.

    Extracción de Datos No Estructurados: Uso de LLMs para convertir texto libre o documentos desordenados en estructuras de datos procesables.

    Validación de Esquema Estricta: Integración de Pydantic para garantizar tipos de datos válidos (proveedor, total, fecha) antes de guardar en base de datos.

    Persistencia NoSQL: Almacenamiento seguro y escalable de los resultados extraídos en Amazon DynamoDB.

    Desarrollo y Testing Local: Pipeline 100% testable en local usando LocalStack sin incurrir en costes de nube pública.

📁 Estructura del Proyecto
Plaintext

aws-gemini-pipeline/
├── src/
│   └── handler.py          # Código principal de la función AWS Lambda
├── docs/                   # Documentación adicional y diagramas
├── .gitignore              # Filtro para excluir temporales, venv y claves API
├── mi_lambda.zip           # Paquete empaquetado para el despliegue
├── evento_prueba.json      # Evento de prueba simulado de S3
├── README.md               # Documentación principal del proyecto
└── requirements.txt        # Dependencias de Python

💻 Instrucciones de Ejecución en Local
Prerrequisitos

    Docker y LocalStack ejecutándose en local.

    Python 3.10+ en un entorno virtual activo (venv).

    awslocal configurado y clave API de Google Gemini (GEMINI_API_KEY).

1. Preparar la tabla en DynamoDB
Bash

awslocal dynamodb create-table \
    --table-name FacturasProcesadas \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

2. Empaquetar y actualizar la Lambda
Bash

source venv/bin/activate
zip -j mi_lambda.zip src/handler.py

awslocal lambda update-function-code \
  --function-name ProcesadorGemini \
  --zip-file fileb://mi_lambda.zip

3. Probar la extracción y persistencia
Bash

# Subir un archivo al bucket S3 para disparar el flujo
awslocal s3 cp factura.txt s3://test-bucket/factura.txt

# Consultar los datos guardados en DynamoDB
awslocal dynamodb scan --table-name FacturasProcesadas

👨‍💻 Autor

Mohcine Najm - Software & Cloud Developer
