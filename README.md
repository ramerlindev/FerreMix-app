# FerreMix App

Aplicación web para ferretería construida con Flask y Supabase.

## Requisitos Previos

- **Python 3.8+**: [Descargar Python](https://www.python.org/downloads/)
- **Lanzador `py`**: Generalmente se instala por defecto con Python en Windows.

## Instalación Rápida (Windows)

1.  Ejecuta `setup_project.bat` para instalar todo (usa `py` automáticamente).
2.  Configura tu `.env` (duplicando `.env.example`).
3.  Ejecuta `run_server.bat` para iniciar la aplicación.

## Instalación Manual

1.  Crear entorno virtual:
    ```bash
    py -m venv venv
    ```
2.  Activar entorno virtual:
    ```bash
    .\venv\Scripts\activate
    ```
3.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## Base de Datos

1.  Copia el contenido de `supabase_schema.sql`.
2.  Ejecútalo en el SQL Editor de Supabase.

## Ejecución

```bash
run_server.bat
```
O manualmente:
```bash
.\venv\Scripts\activate
flask run
```

Visita `http://127.0.0.1:5000`.
