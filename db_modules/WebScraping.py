import time
from sys import platform
import glob #biblio pour la reecher de ficher dans l'arborescence quelque soit le SE 
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

#import de la bd 
from db_modules.db import drop_tables,init_tables,DB
from db_modules.ability import Ability
from db_modules.aether_power import Aether_power
from db_modules.origin import Origin
from db_modules.elemental_type import Elemental_type
from db_modules.hero import Hero
from db_modules.possess import Possess
from db_modules.max_hero import Max_hero

opts = Options()

#opts.add_argument('--headless')

#lien pour télécharger chromium sous windows peut-être pas necessaire 
#https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html?prefix=Win/1278240/

print("Preparation de chromium")
print("Recherche du chemin sous Linux")
p=Path('/home')
chromiumExePath=list(p.glob('**/snap/chromium')) 
if(chromiumExePath == [] ):
    print("Pas de resultat, recherche du chemin sous Windows")
    p=Path('c:/Users')
    chromiumExePath=list(p.glob('**/chrome.exe'))
    if(chromiumExePath == [] ):
        print("Probleme d'acces a chromium, l'application est-elle bien installee?")
        print("Il est possible de le telecharger a partir de ce lien:")
        print("https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html?prefix=Win/1278240/")
opts.binary_location = str(chromiumExePath[0])
driver = webdriver.Chrome(options=opts)

#Fonction pour remplir les bd Passif, Special skill et Family

def addInAbility(name,desc):
    ab1 = DB.execute("Select id From Ability Where Ab_name = '"+name+"'").fetchone()
    if(ab1 is None):
        ab1 = Ability(name,desc)
        ab1.store()
        return ab1.abid
    else :
        return ab1[0]

def addInAp(name,desc):
    ap = DB.execute("Select id From Aether_power Where Power_name = '"+name+"'").fetchone()
    if(ap is None):
        ap = Aether_power(name,desc)
        ap.store()
        return ap.apid
    else :
        return ap[0]


def addInOrigin(family):
    #si le nom est présent dans la alors on ne fait rien sinon on ajoute toutes les infos sur la famille
    fam = DB.execute("Select id From Origin Where Family = '"+family+"'").fetchone()
    if(fam is None):
        origin = driver.find_element(By.XPATH,'//div[@data-table-index="3"]/table/tbody/tr/td[1]').text
        #il est possible qu'une famille n'ait pas de bonus sinon ils sont tous rassembler dans le mm champ
        #La balise html blockquote c'est utilisé qu'une seule fois dans un div de class cooked dans chaque page de héro, on peut donc l'utiliser pour trouver a coup sur le bonus de famille
        html = driver.find_elements(By.XPATH,'div[@class="cooked"]/blockquote')
        if(html == []):
            familyBonus = ""
        else :
            familyBonus = html[0].text
        fam = Origin(family, origin, familyBonus)
        fam.store()
        return fam.oid
    else :
        return fam[0]

#Fonction qui sauvegarde un Hero dans la bd
def saveHero(dico):
    h = Hero(dico['Name'],dico['Rarity'],dico['Class'],dico['Mana Speed'],dico['aetherPower'],dico['Element'],dico['Origin'],dico['SpecialSkill'])
    h.store()
    i=0
    for i in range(dico['nbAbility']):
        p = Possess(h.hid,dico['Ability '+str(i)])
        p.store()
        i+=1
    hm = Max_hero(h.hid, dico['Attack'], dico['Defense'], dico['Health'], dico['Attack LB1'], dico['Defense LB1'], dico['Health LB1'], dico['Attack LB2'], dico['Defense LB2'], dico['Health LB2'])
    hm.store()

