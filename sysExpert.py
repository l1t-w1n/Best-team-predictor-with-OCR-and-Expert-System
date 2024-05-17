from db_modules.db import DB
import random

#On essaie de renvoyer la position du début de la chaine 
def isIn(String,motif):
    #print("isIn function called with String:", String, "and motif:", motif)
    n = len(motif)
    s = len(String)
    if(n>s):
        #print("motif length is greater than String length, returning -1")
        return -1
    elif(String[:n] == motif):
        #print("motif found at the beginning of String, returning", n-1)
        return n-1
    else :
        String = String[1:]
        #print("motif not found, calling isIn recursively with String:", String, "and motif:", motif)
        res = isIn(String,motif)
        if res == -1 :
            #print("motif not found in recursive call, returning -1")
            return -1
        else :
            #print("motif found in recursive call, returning", 1+res)
            return 1+res

def formate(SS):
    print("formate function called with SS:", SS)
    p = SS.find('|')
    if(p == -1):
        print("No '|' found in SS, printing 'abadakor'")
        print("Returning SS unchanged")
        print("SS after returning:", SS)
        return "abadakor"
    else:
        print("Found '|' at position", p)
        SS = SS[p+2:]
       # print("Removing characters before '|' and two characters after '|' in SS, returning new SS")
        #print("New SS:", SS)
        return SS

#Equipe est une liste d'ID et SC un liste de liste avec SC[i][j] = la valeur du prédicat Same_color pour les héros dont les ID sont en case i et j de Equipe
def initSC(Equipe):
    #print("initSC function called with Equipe:", Equipe)
    SC=[]
    for i in range(len(Equipe)):
        colorI = DB.execute("Select e.El_type From Elemental_type e Join Hero h On e.id = h.El_type Where h.id='"+Equipe[i]+"'").fetchone()[0]
        SC.append([])
        for j in range(len(Equipe)):
            colorJ = DB.execute("Select e.El_type From Elemental_type e Join Hero h On e.id = h.El_type Where h.id='"+Equipe[j]+"'").fetchone()[0]
            if(colorI == colorJ):
                SC[i].append(1)
            else :
                SC[i].append(0)
    #print("SC initialized:", SC)
    return SC

def initMana(Equipe):
    #print("initMana function called with Equipe:", Equipe)
    VSM = [0]*len(Equipe)
    SM = [0]*len(Equipe)
    AM = [0]*len(Equipe)
    FM = [0]*len(Equipe)
    VFM = [0]*len(Equipe)
    for i in range(len(Equipe)):
        manaI = DB.execute("Select Mana_speed From Hero Where id='"+Equipe[i]+"'").fetchone()[0]
        match manaI:
            case 'Fast':
                FM[i]=1
            case 'Average':
                AM[i]=1
            case 'Slow':
                SM[i]=1
            case 'Very Fast':
                VFM[i]=1
            case 'Very Slow':
                VSM[i]=1
    #print("Mana initialized: VSM:", VSM, "SM:", SM, "AM:", AM, "FM:", FM, "VFM:", VFM)
    return (VSM,SM,AM,FM,VFM)

def initBonus(Equipe):
    #print("initBonus function called with Equipe:", Equipe)
    LowDefBonus = [0]*len(Equipe) # cette chose n'as pas l'air d'exister 
    HealingBonus = [0]*len(Equipe)
    DodgeBonus = [0]*len(Equipe)
    DamageReduction = [0]*len(Equipe)
    TauntBonus = [0]*len(Equipe)
    RageBonus = [0]*len(Equipe)
    AttackBonus = [0]*len(Equipe)
    for i in range(len(Equipe)):
        atPower = DB.execute("Select ap.Power_name From hero h Join Aether_power ap On h.Power_id=ap.id Where h.id='"+Equipe[i]+"'").fetchone()[0]
        match atPower:
            case 'Dodge':
                DodgeBonus[i]=1
            case 'Damage Reduction':
                DamageReduction[i]=1
            case 'Taunt':
                TauntBonus[i]=1
            case 'Regen':
                HealingBonus[i]=1
            case 'Boosted Regen':
                HealingBonus[i]=1
            case 'Rage' :
                RageBonus[i] = 1
            case 'Attack Up':
                AttackBonus[i] = 1
    #print("Bonuses initialized: HealingBonus:", HealingBonus, "DodgeBonus:", DodgeBonus, "DamageReduction:", DamageReduction, "TauntBonus:", TauntBonus, "RageBonus:", RageBonus, "AttackBonus:", AttackBonus)
    return (LowDefBonus,HealingBonus,DodgeBonus,DamageReduction,TauntBonus,RageBonus,AttackBonus)

