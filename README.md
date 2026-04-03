# MySQL-databases
Library for MySQL databases.

## Features
- Easy to use.
- Requieres the madule `mysql-connect-python`.

## Example of use
```python
from database import DataBase

'''---Creating the database with it's characteristics---'''
db = DataBase(db = "my_database")

'''---Operations---'''
print(db.get_tables())

db.set_data(table = "my_table", column1 = value1, column2 = value2)
                    
print(db.get_data(table = "my_table", columns = [column1, column2]))