import json			#Imports
import os
import getpass
import base64
from datetime import datetime
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

DB_DATEI = "geheimdatenbank.enc"
USER_DATEI = "users.enc"
SALT_DATEI = "salt.bin"

STANDARD_BENUTZER = {
    "admin": {"passwort": "admin123", "rolle": "Administrator", "clearance": 4},
    "director": {"passwort": "director123", "rolle": "Director", "clearance": 4},
    "officer": {"passwort": "officer123", "rolle": "Officer", "clearance": 3},
    "agent": {"passwort": "agent123", "rolle": "Agent", "clearance": 2},
    "informant": {"passwort": "informant123", "rolle": "Informant", "clearance": 1},
    "viewer": {"passwort": "viewer123", "rolle": "Viewer", "clearance": 1}
}

CLEARANCE_NAMEN = {
    1: "PUBLIC",
    2: "INTERN",
    3: "GEHEIM",
    4: "TOP_SECRET"
}


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def trennlinie():
    print("\n" + "=" * 80 + "\n")


def pause():
    input("\nENTER drücken...")


def zeitstempel():
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


def mehrzeilige_eingabe(titel="Text eingeben"):

    print(f"\n{titel}")
    print("Mit EOF beenden.\n")

    zeilen = []

    while True:

        zeile = input()

        if zeile.strip().upper() == "EOF":
            break

        zeilen.append(zeile)

    return "\n".join(zeilen)



# =========================================================
# VERSCHLÜSSELUNG
# =========================================================

def lade_oder_erstelle_salt():
    if os.path.exists(SALT_DATEI):
        with open(SALT_DATEI, "rb") as datei:
            return datei.read()

    salt = os.urandom(16)

    with open(SALT_DATEI, "wb") as datei:
        datei.write(salt)

    return salt


def erzeuge_fernet(masterpasswort):
    salt = lade_oder_erstelle_salt()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000
    )

    key = base64.urlsafe_b64encode(
        kdf.derive(masterpasswort.encode())
    )

    return Fernet(key)


def verschluesselt_speichern(dateiname, daten, fernet):
    json_text = json.dumps(daten, indent=4, ensure_ascii=False)
    verschluesselt = fernet.encrypt(json_text.encode("utf-8"))

    with open(dateiname, "wb") as datei:
        datei.write(verschluesselt)


def verschluesselt_laden(dateiname, standardwert, fernet):
    if not os.path.exists(dateiname):
        verschluesselt_speichern(dateiname, standardwert, fernet)
        return standardwert

    try:
        with open(dateiname, "rb") as datei:
            verschluesselt = datei.read()

        entschluesselt = fernet.decrypt(verschluesselt)
        return json.loads(entschluesselt.decode("utf-8"))

    except InvalidToken:
        print("\nFALSCHES MASTERPASSWORT ODER DATEI BESCHÄDIGT.")
        exit()

    except:
        print("\nFehler beim Laden der verschlüsselten Datei.")
        exit()


def master_login():
    clear()
    trennlinie()
    print("ENCRYPTED CLASSIFIED DATABASE")
    print("MASTER KEY REQUIRED\n")

    masterpasswort = getpass.getpass("Masterpasswort: ")

    if masterpasswort == "":
        print("Masterpasswort darf nicht leer sein.")
        exit()

    return erzeuge_fernet(masterpasswort)


# =========================================================
# LADEN / SPEICHERN
# =========================================================

def lade_benutzer(fernet):
    return verschluesselt_laden(USER_DATEI, STANDARD_BENUTZER.copy(), fernet)


def speichere_benutzer(benutzer, fernet):
    verschluesselt_speichern(USER_DATEI, benutzer, fernet)


def lade_datenbank(fernet):
    return verschluesselt_laden(DB_DATEI, [], fernet)


def speichere_datenbank(datenbank, fernet):
    verschluesselt_speichern(DB_DATEI, datenbank, fernet)


def naechste_id(datenbank):
    if len(datenbank) == 0:
        return 1

    return max(eintrag["id"] for eintrag in datenbank) + 1


