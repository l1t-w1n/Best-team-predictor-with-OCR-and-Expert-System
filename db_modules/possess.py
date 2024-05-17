"""Possess module"""
import secrets
from db_modules.db import DB

class Possess:
    """Object Possess"""

    def __init__(
        self,
        idHero: str,
        idAb: str):
        self.idHero = idHero
        self.idAb = idAb

    def store(self):
        """Save possess into DB"""
        try:
            with DB:
                DB.execute(
                    "INSERT INTO Possess (idHero, idAbility) VALUES (?, ?)",
                    (self.idHero, self.idAb)
                )
        except Exception as e:
            print(f"Error storing possess: {e}")

    def exists(self):
        """Checks if possess instance exists in the DB"""
        res = DB.execute('SELECT * FROM Ability WHERE idHero=? AND idAbility=?', (self.idHero,self.idAb)).fetchone()
        return res is not None

def create_possess_table():
    """Create possess table""" 
    try: 
        with DB:
            DB.execute('''
                CREATE TABLE IF NOT EXISTS Possess(
                    idHero VARCHAR(16),
                    idAbility VARCHAR(16),
                    CONSTRAINT pk_possess PRIMARY KEY (idHero,idAbility),
                    CONSTRAINT fk_idHero FOREIGN KEY (idHero) REFERENCES Hero(id),
                    CONSTRAINT fk_idAbility FOREIGN KEY (idAbility) REFERENCES Ability(id)
                );
            ''')
    except Exception as e :
        print(f"Crée mieux la table toi : {e}")