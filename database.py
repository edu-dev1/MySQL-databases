"""Módulo de funciones extra para ayudar con la conexión de bases de datos y tablas"""
from mysql.connector import connect

class DataBase:
    '''Una base de datos de MySQL.'''
    def __init__(self, host:str = "localhost",
                 user:str = "root",
                 password:str = "root",
                 db:str = "my_database") -> None:
        """Inicializa una base de datos en MySQL para enviar comandos y/o obtener datos.\n
        Nota:
        \tRequiere instalar el módulo `mysql` haciendo `pip install mysql-connector-python`."""
        self.__user = user
        self.__host = host
        self.__password = password
        self.__db = db

    def __str__(self) -> str:
        return "Base de datos."
    
    def __get_columns(self, table:str) -> list[str]:
        """Obtiene todas las columnas disponibles de la tabla especificada."""
        connection = connect(
            host = self.__host,
            user = self.__user,
            password = self.__password,
            database = self.__db
        )
        cursor = connection.cursor()
        cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}'")
        columns = cursor.fetchall()
        cursor.close()

        columns_table = []

        for column in columns:
            columns_table.append(*column)

        return columns_table
    
    def get_tables(self) -> list[str]:
        """Obtiene todas las tablas disponibles de la base de datos inicializada."""
        connection = connect(
            host = self.__host,
            user = self.__user,
            password = self.__password,
            database = self.__db
        )
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.close()

        __tables = []

        for table in tables:
            __tables.append(*table)

        return __tables
    
    def get_data(self, table:str, columns:tuple|list = []) -> list[tuple]:
        """Retorna una lista con todos los datos de `table`, `[]` si está vacía."""

        if table not in self.get_tables():
            raise ValueError("Tabla errónea.")

        connection = connect(
            host = self.__host,
            user = self.__user,
            password = self.__password,
            database = self.__db
        )
        cursor = connection.cursor()
        
        if not len(columns):
            cursor.execute(f"SELECT * FROM {table}")
            data = cursor.fetchall()
        else:
            if any(column not in self.__get_columns(table) for column in columns):
                raise ValueError("Columna errónea.")
            else:
                cursor.execute(f"SELECT {", ".join(columns)} FROM {table}")
                if len(columns) == 1:
                    data = []

                    for dt in cursor.fetchall():
                        data.append(*dt)
                else:
                    data = cursor.fetchall()
        cursor.close()

        return data if data else [()]
    
    def set_data(self, table:str, **columns_values) -> None:
        """Agrega nuevos datos a la tabla deseada."""
     
        if table not in self.get_tables():
            raise ValueError("Tabla errónea.")   
    
        connection = connect(
            host = self.__host,
            user = self.__user,
            password = self.__password,
            database = self.__db
        )

        columns = list(columns_values.keys())
        values = list(columns_values.values())

        if any(column not in self.__get_columns(table) for column in columns):
            raise ValueError("Columna errónea.")

        cursor = connection.cursor()
        
        placeholders = ", ".join(["%s"] * len(values))
        columns_str = ", ".join(columns)

        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"

        cursor.execute(query, values)
        connection.commit()
        
        cursor.close()

        return None
    
    def clear_table(self, table:str) -> None:
        """Limpia toda la tabla."""
        if table not in self.get_tables():
            raise ValueError("Tabla errónea.")
        
        connection = connect(
            host = self.__host,
            user = self.__user,
            password = self.__password,
            database = self.__db
        )

        cursor = connection.cursor()
        
        cursor.execute(f"DELETE FROM {table}")
        cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")

        connection.commit()
        cursor.close()
        return None
    
    def clear_row(self, table:str, id:int|None = None) -> None:
        """Limpia la fila especificada.\n
        Si `id` es None reiniciando el `id` a 1, si `id` es un entero positivo borra
        esa fila.\n
        Nota:
        \tLa tabla seleccionada debe tener una columna id."""
        if table not in self.get_tables():
            raise ValueError("Tabla errónea.")
        
        if id is not None and id < 0:
            raise ValueError("id debe ser positivo.")
        
        connection = connect(
            host = self.__host,
            user = self.__user,
            password = self.__password,
            database = self.__db
        )

        cursor = connection.cursor()
        
        if id is not None:
            cursor.execute(f"DELETE FROM {table} WHERE id = {id}")

        connection.commit()
        cursor.close()
        return None
    
    def set_id(self, table:str, id:int) -> None:

        if table not in self.get_tables():
            raise ValueError("Tabla errónea.")
        if id < 0:
            raise ValueError("No id's negativos.")
        
        connection = connect(
            host = self.__host,
            user = self.__user,
            password = self.__password,
            database = self.__db
        )

        cursor = connection.cursor()
        cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = {id}")
        connection.commit()
        cursor.close()

        return None
    
    def clear_rows(self, table:str, id_range:tuple[int, int]) -> None:
        """Limpia las filas marcadas por el `id_range` (inicio, fin).\n
        Nota:
        \tLa tabla seleccionada debe tener una columna id."""
        if table not in self.get_tables():
            raise ValueError("Tabla errónea.")
        
        if any(_id < 0 for _id in id_range):
            raise ValueError("id debe ser positivo.")
        
        id_start = id_range[0]
        id_end = id_range[1]

        if id_start > id_end:
            raise ValueError("Rango de inicio mayor que el final.")
        
        connection = connect(
            host = self.__host,
            user = self.__user,
            password = self.__password,
            database = self.__db
        )
        

        cursor = connection.cursor()
        
        cursor.execute(f"DELETE FROM {table} WHERE id BETWEEN {id_start} AND {id_end}")
        
        connection.commit()
        cursor.close()
        return None
    
    def update_data(self, table:str, id:int, **column_newval) -> None:
        '''Actualiza el dato especificado de acuerdo a su `id`.\n
        Nota\n
        \tLa tabla debe tener una columna id.\n
        \tActualiza una columna a la vez.\0
        '''
        connection = connect(
            host = self.__host,
            user = self.__user,
            password = self.__password,
            database = self.__db
        )

        column = "".join(column_newval.keys())
        new_val = list(column_newval.values())[0]

        new_val = "".join(column_newval.values()) if isinstance(new_val, str) else new_val

        val = f"'{new_val}'" if str(new_val).isalpha() else new_val

        cursor = connection.cursor()
        
        cursor.execute(f"UPDATE {table}\
                        SET {column} = {val}\
                        WHERE id = {id};\
                        ")
        connection.commit()
        
        cursor.close()
        return None