# =========================================================
# LOGIN
# =========================================================

def login(benutzer):
    clear()
    trennlinie()

    print("CLASSIFIED DATABASE")
    print("AUTHENTICATION REQUIRED\n")

    for _ in range(3):
        benutzername = input("Codename: ")
        passwort = getpass.getpass("Passphrase: ")

        if benutzername in benutzer and benutzer[benutzername]["passwort"] == passwort:
            print("\nACCESS GRANTED")
            return benutzername, benutzer[benutzername]

        print("\nACCESS DENIED\n")

    print("SYSTEM LOCKED")
    exit()


# =========================================================
# RECHTE
# =========================================================

def ist_admin(userdaten):
    return userdaten["rolle"] == "Administrator"


def darf_anzeigen(userdaten, eintrag):
    return userdaten["clearance"] >= eintrag["sicherheitsstufe"]


def darf_bearbeiten(userdaten, eintrag):
    return userdaten["clearance"] >= eintrag["sicherheitsstufe"]


def darf_loeschen(userdaten):
    return userdaten["clearance"] == 4


def darf_erstellen(userdaten):
    return userdaten["rolle"] != "Viewer"


# =========================================================
# AKTEN
# =========================================================

def eintrag_anzeigen(eintrag):
    print("-" * 80)
    print(f"ID:                 {eintrag['id']}")
    print(f"Codename/Titel:     {eintrag['codename']}")
    print(f"Kategorie:          {eintrag['kategorie']}")
    print(f"Sicherheitsstufe:   {CLEARANCE_NAMEN[eintrag['sicherheitsstufe']]}")
    print(f"Status:             {eintrag['status']}")
    print(f"Erstellt von:       {eintrag['erstellt_von']}")
    print(f"Erstellt am:        {eintrag['erstellt_am']}")
    print(f"Geändert am:        {eintrag['geaendert_am']}")
    print(f"Inhalt:             {eintrag['inhalt']}")
    print("-" * 80)


def geschwaerzter_eintrag(eintrag):
    print("-" * 80)
    print(f"ID:                 {eintrag['id']}")
    print("Codename/Titel:     [REDACTED]")
    print("Kategorie:          [REDACTED]")
    print(f"Sicherheitsstufe:   {CLEARANCE_NAMEN[eintrag['sicherheitsstufe']]}")
    print("Status:             ACCESS DENIED")
    print("Inhalt:             ███████████████████████████████████")
    print("-" * 80)


def akten_liste_anzeigen(datenbank, userdaten, nur_sichtbare=False):
    trennlinie()

    print("SICHTBARE AKTEN\n" if nur_sichtbare else "AKTENÜBERSICHT\n")

    angezeigte_akten = []

    for eintrag in datenbank:
        if nur_sichtbare and not darf_anzeigen(userdaten, eintrag):
            continue
        angezeigte_akten.append(eintrag)

    if len(angezeigte_akten) == 0:
        print("Keine Akten vorhanden.")
        pause()
        return

    for index, eintrag in enumerate(angezeigte_akten, start=1):
        if darf_anzeigen(userdaten, eintrag):
            print(
                f"{index}. {eintrag['codename']:<30} | "
                f"{CLEARANCE_NAMEN[eintrag['sicherheitsstufe']]:<10} | "
                f"{eintrag['status']}"
            )
        else:
            print(
                f"{index}. [REDACTED]                     | "
                f"{CLEARANCE_NAMEN[eintrag['sicherheitsstufe']]:<10} | "
                f"ACCESS DENIED"
            )

    print("\n0 - Zurück")

    try:
        auswahl = int(input("\nWelche Akte öffnen?: "))
    except:
        print("Ungültige Eingabe.")
        pause()
        return

    if auswahl == 0:
        return

    if auswahl < 1 or auswahl > len(angezeigte_akten):
        print("Diese Akte gibt es nicht.")
        pause()
        return

    akte = angezeigte_akten[auswahl - 1]

    trennlinie()
    print("AKTE GEÖFFNET\n")

    if darf_anzeigen(userdaten, akte):
        eintrag_anzeigen(akte)
    else:
        geschwaerzter_eintrag(akte)

    pause()