def initTypeDamage(Equipe):
    #print("initTypeDamage function called with Equipe:", Equipe)
    triShot = [0]*5
    sniper = [0]*5
    justShootEveryone = [0]*5
    triShotDesc = "damage to the target and nearby enemies"
    BoomBoomDesc = "damage to all enemies"
    triShotDesc2 = "damage to the nearby enemies"
    for i in range(len(Equipe)):
        SS = DB.execute("Select SpecialSkill from hero where id='"+Equipe[i]+"'").fetchone()[0]
        if(SS != None):
            if(isIn(SS, triShotDesc)!=-1):
                triShot[i]=1
            elif(isIn(SS,triShotDesc2)!=-1):
                triShot[i]=1
            elif(isIn(SS, BoomBoomDesc)!=-1):
                justShootEveryone[i] = 1
            else :
                sniper[i]=1
    #print("Type damage initialized: triShot:", triShot, "sniper:", sniper, "justShootEveryone:", justShootEveryone)
    return (triShot,sniper,justShootEveryone)

def init_DispelsBuff_Bonus(Equipe):
    #print("init_DispelsBuff_Bonus function called with Equipe:", Equipe)
    disB = [0]*len(Equipe)
    for i in range(len(Equipe)):
        SS = DB.execute("Select SpecialSkill From Hero where id='"+Equipe[i]+"'").fetchone()[0]
        if(SS != None):
            p = isIn(SS, "Dispels buffs from all enemies")
            if(p != -1):
                disB[i]=1
            else : 
                p = isIn(SS, "Dispels buffs from the target")
                if p != -1:
                    disB[i]=1
    #print("Dispel Buff Bonus initialized:", disB)
    return disB

def init_LowerEnemieStats(Equipe):
    #print("init_LowerEnemieStats function called with Equipe:", Equipe)
    lS = [0]*len(Equipe)
    for i in range(len(Equipe)):
        SS = DB.execute("Select SpecialSkill From Hero where id='"+Equipe[i]+"'").fetchone()[0]
        if(SS != None):
            p = isIn(SS, "The target and nearby enemies get -")
            if(p != -1):
                lS[i]=1
            else :
                p = isIn(SS, "All enemies get -")
                if(p != -1):
                    lS[i]=1
    #print("Lower Enemy Stats initialized:", lS)
    return lS

def init_DamageBuff_Bonus(Equipe):
    #print("init_DamageBuff_Bonus function called with Equipe:", Equipe)
    dB = [0]*len(Equipe)
    for i in range(len(Equipe)):
        SS = DB.execute("Select SpecialSkill From Hero where id='"+Equipe[i]+"'").fetchone()[0]
        if(SS != None):
            p = isIn(SS, "All damage all enemies receive is increase by +")#Celui la marche l'autre j'ai pas d'exemple qui corresponde dans ma bd 
            if(p != -1):
                dB[i]=1
            else :
                p = isIn(SS, "All allies gets +")
                if(p != -1):
                    p+=1
                    while(SS[p].isdigit() or SS[p]=="%"):
                        p+=1
                    if(SS[p:p+len(" normal damage")] == " normal damage"):
                        dB[i]=1
    #print("Damage Buff Bonus initialized:", dB)
    return dB

