"""Updated Hero module"""
import secrets
from db_modules.db import DB
from db_modules.hero import Hero, load_hero

def get_new_chid():
    """Current Hero id generation"""
    new_chid = secrets.token_hex(8)
    while load_current_hero(new_chid) is not None:
        new_chid = secrets.token_hex(8)
    return new_chid

class Current_hero(Hero):
    """Object Current Hero"""

    def __init__(
            self,
            idHero: str,
            Power: int,
            Attack: int,
            Defense: int,
            Health: int,
            Level: int,
            Ascension: int,
            Skill_level: int):
        self.chid = idHero
        self.Power = Power
        self.Attack = Attack
        self.Defense = Defense
        self.Health = Health
        self.Level = Level
        self.Ascension = Ascension
        self.Skill_level = Skill_level
        
    
    def store(self):
        """Save current hero into DB"""
        

        #check if self.chid is already in the database
        #if true, add (or keep) the strongest power to the database
        try:
            with DB:
                if self.exists(): #If ID is already in the database
                    PowerStored = DB.execute('SELECT Power from Current_hero WHERE id=?',(self.chid,)).fetchone()[0]
                    if int(self.Power)>int(PowerStored): delete_id_current_hero_table(self.chid)
                    else: return

                else:
                    DB.execute(
                        "INSERT INTO Current_hero (id, Power, Attack, Defense, Health, Level, Ascension, Skill_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (self.chid, self.Power, self.Attack, self.Defense, self.Health, self.Level, self.Ascension, self.Skill_level)
                    )
        except Exception as e:
            print(f"Error storing current hero: {e}")

    def exists(self):
        """Checks if current hero exists in the DB"""
        res = DB.execute('SELECT * FROM Current_hero WHERE id=?', (self.chid,)).fetchone()
        return res is not None

def load_current_hero(chid: str):
    res = None
    if chid is not None:
        try:
            with DB:
                res = DB.execute("SELECT * FROM Current_hero WHERE id=?", (chid,)).fetchone()
        except Exception as e:
            print(f"Error loading current hero: {e}")

    if res is None:
        return None

    chid, Power, Attack, Defense, Health, Level, Ascension, Skill_level = res
    current_hero = Current_hero(chid, Power, Attack, Defense, Health, Level, Ascension, Skill_level)
    return current_hero

def create_current_hero_table():
    """Creates current hero table"""
    try:
        with DB:
            DB.execute('''
                CREATE TABLE IF NOT EXISTS Current_hero(
                    id VARCHAR(16),
                    Power INT,
                    Attack INT,
                    Defense INT,
                    Health INT,
                    Level INT,
                    Ascension INT,
                    Skill_level INT,
                    CONSTRAINT pk_current_hero PRIMARY KEY (id),
                    CONSTRAINT fk_current_hero FOREIGN KEY (id) REFERENCES Hero(id)
                );
            ''')
    except Exception as e:
        print(f"Error creating Current Hero table: {e}")

def delete_current_hero_table():
    try:
        with DB:
            DB.execute('DROP TABLE Current_hero')
    except Exception as e:
        print(f"Error deleting Current Hero table: {e}")

def delete_id_current_hero_table(idD):
    try:
        with DB:
            DB.execute('DELETE FROM Current_hero WHERE id=?',(idD))
    except Exception as e:
        print(f"Error deleting id Current Hero table: {e}")