def suche(datenbank, userdaten):
    trennlinie()
    print("INTELLIGENCE SEARCH\n")

    suchtext = input("Suchbegriff: ").lower()
    treffer = []

    for eintrag in datenbank:
        if not darf_anzeigen(userdaten, eintrag):
            continue

        text = (
            str(eintrag["id"]) + " " +
            eintrag["codename"] + " " +
            eintrag["kategorie"] + " " +
            eintrag["inhalt"] + " " +
            eintrag["status"]
        ).lower()

        if suchtext in text:
            treffer.append(eintrag)

    if len(treffer) == 0:
        print("Keine sichtbaren Treffer gefunden.")
        pause()
        return

    for index, eintrag in enumerate(treffer, start=1):
        print(
            f"{index}. {eintrag['codename']} | "
            f"{CLEARANCE_NAMEN[eintrag['sicherheitsstufe']]} | "
            f"{eintrag['status']}"
        )

    print("\n0 - Zurück")

    try:
        auswahl = int(input("\nWelche Akte öffnen?: "))
    except:
        print("Ungültige Eingabe.")
        pause()
        return

    if auswahl == 0:
        return

    if 1 <= auswahl <= len(treffer):
        eintrag_anzeigen(treffer[auswahl - 1])
    else:
        print("Ungültige Auswahl.")

    pause()


def akte_erstellen(datenbank, benutzername, userdaten, fernet):
    trennlinie()
    print("NEUE AKTE ERSTELLEN\n")

    if not darf_erstellen(userdaten):
        print("ACCESS DENIED")
        print("Viewer dürfen keine Akten erstellen.")
        pause()
        return

    codename = input("Titel / Codename: ")
    kategorie = input("Kategorie: ")
    inhalt = mehrzeilige_eingabe(
        "Geheimer Inhalt"
    )

    print("\nSicherheitsstufe:")
    print("1 - PUBLIC")
    print("2 - INTERN")
    print("3 - GEHEIM")
    print("4 - TOP_SECRET")

    try:
        stufe = int(input("\nStufe: "))
    except:
        print("Ungültige Eingabe.")
        pause()
        return

    if stufe < 1 or stufe > 4:
        print("Ungültige Sicherheitsstufe.")
        pause()
        return

    if stufe > userdaten["clearance"]:
        print("Du kannst keine höhere Clearance vergeben als deine eigene.")
        pause()
        return

    neuer_eintrag = {
        "id": naechste_id(datenbank),
        "codename": codename,
        "kategorie": kategorie,
        "inhalt": inhalt,
        "sicherheitsstufe": stufe,
        "status": "AKTIV",
        "erstellt_von": benutzername,
        "erstellt_am": zeitstempel(),
        "geaendert_am": zeitstempel()
    }

    datenbank.append(neuer_eintrag)
    speichere_datenbank(datenbank, fernet)

    print("\nAKTE VERSCHLÜSSELT GESPEICHERT.")
    pause()


def finde_akte(datenbank, id_nummer):
    for eintrag in datenbank:
        if eintrag["id"] == id_nummer:
            return eintrag

    return None