def init_HealingBuff_Bonus(Equipe):
    #print("init_HealingBuff_Bonus function called with Equipe:", Equipe)
    iH=[0]*len(Equipe)
    for i in range(len(Equipe)):
        SS = DB.execute("Select SpecialSkill From Hero where id='"+Equipe[i]+"'").fetchone()[0]
        if(SS!=None):
            p = isIn(SS,"All allies regenerate ")
            if(p!=-1):
                #on passe tout les numéros puis on cherche la suite du motif a reconnaitre 
                p+=1
                while(SS[p].isdigit() or SS[p]=="%"):
                    p+=1
                if SS[p:p+3] == " HP" :
                    #un motif a été reconnu dans son entièreté, le prédicat HealingBuff_Bonus vaut vrai pour ce terme 
                    iH[i]=1
            else :
                #on cherche l'autre motif 
                p = isIn(SS,"Recovers ")
                if p != -1 :
                    #on passe tout les numéros puis on cherche la suite du motif a reconnaitre 
                    p+=1
                    while(SS[p].isdigit() or SS[p]=="%"):
                        p+=1
                    if SS[p:p+len(" health for all allies")] == " health for all allies" :
                         #un motif a été reconnu dans son entièreté, le prédicat HealingBuff_Bonus vaut vrai pour ce terme 
                        iH[i]=1
    #print("Healing Buff Bonus initialized:", iH)
    return iH

def init_BoostedHealth_Bonus(Equipe):
    #print("init_BoostedHealth_Bonus function called with Equipe:", Equipe)
    bH = [0]*len(Equipe)
    for i in range(len(Equipe)):
        SS = DB.execute("Select SpecialSkill From Hero where id='"+Equipe[i]+"'").fetchone()[0]
        if(SS != None):
            p = isIn(SS, "Boosts health for all allies") # a déjà marché 
            if(p != -1):
                bH[i]=1
            else :
                p = isIn(SS, "Boosts health of all allies")# a déjà marché
                if( p != -1):
                    bH[i]=1
                else:
                    p = isIn(SS, "All allies regenerate ")
                    if p != -1 :
                        #on passe tout les numéros puis on cherche la suite du motif a reconnaitre 
                        p+=1
                        while(SS[p].isdigit() or SS[p]=="%"):
                            p+=1
                        if(SS[p:p+len(" boosted health")] == " boosted health"):
                            bH[i]=1
    #print("Boosted Health Bonus initialized:", bH)
    return bH

def init_Cleanses_Bonus(Equipe):
    #print("init_Cleanses_Bonus function called with Equipe:", Equipe)
    C = [0]*len(Equipe)
    for i in range(len(Equipe)):
        SS = DB.execute("Select SpecialSkill From Hero where id='"+Equipe[i]+"'").fetchone()[0]
        if(SS != None):
            p = isIn(SS, "Cleanses")
            if(p != -1):
                C[i]=1
    #print("Cleanses Bonus initialized:", C)
    return C

def init_Revive_Bonus(Equipe):
    #print("init_Revive_Bonus function called with Equipe:", Equipe)
    R = [0]*len(Equipe)
    for i in range(len(Equipe)):
        SS = DB.execute("Select SpecialSkill From Hero where id='"+Equipe[i]+"'").fetchone()[0]
        if(SS != None):
            p = isIn(SS, " chance to get revived")
            if(p != -1):
                R[i]=1
    #print("Revive Bonus initialized:", R)
    return R

def init_strongVsAdvCol(Equipe,CoulAdv):
    #print("init_strongVsAdvCol function called with Equipe:", Equipe, "and CoulAdv:", CoulAdv)
    sAC = [0]*len(Equipe)
    for i in range(len(Equipe)):
        Coul = DB.execute("Select e.Strong_against From Hero h Join Elemental_type e On h.El_type = e.id Where h.id='"+Equipe[i]+"'").fetchone()[0]
        if(Coul == CoulAdv):
            sAC[i]=1
    #print("Strong vs. Adv Col initialized:", sAC)
    return sAC

####### sous-formules 
def isHealer(x,iH,bH):
    #print("isHealer function called with x:", x, "iH:", iH, "bH:", bH)
    return iH[x]+bH[x]>0

