import sys
from sqlalchemy import create_engine, text

def test_connection():
    print("--- Prueba de Conexión a Base de Datos ---")
    print("Por favor, pega tu cadena de conexión (URI) abajo y presiona Enter:")
    print("Ejemplo: postgresql://postgres.user:pass@host:5432/postgres")
    
    db_url = input("URL: ").strip()
    
    if not db_url:
        print("Error: No ingresaste ninguna URL.")
        return

    # Fix common Supabase/SQLAlchemy issues
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    print(f"\nIntentando conectar a: {db_url.split('@')[-1] if '@' in db_url else '...'}")
    
    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print("\n[ÉXITO] ¡Conexión exitosa!")
            print(f"Versión del servidor: {version}")
    except Exception as e:
        print("\n[ERROR] No se pudo conectar.")
        print(f"Detalle del error: {e}")

if __name__ == "__main__":
    test_connection()
    input("\nPresiona Enter para salir...")