def akte_bearbeiten(datenbank, userdaten, fernet):
    trennlinie()
    print("AKTE BEARBEITEN\n")

    for eintrag in datenbank:
        if darf_anzeigen(userdaten, eintrag):
            print(
                f"ID {eintrag['id']} | "
                f"{eintrag['codename']} | "
                f"{CLEARANCE_NAMEN[eintrag['sicherheitsstufe']]}"
            )

    try:
        id_nummer = int(input("\nID der Akte: "))
    except:
        print("Ungültige ID.")
        pause()
        return

    eintrag = finde_akte(datenbank, id_nummer)

    if eintrag is None:
        print("Akte nicht gefunden.")
        pause()
        return

    if not darf_bearbeiten(userdaten, eintrag):
        print("ACCESS DENIED")
        pause()
        return

    eintrag_anzeigen(eintrag)

    print("\n1 - Titel / Codename")
    print("2 - Kategorie")
    print("3 - Inhalt")
    print("4 - Status")
    print("5 - Sicherheitsstufe")
    print("0 - Abbrechen")

    wahl = input("\nAuswahl: ")

    if wahl == "1":
        eintrag["codename"] = input("Neuer Titel / Codename: ")
    elif wahl == "2":
        eintrag["kategorie"] = input("Neue Kategorie: ")
    elif wahl == "3":
        eintrag["inhalt"] = mehrzeilige_eingabe(
            "Neuer Inhalt"
        )
    elif wahl == "4":
        eintrag["status"] = input("Neuer Status: ")
    elif wahl == "5":
        try:
            neue_stufe = int(input("Neue Sicherheitsstufe 1-4: "))
        except:
            print("Ungültige Eingabe.")
            pause()
            return

        if neue_stufe < 1 or neue_stufe > 4:
            print("Ungültige Sicherheitsstufe.")
            pause()
            return

        if neue_stufe > userdaten["clearance"]:
            print("Zu hohe Sicherheitsstufe.")
            pause()
            return

        eintrag["sicherheitsstufe"] = neue_stufe
    elif wahl == "0":
        return
    else:
        print("Ungültige Auswahl.")
        pause()
        return

    eintrag["geaendert_am"] = zeitstempel()
    speichere_datenbank(datenbank, fernet)

    print("\nAKTE AKTUALISIERT UND VERSCHLÜSSELT GESPEICHERT.")
    pause()


def akte_loeschen(datenbank, userdaten, fernet):
    trennlinie()
    print("AKTE LÖSCHEN\n")

    if not darf_loeschen(userdaten):
        print("ACCESS DENIED")
        pause()
        return

    for eintrag in datenbank:
        print(
            f"ID {eintrag['id']} | "
            f"{eintrag['codename']} | "
            f"{CLEARANCE_NAMEN[eintrag['sicherheitsstufe']]}"
        )

    try:
        id_nummer = int(input("\nID der Akte: "))
    except:
        print("Ungültige ID.")
        pause()
        return

    eintrag = finde_akte(datenbank, id_nummer)

    if eintrag is None:
        print("Akte nicht gefunden.")
        pause()
        return

    eintrag_anzeigen(eintrag)

    bestaetigung = input("\nDELETE eingeben zum Löschen: ")

    if bestaetigung == "DELETE":
        datenbank.remove(eintrag)
        speichere_datenbank(datenbank, fernet)
        print("AKTE GELÖSCHT")
    else:
        print("Abgebrochen.")

    pause()


# =========================================================
# BENUTZER
# =========================================================

def benutzer_anzeigen(benutzer):
    print("\nAKTUELLE BENUTZER:\n")

    for index, (name, daten) in enumerate(benutzer.items(), start=1):
        print(
            f"{index}. {name:<15} | "
            f"{daten['rolle']:<15} | "
            f"{CLEARANCE_NAMEN[daten['clearance']]}"
        )


def rolle_auswaehlen():
    print("\nRolle wählen:")
    print("1 - Viewer        | PUBLIC | Nur ansehen")
    print("2 - Informant     | PUBLIC")
    print("3 - Agent         | INTERN")
    print("4 - Officer       | GEHEIM")
    print("5 - Director      | TOP_SECRET")
    print("6 - Administrator | TOP_SECRET")

    rollen = {
        "1": {"rolle": "Viewer", "clearance": 1},
        "2": {"rolle": "Informant", "clearance": 1},
        "3": {"rolle": "Agent", "clearance": 2},
        "4": {"rolle": "Officer", "clearance": 3},
        "5": {"rolle": "Director", "clearance": 4},
        "6": {"rolle": "Administrator", "clearance": 4}
    }

    return rollen.get(input("\nAuswahl: "))