def isSoutien(x,disB,lS,dB,iH,bH,C,R):
    #print("isSoutien function called with x:", x, "disB:", disB, "lS:", lS, "dB:", dB, "iH:", iH, "bH:", bH, "C:", C, "R:", R)
    return disB[x]+lS[x]+dB[x]+iH[x],bH[x],C[x],R[x]>0

def calcul_atLeast3Frappeur(Equipe,VFM,FM,AM,SC):
    #print("calcul_atLeast3Frappeur function called with Equipe:", Equipe, "VFM:", VFM, "FM:", FM, "AM:", AM, "SC:", SC)
    res = False
    for i in range(len(Equipe)):
        for j in range(i+1,len(Equipe)):
            for k in range(j+1,len(Equipe)):
                sat1 = VFM[Equipe[i]]*VFM[Equipe[j]]*VFM[Equipe[k]] + FM[Equipe[i]]*FM[Equipe[j]]*FM[Equipe[k]] + AM[Equipe[i]]*AM[Equipe[j]]*AM[Equipe[k]]
                if(sat1 > 0):
                    sat2 = SC[Equipe[i]][Equipe[j]] * SC[Equipe[j]][Equipe[k]] * SC[Equipe[i]][Equipe[k]]
                    if(sat2 == 1):
                        return (True,i,j,k)
    return (False,-1,-1,-1)

def calcul_atLeast2Soutiens(Equipe,disB,lS,dB,iH,bH,C,R):
    #print("calcul_atLeast2Soutiens function called with Equipe:", Equipe, "disB:", disB, "lS:", lS, "dB:", dB, "iH:", iH, "bH:", bH, "C:", C, "R:", R)
    for i in range(len(Equipe)):
        for j in range(i+1,len(Equipe)):
            if(isHealer(Equipe[i], iH, bH) and isSoutien(Equipe[j], disB, lS, dB, iH, bH, C, R) ):
                return (True,i,j)
            if(isHealer(Equipe[j], iH, bH) and isSoutien(Equipe[i], disB, lS, dB, iH, bH, C, R)):
                return (True,j,i)
    return (False,-1,-1) 

def calcul_3_2(Equipe,SC):
    #print("calcul_3_2 function called with Equipe:", Equipe, "SC:", SC)
    for i in range(len(Equipe)):
        for j in range(i+1,len(Equipe)):
            for k in range(j+1,len(Equipe)):
                sat1 = SC[Equipe[i]][Equipe[j]]*SC[Equipe[i]][Equipe[k]]*SC[Equipe[j]][Equipe[k]]
                if(sat1>0):
                    sat2 = True
                    for l in range(len(Equipe)):
                        if( (l!=i and l!=j and l!=k) ): #Comparer i et j revient a comparer Equipe[i] et Equipe[j] car il ne peut y avoir deux fois le même Héro dans Equipe
                            for m in range(l+1,len(Equipe)):
                                if(m!=i and m!=j and m!=k and m!=l):
                                    if( not(SC[Equipe[m]][Equipe[i]]==0 and SC[Equipe[l]][Equipe[i]]==0)):
                                        sat = False 
                    if(sat2):
                        return True
    return False 

#Moteur d'inférence
def lesProblemes(Equipe,SC,VFM,FM,AM,disB,lS,dB,iH,bH,C,R,sAC):
    #print("lesProblemes function called with Equipe:", Equipe, "SC:", SC, "VFM:", VFM, "FM:", FM, "AM:", AM, "disB:", disB, "lS:", lS, "dB:", dB, "iH:", iH, "bH:", bH, "C:", C, "R:", R, "sAC:", sAC)
    #instanciation des Prédicats (uniquement ceux utiliser par les règles dans cette version)

    #calcul des Règles 
    tactique = calcul_3_2(Equipe, SC)
    if(tactique):
        aL3f = calcul_atLeast3Frappeur(Equipe, VFM, FM, AM ,SC)
        res = aL3f[0]
        f1 = aL3f[1]
        f2 = aL3f[2]
        f3 = aL3f[3]
        if(res):
            aL2s = calcul_atLeast2Soutiens(Equipe, disB, lS, dB, iH, bH, C, R)
            res = aL2s[0]
            h = aL2s[1]
            s = aL2s[2]
            if(res):
                if(sAC[Equipe[f1]] == 1):#Comme a ce stade on sait que f1 f2 et f3 sont tous de la  même couleur on teste qu'un 
                    return (True,f1,f2,f3,h,s)
    return (False,-1,-1,-1,-1,-1)

