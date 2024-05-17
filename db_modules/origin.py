"""Origin module"""
import secrets
from db_modules.db import DB

def get_new_oid():
    """Origin id generation"""
    new_oid = secrets.token_hex(8)
    while load_origin(new_oid) is not None:
        new_oid = secrets.token_hex(8)
    return new_oid

class Origin:
    """Object Origin"""

    def __init__(
            self, 
            Family: str,
            origin: str,
            Family_Bonus: str):
        self.oid = None
        self.Family = Family
        self.origin = origin
        self.Family_Bonus = Family_Bonus
    
    def store(self):
        """Save origin into DB"""
        if self.oid is None:
            self.oid = get_new_oid()
            try:
                with DB:
                    DB.execute(
                        "INSERT INTO Origin (id, Family, Origin, Family_Bonus) VALUES (?, ?, ?, ?)",
                        (self.oid, self.Family, self.origin, self.Family_Bonus)
                    )
            except Exception as e:
                print(f"Error storing origin: {e}")
    
    def exists(self):
        """Checks if origin exists in the DB"""
        res = DB.execute('SELECT * FROM Origin WHERE id=?', (self.oid,)).fetchone()
        return res is not None

def load_origin(oid: str):
    res = None
    if oid is not None:
        try:
            with DB:
                res = DB.execute("SELECT * FROM Origin WHERE id=?", (oid,)).fetchone()
        except Exception as e:
            print(f"Error loading origin: {e}")

    if res is None:
        return None

    oid, Family, origin, Family_Bonus = res
    o = Origin(Family, origin, Family_Bonus)
    o.oid = oid
    return o

def create_origin_table():
    """Creates origin table"""
    try:
        with DB:
            DB.execute('''
                CREATE TABLE IF NOT EXISTS Origin(
                    id VARCHAR(16),
                    Family VARCHAR(100),
                    Origin VARCHAR(100),
                    Family_Bonus VARCHAR(100),
                    CONSTRAINT pk_origin PRIMARY KEY (id)
                );
            ''')
    except Exception as e:
        print(f"Error creating Origin table: {e}")