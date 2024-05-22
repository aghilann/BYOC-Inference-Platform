import json
from models.MLModel import MLModel  # Correct the import path
from models.Database import Database  # Correct the import path

class MLModelPersistence:
    db: Database
    def __init__(self, db: Database):
        self.db = db

    def get(self, model_name: str, model_version: str) -> MLModel:
        with self.db.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM ml_models
                    WHERE name = %s AND version = %s
                    """,
                    (model_name, model_version)
                )
                row = cursor.fetchone()
                if row:
                    return MLModel(
                        image_url=row[1],
                        exposed_port=row[2],
                        name=row[3],
                        version=row[4],
                        min_replicas=row[5],
                        max_replicas=row[6],
                        description=row[7],
                        created_at=row[8].strftime('%Y-%m-%d %H:%M:%S.%f %z') if row[8] else None,
                        author=row[9],
                        tags=row[10],
                        dependencies=row[11],
                        input_schema=row[12],
                        output_schema=row[13],
                        license=row[14],
                        framework=row[15],
                        hyperparameters=row[16],
                        metrics=row[17],
                        endpoint=row[18],
                        environment_variables=row[19]
                    )
                else:
                    raise ValueError(f"Model {model_name}:{model_version} not found")

    def create_table(self):
        with self.db.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS ml_models (
                        id SERIAL PRIMARY KEY,
                        image_url TEXT NOT NULL,
                        exposed_port INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        version TEXT NOT NULL,
                        min_replicas INTEGER DEFAULT 1,
                        max_replicas INTEGER DEFAULT 10,
                        description TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        author TEXT,
                        tags TEXT[],
                        dependencies JSONB,
                        input_schema TEXT,
                        output_schema TEXT,
                        license TEXT,
                        framework TEXT,
                        hyperparameters JSONB,
                        metrics JSONB,
                        endpoint TEXT,
                        environment_variables JSONB
                    )
                    """
                )
                conn.commit()

    def delete(self, model_name: str, model_version: str) -> bool:
        with self.db.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM ml_models
                    WHERE name = %s AND version = %s
                    """,
                    (model_name, model_version)
                )
                conn.commit()
                if cursor.rowcount > 0:
                    return True
                else:
                    raise ValueError(f"Model metadata {model_name}:{model_version} not found")

    def save(self, model: MLModel):
        self.create_table()
        with self.db.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO ml_models (
                        image_url, exposed_port, name, version, min_replicas, max_replicas, description, created_at, author, tags, 
                        dependencies, input_schema, output_schema, license, framework, hyperparameters, metrics, endpoint, environment_variables
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        model.image_url,
                        model.exposed_port,
                        model.name,
                        model.version,
                        model.min_replicas,
                        model.max_replicas,
                        model.description,
                        model.created_at,
                        model.author,
                        model.tags,
                        json.dumps(model.dependencies) if model.dependencies else None,
                        model.input_schema,
                        model.output_schema,
                        model.license,
                        model.framework,
                        json.dumps(model.hyperparameters) if model.hyperparameters else None,
                        json.dumps(model.metrics) if model.metrics else None,
                        model.endpoint,
                        json.dumps(model.environment_variables) if model.environment_variables else None
                    )
                )
                conn.commit()