import asyncio
import os
import asyncpg

DATABASE_URL = os.getenv("DATABASE_URL")

async def create_tables():
    """Create database tables and extensions"""
    # Connect to database
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Enable extensions
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
        
        # Execute schema
        with open('../ops/db/init.sql', 'r') as f:
            schema = f.read()
            # Split by individual statements and execute
            statements = schema.split(';')
            for statement in statements:
                if statement.strip():
                    await conn.execute(statement + ';')
        
        print("Database tables created successfully!")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_tables())