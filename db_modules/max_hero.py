#Max Hero module#
import secrets
from db_modules.db import DB
from hero import Hero, load_hero

def get_new_mhid():
    #Max Hero id generation#
    new_mhid = secrets.token_hex(8)
    while load_max_hero(new_mhid) is not None:
        new_mhid = secrets.token_hex(8)
    return new_mhid

class Max_hero(Hero):
    #Object Max Hero#

    def __init__(
            self, 
            idHero: str,
            Attack: int,
            Defense: int,
            Health: int,
            AttackLB1: int,
            DefenseLB1: int,
            HealthLB1: int,
            AttackLB2: int,
            DefenseLB2: int,
            HealthLB2: int):  
        self.mhid = idHero
        self.Attack = Attack
        self.Defense = Defense
        self.Health = Health
        self.AttackLB1 = AttackLB1
        self.DefenseLB1 = DefenseLB1
        self.HealthLB1 = HealthLB1
        self.AttackLB2 = AttackLB2
        self.DefenseLB2 = DefenseLB2
        self.HealthLB2 = HealthLB2
    
    def store(self):
        #Save max hero into DB#
        try:
            with DB:
                DB.execute(
                    "INSERT INTO Max_hero (id, Attack, Defense, Health, AttackLB1, DefenseLB1, HealthLB1, AttackLB2, DefenseLB2, HealthLB2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (self.mhid, self.Attack, self.Defense, self.Health, self.AttackLB1, self.DefenseLB1, self.HealthLB1, self.AttackLB2, self.DefenseLB2, self.HealthLB2)
                )
        except Exception as e:
            print(f"Error storing max hero: {e}")
    
    def exists(self):
        #Checks if max hero exists in the DB#
        res = DB.execute('SELECT * FROM Max_hero WHERE id=?', (self.mhid,)).fetchone()
        return res is not None

def load_max_hero(mhid: str):
    res = None
    if mhid is not None:
        try:
            with DB:
                res = DB.execute("SELECT * FROM Max_hero WHERE id=?", (mhid,)).fetchone()
        except Exception as e:
            print(f"Error loading max hero: {e}")

    if res is None:
        return None

    mhid, Attack, Defense, Health, AttackLB1, DefenseLB1, HealthLB1, AttackLB2, DefenseLB2, HealthLB2 = res
    max_hero = Max_hero(mhid, Attack, Defense, Health, AttackLB1, DefenseLB1, HealthLB1, AttackLB2, DefenseLB2, HealthLB2)
    return max_hero

def create_max_hero_table():
    #Creates max hero table#
    try:
        with DB:
            DB.execute('''
                CREATE TABLE IF NOT EXISTS Max_hero(
                    id VARCHAR(16),
                    Attack INT,
                    Defense INT,
                    Health INT,
                    AttackLB1 INT,
                    DefenseLB1 INT,
                    HealthLB1 INT,
                    AttackLB2 INT,
                    DefenseLB2 INT,
                    HealthLB2 INT,
                    CONSTRAINT pk_max_hero PRIMARY KEY (id),
                    CONSTRAINT fk_max_hero FOREIGN KEY (id) REFERENCES Hero(id)
                );
            ''')
    except Exception as e:
        print(f"Error creating Max Hero table: {e}")