def Jour5SansVoirLeSoleil(OnSeCroiraitEnBretagne, SC, VFM, FM, AM, disB, lS, dB, iH, bH, C, R, sAC):
    #print("Jour5SansVoirLeSoleil function called with OnSeCroiraitEnBretagne:", OnSeCroiraitEnBretagne, "SC:", SC, "VFM:", VFM, "FM:", FM, "AM:", AM, "disB:", disB, "lS:", lS, "dB:", dB, "iH:", iH, "bH:", bH, "C:", C, "R:", R, "sAC:", sAC)
    trucsQuiMarchent = []
    n = len(OnSeCroiraitEnBretagne)
    for i in range(n):
        for j in range(i+1,n):
            for k in range(j+1,n):
                for l in range(k+1,n):
                    for m in range(l+1,n):
                        Equipe = [i,j,k,l,m]
                        # Si l'équipe vérifie les règles alors on l'ajoute aux trucs qui marchent
                        (res,f1,f2,f3,h,s) = lesProblemes(Equipe, SC, VFM, FM, AM, disB, lS, dB, iH, bH, C, R, sAC)
                        if(res):
                            trucsQuiMarchent.append((Equipe,f1,f2,f3,h,s))
    return trucsQuiMarchent

def classementDégat(Deck,Class,f1,f2,f3):
    #print("classementDégat function called with Deck:", Deck, "Class:", Class, "f1:", f1, "f2:", f2, "f3:", f3)
    #Il vas y avoir big problème içi
    tier1 = []
    tier2 = []
    ClassSp = []
    for indiceEquipe in range(len(Class)):
        EquipeID = [Deck[e] for e in Class[indiceEquipe]]
        (trishot,sniper,justShootEveryone) = initTypeDamage(EquipeID)
        ClassSp.append((trishot,sniper,justShootEveryone))
        if(trishot[f1]==1) and (trishot[f2]==1) and (trishot[f3]==1):
            tier1.append(indiceEquipe)
        else : 
            tier2.append(indiceEquipe)
    if(len(tier1)>0):
        if(len(tier1)==1):
            return tier1[0]
        else :
            max = 0
            best = -1
            for i in tier1:
                EquipeID = [Deck[e] for e in i]
                dégats = DB.execute("Select Attack From Current_hero Where id='"+EquipeID[f1]+"'").fetchone()[0] * 3
                dégats += DB.execute("Select Attack From Current_hero Where id='"+EquipeID[f2]+"'").fetchone()[0] * 3
                dégats += DB.execute("Select Attack From Current_hero Where id='"+EquipeID[f3]+"'").fetchone()[0] * 3
                if(dégats > max):
                    max = dégats
                    best = Class[i]
            return best 
    else :
        print("pas ouf la team"+str(tier2))
        max = 0
        best = -1
        for i in tier2:
            (trishot,sniper,justShootEveryone) = ClassSp[i]
            EquipeID = [Deck[e] for e in Class[i]]
            dégats = 0
            for j in [f1,f2,f3]:
                #print("j = "+str(j))
                #TODO Changer Max_hero pour Current_hero dans la table
                degat = DB.execute("Select Attack From Max_hero Where id='"+EquipeID[j]+"'").fetchone()[0]
                if(trishot[j]==1):
                    dégats+=degat*3
                else :
                    if(justShootEveryone[j]==1):
                        dégats+=degat*5
                    else :
                        dégats+=degat
            if(max<dégats):
                max = dégats
                best = Class[i]
        return best