def benutzer_hinzufuegen(benutzer, fernet):
    trennlinie()
    print("BENUTZER HINZUFÜGEN\n")

    neuer_name = input("Neuer Benutzername: ").strip()

    if neuer_name == "":
        print("Benutzername darf nicht leer sein.")
        pause()
        return

    if neuer_name in benutzer:
        print("Benutzer existiert bereits.")
        pause()
        return

    passwort = getpass.getpass("Passwort: ")

    if passwort == "":
        print("Passwort darf nicht leer sein.")
        pause()
        return

    rolle = rolle_auswaehlen()

    if rolle is None:
        print("Ungültige Rolle.")
        pause()
        return

    benutzer[neuer_name] = {
        "passwort": passwort,
        "rolle": rolle["rolle"],
        "clearance": rolle["clearance"]
    }

    speichere_benutzer(benutzer, fernet)

    print("\nBENUTZER ERSTELLT UND VERSCHLÜSSELT GESPEICHERT.")
    pause()


def benutzer_bearbeiten(benutzer, aktueller_benutzername, fernet):
    trennlinie()
    print("BENUTZER BEARBEITEN")
    benutzer_anzeigen(benutzer)

    name = input("\nBenutzername: ").strip()

    if name not in benutzer:
        print("Benutzer nicht gefunden.")
        pause()
        return

    print("\n1 - Rolle / Clearance ändern")
    print("2 - Benutzername ändern")
    print("0 - Abbrechen")

    wahl = input("\nAuswahl: ")

    if wahl == "1":
        rolle = rolle_auswaehlen()

        if rolle is None:
            print("Ungültige Rolle.")
            pause()
            return

        benutzer[name]["rolle"] = rolle["rolle"]
        benutzer[name]["clearance"] = rolle["clearance"]

    elif wahl == "2":
        neuer_name = input("Neuer Benutzername: ").strip()

        if neuer_name == "":
            print("Benutzername darf nicht leer sein.")
            pause()
            return

        if neuer_name in benutzer:
            print("Benutzername existiert bereits.")
            pause()
            return

        benutzer[neuer_name] = benutzer.pop(name)

        if name == aktueller_benutzername:
            print("Hinweis: Du hast deinen eigenen Namen geändert.")

    elif wahl == "0":
        return

    else:
        print("Ungültige Eingabe.")
        pause()
        return

    speichere_benutzer(benutzer, fernet)
    print("Benutzer wurde aktualisiert.")
    pause()


def benutzer_passwort_aendern(benutzer, fernet):
    trennlinie()
    print("PASSWORT ÄNDERN")
    benutzer_anzeigen(benutzer)

    name = input("\nBenutzername: ").strip()

    if name not in benutzer:
        print("Benutzer nicht gefunden.")
        pause()
        return

    passwort1 = getpass.getpass("Neues Passwort: ")
    passwort2 = getpass.getpass("Passwort wiederholen: ")

    if passwort1 == "" or passwort1 != passwort2:
        print("Passwort ungültig oder stimmt nicht überein.")
        pause()
        return

    benutzer[name]["passwort"] = passwort1
    speichere_benutzer(benutzer, fernet)

    print("Passwort wurde geändert.")
    pause()


def benutzer_loeschen(benutzer, aktueller_benutzername, fernet):
    trennlinie()
    print("BENUTZER LÖSCHEN")
    benutzer_anzeigen(benutzer)

    name = input("\nBenutzername löschen: ").strip()

    if name not in benutzer:
        print("Benutzer nicht gefunden.")
        pause()
        return

    if name == aktueller_benutzername:
        print("Du kannst dich nicht selbst löschen.")
        pause()
        return

    admin_anzahl = sum(1 for daten in benutzer.values() if daten["rolle"] == "Administrator")

    if benutzer[name]["rolle"] == "Administrator" and admin_anzahl <= 1:
        print("Der letzte Administrator darf nicht gelöscht werden.")
        pause()
        return

    bestaetigung = input("\nDELETE eingeben zum Löschen: ")

    if bestaetigung == "DELETE":
        del benutzer[name]
        speichere_benutzer(benutzer, fernet)
        print("Benutzer wurde gelöscht")
    else:
        print("Abgebrochen.")

    pause()