#Fonction qui récupère les données d'un Héroe depuis sa page sur le forum du jeu 
def getDataHero():
    #Erreur de timeOut execption dans la page https://forum.smallgiantgames.com/t/14-titans-no-skips-top-alliances-ideas-to-share-the-hp-between-all-members/248655
    #Cette page a passé le test de isAChampPage alors qu'elle n'aurait pas du
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,"//div[@class='cooked']/div[@class='md-table fullscreen-table-wrapper']")))
    html = driver.find_elements(By.XPATH,"//div[@class='cooked']/div[@class='md-table fullscreen-table-wrapper']")
    isComplete = driver.find_elements(By.XPATH,'//div[@data-table-index="'+html[0].get_attribute("data-table-index")+'"]/table/thead/tr/th/h1')
    if isComplete ==[]:
        j=0
        name = driver.find_element(By.XPATH,'//div[@class="cooked"]/p[1]/strong').text
    else :
        j=1
        name = isComplete[0].text
    dico = {
            "Name" : name ,
            'Rarity' : driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j].get_attribute("data-table-index")+'"]/table/tbody/tr/td[1]').text,
            'Class' : driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j].get_attribute("data-table-index")+'"]/table/tbody/tr/td[3]').text,
            'Mana Speed' : driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j].get_attribute("data-table-index")+'"]/table/tbody/tr/td[4]/small').text,
    }
    elemName = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j].get_attribute("data-table-index")+'"]/table/tbody/tr/td[2]').text
    elemid = DB.execute("Select id From Elemental_type Where El_type = '"+elemName+"'").fetchone()
    if(elemid is None):
        print("HAAAAAAAAAAA !")
    else :
        dico["Element"] = elemid[0]
    #permet de savoir si le Héro a des costumes
    nbCostume = len(driver.find_elements(By.XPATH,'//div[@data-table-index="2"]/table/tbody/tr[1]/td[2]/ins'))
    #Le bloc suivant remplie les stats du Héro au niveau max (avec tout les costumes si il en a)
    if(nbCostume == 0):
        dico['Attack'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[1]/td[2]/big').text
        dico['Defense'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[1]/td[3]/big').text
        dico['Health'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[1]/td[4]/big').text
        dico['Attack LB1'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[2]/td[2]/big').text
        dico['Defense LB1'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[2]/td[3]/big').text
        dico['Health LB1'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[2]/td[4]/big').text
        dico['Attack LB2'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[3]/td[2]/big').text
        dico['Defense LB2'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[3]/td[3]/big').text
        dico['Health LB2'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[3]/td[4]/big').text
    else :
        print("héro avec costumes")
        dico['Attack'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[1]/td[2]/ins["'+str(nbCostume)+'"]').text
        dico['Defense'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[1]/td[3]/ins["'+str(nbCostume)+'"]').text
        dico['Health'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[1]/td[4]/ins["'+str(nbCostume)+'"]').text
        dico['Attack LB1'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[2]/td[2]/ins["'+str(nbCostume)+'"]').text
        dico['Defense LB1'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[2]/td[3]/ins["'+str(nbCostume)+'"]').text
        dico['Health LB1'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[2]/td[4]/ins["'+str(nbCostume)+'"]').text
        dico['Attack LB2'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[3]/td[2]/ins["'+str(nbCostume)+'"]').text
        dico['Defense LB2'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[3]/td[3]/ins["'+str(nbCostume)+'"]').text
        dico['Health LB2'] = driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+1].get_attribute("data-table-index")+'"]/table/tbody/tr[3]/td[4]/ins["'+str(nbCostume)+'"]').text

    #Gestion a part des attribut qui sont dans d'autres classes dans la bdd (car ils ne sont pas nécessairemment présent pour chaque Héro, c'est la raison pour laquelle ils sont dans une classe a part)
    Ability = driver.find_elements(By.XPATH,"//div[@class='md-table fullscreen-table-wrapper']/table/thead/tr/th[contains(text(),'Ability:')]")
    Resist = driver.find_elements(By.XPATH,"//div[@class='md-table fullscreen-table-wrapper']/table/thead/tr/th[contains(text(),'Resist:')]")
    Ability+=Resist
    for i in range(len(Ability)):
        Str = Ability[i].text[9:]
        p = Str.find('\n')
        idAbility = addInAbility(Str[:p],Str[p+2:])
        dico['Ability '+str(i)] = str(idAbility)
    dico['nbAbility'] = len(Ability)
    
    SS = driver.find_elements(By.XPATH,"//div[@class='md-table fullscreen-table-wrapper']/table/thead/tr/th[contains(text(),'Special Skill:')]/../../..")
    if(SS != []):
        Str = SS[0].text[15:]
        p = Str.find('\n')
        dico['SpecialSkill']= Str[:p] + ' | ' +Str[p+1:]
    else :
        dico['SpecialSkill'] = None
        

    #Gestion de la classe origin
    famille =  driver.find_element(By.XPATH,'//div[@data-table-index="'+html[j+2].get_attribute("data-table-index")+'"]/table/tbody/tr/td[2]').text
    dico['Origin'] = str(addInOrigin(famille))
    #Cannot locate elemennt ?? : Nadezhda
    ApName = driver.find_elements(By.XPATH,"//div[@class='md-table fullscreen-table-wrapper']/table/thead/tr/th/small[contains(text(),'Aether Power')]/../../../../tbody/tr/td[2]")
    if(ApName !=[]):
        ApDesc = driver.find_element(By.XPATH,"//div[@class='md-table fullscreen-table-wrapper']/table/thead/tr/th/small[contains(text(),'Aether Power')]/../../../../tbody/tr/td[3]").text
        dico["aetherPower"] = str(addInAp(ApName[0].text,ApDesc))
    else :
        dico["aetherPower"] = None

    return dico

#La fonction suivante vérifie qu'une chaine de caractère corrspond a la syntaxe d'un titre de page de Héro sur le forum d'empire and puzzles
def isAchampPage(titre):
    p=titre.find('-')
    if(p==-1): # car ces idiots ont eu la bonne idée d'utiliser des tirets différents sorti de nulle part 
        p=titre.find('–')
    if(p!=-1):
        if(titre[p+2].isdigit() and titre[p+3]=='*'):
            return True 
        else:
            #si le tiret n'est pas suivi d'un espace puis d'un nombre puis d'une étoile on cherche un autre tiret
            titre=titre[:p]+titre[p+1:]
            p=titre.find('-')
            if(p==-1):
                p=titre.find('–')
            while (p!=-1) and not (p>=len(titre)-3) and not(titre[p+2].isdigit() and titre[p+3]=='*'):
                # içi on fait l'hypothèse (bancale) que le créateur de la page n'aura pas utiliser les deux tiret différents dans le même titre
                titre=titre[:p]+titre[p+1:]
                p=titre.find('-')
                if(p==-1):
                    p=titre.find('–')
                if(p+3>=len(titre)):
                    print(titre)
            if(p != -1):
                if(len(titre)>p+3):
                    if(titre[p+2].isdigit() and titre[p+3]=='*'):
                        return True
    return False

#Fonction qui vas a la page d'un héro précis en prenant son nom en params !! Attention aux héros avec des costumes il en existe plusieurs version 
def addHero(name):
    #Lien vers la page qui contient les pages de Héro sur le forum
    driver.get('https://forum.smallgiantgames.com/c/player-guides/13')
    #La ligne suivante sers a accepter les cookies (on utilise un wait car c'est un fenêtre pop-up qui apparait après le chargement de la page)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,"//button[contains(text(),'Accepter les cookies')]"))).click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//button[@id="search-button"]'))).click()#acces a la barre de recherche
    searchBar = driver.find_element(By.XPATH,'//input[@id="search-term"]')
    searchBar.send_keys(name)
    #clique sur le résultat qui contient la mention "player guide"
    driver.find_element(By.XPATH,'//a[@class="search-link"]/span/span/span[contains(text(),"Player Guides")]/../../..').click()
    #récupère le lien du premier résultat
    noTitre=True
    i=1
    #la boucle suivante vérifie que le premier lien est bien celui d'une page de champion
    while(noTitre):
        titre = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,"//div[@class='search-result-topic']/ul/li["+str(i)+"]/a/span/span/span/a/span"))).text
        print(type(titre) , titre)
        if(isAchampPage(titre)):
            noTitre=False
        else:
            i+=1
    driver.find_element(By.XPATH,"//div[@class='search-result-topic']/ul/li["+str(i)+"]/a/span/span/span/a/span").click()
    dico = getDataHero()
    driver.quit()
    #si dico ne contient qu'un msg d'erreur on l'affiche (cas qui n'arrive jamais dans la version actuelle du fichier) 
    if(type(dico)==str):
        print(dico)
    else :
        return dico

#Fonction qui passe en revu tout les liens de la page player guide du forum pour récupére toutes les infos sur les Héros présent sur le forum
def addAllHeroes():
    global driver 
    driver.get('https://forum.smallgiantgames.com/c/player-guides/13')
    # Accepter les cookies
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,"//button[contains(text(),'Accepter les cookies')]"))).click()

    #ce bloc permet de scroller jusqu'a la fin de la liste pour charger tout les liens
    Y1 = 0
    Y2 = -1
    i=0
    while Y1 != Y2:
        Y1 = driver.execute_script("return document.documentElement.scrollHeight")
        driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight)")
        time.sleep(0.5)
        Y2 = driver.execute_script("return document.documentElement.scrollHeight")
        i+=1
        cpt=1
        while Y1 == Y2 and cpt<5:
            Y1 = driver.execute_script("return document.documentElement.scrollHeight")
            driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight)")
            time.sleep(0.5*cpt)
            Y2 = driver.execute_script("return document.documentElement.scrollHeight")
            cpt+=1
    #TODO mettre un truc du sytle while Y1=Y2 and cpt<n { attendre un peu au cas ou on sot pas au bout de la page }

    #le bloc suivant permet de recupérer les titre de toutes les pages du forum (le XPATH m'as l'air tout a fait bancal)
    lignes = driver.find_elements(By.XPATH,"//tr")
    print("nb lignes afficher : ",len(lignes))
    toCheck=[]
    for i in range(4,len(lignes)):
        titre = driver.find_element(By.XPATH,'//tr[@id="'+lignes[i].get_attribute("id")+'"]/td[1]/span/a').text
        if(isAchampPage(titre)):
            # si le titre de la page respecte la syntaxe d'un titre de page de Héro alors on ajouter l'inde de cette ligne dans la liste des lien a regarder
            toCheck.append(i)
    #a subi des modif depuis le dernire test (Création de isAchampPage())
    print(toCheck,len(toCheck))

    #récuperation de tout les liens et stockage dans le tableau links
    links = []
    for i in range(len(toCheck)):
        links.append(driver.find_element(By.XPATH,'//tr[@id="'+lignes[toCheck[i]].get_attribute("id")+'"]/td[1]/span/a').get_attribute("href"))
    #récupération des infos de chaque héro sur leur page
    DATA=[]
    for i in range(len(toCheck)):
        #print("i = "+str(i))
        #print(lignes[toCheck[i]].get_attribute("id"))
        #link = driver.find_element(By.XPATH,'//tr[@id="'+lignes[toCheck[i]].get_attribute("id")+'"]/td[1]/span/a').get_attribute("href")
        try :
            driver.get(links[i])
            print(i)
            print(links[i])
            dico = getDataHero()
            saveHero(dico)
        except WebDriverException :
            print("woooooooo")
            driver = webdriver.Chrome(options=opts)
            driver.get(links[i])
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,"//button[contains(text(),'Accepter les cookies')]"))).click()
            print(links[i])
            dico = getDataHero()
            saveHero(dico)
        
        DATA.append(dico)
    return DATA

#print(addHero("Cupido"))
#dico=addHero("Cupido")
#print(dico)
#saveHero(dico)
#saveHero(addHero("Lazara"))
addAllHeroes()