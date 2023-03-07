import pg8000.native

def lambda_handler(event, context):
    if event['config']['first_setup'] == "False":
        return event

    conn = pg8000.native.Connection(
        user = os.environ.get('DB_USERNAME').encode('EUC-JP'),
        password = os.environ.get('DB_PASSWORD').encode('EUC-JP'),
        host = os.environ.get('DB_HOSTNAME'),
        database = os.environ.get('DB_NAME').encode('EUC-JP'),
        port = 5432
    )

    DDLs = 

    conn.run(**DDLs)
    print('finished creating database structure.')

    load_zones = 

    for zone in load_zones:
        cols = ', '.join(f'"{k}"' for k in zone.keys())   
        vals = ', '.join(f':{k}' for k in zone.keys())
        stmt = f"""INSERT INTO "load_zones" ({cols}) VALUES ({vals});"""
        conn.run(stmt, **zone)

    points_of_interest = 

    return event

def insert(table, data, insert_fk = False, **kwargs):
    cols = ', '.join(f'"{k}"' for k in data.keys())
    vals = ', '.join(f':{k}' for k in data.keys())
    # alter this to be specific for each function that sends data to the DB. 
    # how it's written now is just awful.

    if insert_fk:
        foreign_key = kwargs.get('foreign_key')
        foreign_table = kwargs.get('foreign_table')
        where_col = kwargs.get('where_col')
        where_val = kwargs.get('where_val')
        cols += f', {foreign_key}'
        vals += f', :(SELECT {foreign_key} FROM {foreign_table} WHERE {where_col}={where_val})'
    stmt = f"""INSERT INTO "load_zones" ({cols}) VALUES ({vals});"""

https://dba.stackexchange.com/questions/46410/how-do-i-insert-a-row-which-contains-a-foreign-key