def benutzer_menu(benutzer, userdaten, aktueller_benutzername, fernet):
    if not ist_admin(userdaten):
        trennlinie()
        print("ACCESS DENIED")
        print("Nur Administratoren dürfen Benutzer verwalten.")
        pause()
        return

    while True:
        trennlinie()

        print("BENUTZER VERWALTUNG\n")
        benutzer_anzeigen(benutzer)

        print("\n" + "-" * 80)

        print("\n1 - Benutzer hinzufügen")
        print("2 - Benutzer bearbeiten")
        print("3 - Passwort ändern")
        print("4 - Benutzer löschen")
        print("0 - Zurück")

        wahl = input("\nAuswahl: ")

        if wahl == "1":
            benutzer_hinzufuegen(benutzer, fernet)
        elif wahl == "2":
            benutzer_bearbeiten(benutzer, aktueller_benutzername, fernet)
        elif wahl == "3":
            benutzer_passwort_aendern(benutzer, fernet)
        elif wahl == "4":
            benutzer_loeschen(benutzer, aktueller_benutzername, fernet)
        elif wahl == "0":
            return
        else:
            print("Ungültige Eingabe.")
            pause()


def meine_clearance(userdaten):
    trennlinie()

    print("CLEARANCE INFORMATION\n")
    print(f"Rolle:      {userdaten['rolle']}")
    print(f"Clearance:  {CLEARANCE_NAMEN[userdaten['clearance']]}\n")

    for stufe in range(1, 5):
        if userdaten["clearance"] >= stufe:
            print(f"{CLEARANCE_NAMEN[stufe]}: ERLAUBT")
        else:
            print(f"{CLEARANCE_NAMEN[stufe]}: VERWEIGERT")

    pause()


def hauptmenu(benutzername, userdaten, datenbank, benutzer, fernet):
    while True:
        trennlinie()

        print("CLASSIFIED DATABASE")
        print(f"Angemeldet als: {benutzername}")
        print(f"Rolle: {userdaten['rolle']}")
        print(f"Clearance: {CLEARANCE_NAMEN[userdaten['clearance']]}\n")

        print("1 - Aktenübersicht öffnen")
        print("2 - Nur sichtbare Akten")
        print("3 - Suche")
        print("4 - Neue Akte erstellen")
        print("5 - Akte bearbeiten")
        print("6 - Akte löschen")
        print("7 - Benutzerverwaltung")
        print("8 - Meine Clearance")
        print("0 - Logout")

        wahl = input("\nAuswahl: ")

        if wahl == "1":
            akten_liste_anzeigen(datenbank, userdaten, nur_sichtbare=False)
        elif wahl == "2":
            akten_liste_anzeigen(datenbank, userdaten, nur_sichtbare=True)
        elif wahl == "3":
            suche(datenbank, userdaten)
        elif wahl == "4":
            akte_erstellen(datenbank, benutzername, userdaten, fernet)
        elif wahl == "5":
            akte_bearbeiten(datenbank, userdaten, fernet)
        elif wahl == "6":
            akte_loeschen(datenbank, userdaten, fernet)
        elif wahl == "7":
            benutzer_menu(benutzer, userdaten, benutzername, fernet)
        elif wahl == "8":
            meine_clearance(userdaten)
        elif wahl == "0":
            clear()
            print("Logout erfolgreich.\n")
            break
        else:
            print("Ungültige Eingabe.")
            pause()


if __name__ == "__main__":
    while True:
        fernet = master_login()

        benutzer = lade_benutzer(fernet)
        datenbank = lade_datenbank(fernet)

        benutzername, userdaten = login(benutzer)

        hauptmenu(
            benutzername,
            userdaten,
            datenbank,
            benutzer,
            fernet
        )