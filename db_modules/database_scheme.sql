CREATE TABLE Aether_power(
    id VARCHAR(16),
    Power_name VARCHAR(100),
    Power_description TEXT,
    CONSTRAINT pk_aether_power PRIMARY KEY (id)
);

CREATE TABLE Elemental_type(
    id VARCHAR(16),
    El_type VARCHAR(100),
    Strong_against VARCHAR(100),
    Weak_against VARCHAR(100),
    CONSTRAINT pk_elemental_type PRIMARY KEY (id)
);

CREATE TABLE Ability(
    id VARCHAR(16),
    Ab_name VARCHAR(100),
    Ab_description BIGTEXT,
    CONSTRAINT pk_ability PRIMARY KEY (id)
);

CREATE TABLE Origin(
    id VARCHAR(16),
    Family VARCHAR(100),
    Origin VARCHAR(100),
    Family_Bonus VARCHAR(100),
    CONSTRAINT pk_origin PRIMARY KEY (id)
);

CREATE TABLE Hero(
    id VARCHAR(16),
    Hero_name VARCHAR(100),
    Rarity VARCHAR(100),
    Class VARCHAR(100),
    Mana_speed VARCHAR(50),
    Power_id VARCHAR(16),
    El_type VARCHAR(16),
    Origin VARCHAR(16),
    SpecialSkill TEXT,
    CONSTRAINT pk_hero PRIMARY KEY (id),
    CONSTRAINT fk_hero_origin FOREIGN KEY (Origin) REFERENCES Origin(id),
    CONSTRAINT fk_hero_power FOREIGN KEY (Power_id) REFERENCES Aether_power(id),
    CONSTRAINT fk_hero_el_power FOREIGN KEY (El_type) REFERENCES Elemental_type(id)
);

CREATE TABLE Current_hero(
    id VARCHAR(16),
    Power INT,
    Attack INT,
    Defense INT,
    Health INT,
    Level INT,
    Ascension INT,
    Skill_level INT,
    CONSTRAINT pk_current_hero PRIMARY KEY (id)
    CONSTRAINT fk_current_hero FOREIGN KEY (id) REFERENCES Hero(id)
);

CREATE TABLE Max_hero(
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
    CONSTRAINT pk_max_hero PRIMARY KEY (id)
    CONSTRAINT fk_max_hero FOREIGN KEY (id) REFERENCES Hero(id)
);


CREATE TABLE IF NOT EXISTS Possess(
    idHero VARCHAR(16),
    idAbility VARCHAR(16),
    CONSTRAINT pk_possess PRIMARY KEY (idHero,idAbility),
    CONSTRAINT fk_idHero FOREIGN KEY (idHero) REFERENCES Hero(id),
    CONSTRAINT fk_idAbility FOREIGN KEY (idAbility) REFERENCES Ability(id)
);