def onChangePasUneEquipeQuiGagne(Deck,trucsQuiMarchent,disB,lS,dB,iH,bH,C,R):
    #print("onChangePasUneEquipeQuiGagne function called with Deck:", Deck, "trucsQuiMarchent:", trucsQuiMarchent, "disB:", disB, "lS:", lS, "dB:", dB, "iH:", iH, "bH:", bH, "C:", C, "R:", R)
    tier1=[]
    tier2=[]
    tier3=[]
    tier4=[]
    tier5=[]
    for i in trucsQuiMarchent:
        Equipe = i[0]
        f1 = i[1]
        f2 = i[2]
        f3 = i[3]
        h = i[4]
        s = i[5]
        #règles de priorités entre les types de soutiens
        if(R[Equipe[s]] == 1):
            tier1.append(Equipe)
        else: 
            if(C[Equipe[s]] == 1) or (disB[Equipe[s]] == 1):
                tier2.append(Equipe)
            else :
                if(lS[Equipe[s]]):
                    tier3.append(Equipe)
                else :
                    if(dB[Equipe[s]]):
                        tier4.append(Equipe)
                    else :
                        if(iH[Equipe[s]]==1) or (bH[Equipe[s]]==1):
                            tier5.append(Equipe)
    cpt=1
    for i in [tier1,tier2,tier3,tier4,tier5]:
        #print("contenu du tier "+str(i))
        if(len(i)>0):
            #print("l'équipe fait partie du tier = "+str(cpt))
            if(len(i)==1):
                #print("un seul choix")
                return i[0]
            else :
                #print("plusieurs choix")
                #parmis celles qui ont le meilleur soutiens on classe par quantité de dégats totaux 
                return classementDégat(Deck, i, f1, f2, f3) 
        cpt+=1


def moteur_inférence(Deck,CoulAdv):
    #print("moteur_inférence function called with Deck:", Deck, "CoulAdv:", CoulAdv)
    #instanciation des Prédicats (uniquement ceux utiliser par les règles dans cette version)
    SC = initSC(Deck)
    manas = initMana(Deck) #rappel du format du tuple (VSM,SM,AM,FM,VFM)
    VSM = manas[0]
    SM = manas[1]
    AM = manas[2]
    FM = manas[3]
    VFM = manas[4]
    disB = init_DispelsBuff_Bonus(Deck)
    lS = init_LowerEnemieStats(Deck)
    dB = init_DamageBuff_Bonus(Deck)
    iH = init_HealingBuff_Bonus(Deck)
    bH = init_BoostedHealth_Bonus(Deck)
    C = init_Cleanses_Bonus(Deck)
    R = init_Revive_Bonus(Deck)
    sAC = init_strongVsAdvCol(Deck, CoulAdv)

    #filtrage des équipes en fonction des critère considéré comme indispensable par le système expert
    trucsQuiMarchent = Jour5SansVoirLeSoleil(Deck, SC, VFM, FM, AM, disB, lS, dB, iH, bH, C, R, sAC)

    if(trucsQuiMarchent != []):
        #classement des Equipes restantes via des règles auquelles est associé un poid 
        lEquipeQuiGagne = onChangePasUneEquipeQuiGagne(Deck,trucsQuiMarchent,disB, lS, dB, iH, bH, C, R)
        return lEquipeQuiGagne
    else :
        return []

def launchSysExpert(CoulAdv):
    print("launchSysExpert function called with CoulAdv:", CoulAdv)
    Deck=[]
    Rarity = ["Legendary","Epic","Rare"]
    for i in Rarity:
        
        List = DB.execute("Select c.id From Current_hero c \
                            Join Hero h on c.id = h.id \
                            Where h.Rarity ='"+i+"'").fetchall()
        
        Deck += [e[0] for e in List]
        equipe = moteur_inférence(Deck, CoulAdv)
        print(f"Equipe: {equipe}")
        if(equipe != []):
            result = [Deck[e] for e in equipe]
            #print(result)
            return result
    return "Acune équipe ne correspond"

if __name__ == "__main__":
    CoulAdv="Fire/Red"
    #print(f"Result from Expert System: {launchSysExpert(CoulAdv)}\n")
    result = launchSysExpert("Dark/Purple")
    print(f"\nResult from Expert System: {result}")