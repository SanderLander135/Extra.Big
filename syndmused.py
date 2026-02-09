import csv
import os  # Faili olemasolu kontrollimiseks
from datetime import datetime

# ==========================================================
# 1. SEADISTUSED - Siit saad muuta kuupäeva
# ==========================================================
OTSITAV_PAEV = 21
OTSITAV_KUU = 8

sisend_fail = 'andmed.csv'
valjund_fail = 'filtreeritud_tulemus.csv'


# ==========================================================
# 2. ABIFUNKTSIOONID
# ==========================================================

def tekita_kp_objekt(kp_string):
    """Proovib muuta teksti kuupäevaks (toetab . ja - eraldajat)"""
    if not kp_string or not kp_string.strip():
        return None

    kp_string = kp_string.strip()
    # Proovime erinevaid levinud kuupäeva vorminguid
    for vorming in ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y']:
        try:
            return datetime.strptime(kp_string, vorming)
        except ValueError:
            continue
    return None


def arvuta_vanus(synd, surm):
    """Arvutab täpse vanuse surmahetkel"""
    vanus = surm.year - synd.year
    # Kui surmakuupäev on kalendriaastas eespool kui sünnikuupäev, lahutame 1 aasta
    if (surm.month, surm.day) < (synd.month, synd.day):
        vanus -= 1
    return vanus


# ==========================================================
# 3. KONTROLL JA TÖÖTLEMINE
# ==========================================================

# Kontrollime, kas sisendfail on üldse olemas
if not os.path.exists(sisend_fail):
    print(f"VIGA: Faili '{sisend_fail}' ei leitud!")
    print("Palun veendu, et andmefail on skriptiga samas kaustas.")
else:
    tulemused = []

    with open(sisend_fail, mode='r', encoding='utf-8-sig') as f:
        # Tuvastame eraldaja automaatselt (kas ; või ,)
        test_rida = f.readline()
        f.seek(0)
        eraldaja = ';' if ';' in test_rida else ','

        lugeja = csv.DictReader(f, delimiter=eraldaja)
        # Eemaldame pealkirjadest võimalikud tühikud
        lugeja.fieldnames = [n.strip() for n in lugeja.fieldnames]

        # Lisame uue veeru nime päisesse
        uus_pais = lugeja.fieldnames + ['Vanus']

        for rida in lugeja:
            # Kasutame sinu faili päiseid: 'Sünniaeg' ja 'Surmaaeg'
            synd_kp = tekita_kp_objekt(rida.get('Sünniaeg'))
            surm_kp = tekita_kp_objekt(rida.get('Surmaaeg'))

            if not synd_kp:
                continue

            # Kontrollime, kas sünd või surm langes valitud päevale
            on_synnipaev = (synd_kp.day == OTSITAV_PAEV and synd_kp.month == OTSITAV_KUU)
            on_surmapaev = (surm_kp and surm_kp.day == OTSITAV_PAEV and surm_kp.month == OTSITAV_KUU)

            if on_synnipaev or on_surmapaev:
                vanus_lahter = ""

                # Kui isik on surnud, arvutame vanuse. Elaval jääb tühi.
                if surm_kp:
                    vanus_lahter = arvuta_vanus(synd_kp, surm_kp)

                # Muudame kuupäevad Eesti vormingusse (PP.KK.AAAA)
                rida['Sünniaeg'] = synd_kp.strftime('%d.%m.%Y')
                if surm_kp:
                    rida['Surmaaeg'] = surm_kp.strftime('%d.%m.%Y')
                else:
                    rida['Surmaaeg'] = ""

                # Lisame arvutatud vanuse
                rida['Vanus'] = vanus_lahter
                tulemused.append(rida)

    # ==========================================================
    # 4. SALVESTAMINE
    # ==========================================================
    if tulemused:
        with open(valjund_fail, mode='w', encoding='utf-8', newline='') as f:
            # Kirjutame semikooloniga eraldatud faili
            kirjutaja = csv.DictWriter(f, fieldnames=uus_pais, delimiter=';')
            kirjutaja.writeheader()
            kirjutaja.writerows(tulemused)
        print(f"Edukalt töödeldud! Leiti {len(tulemused)} isikut ja salvestati faili '{valjund_fail}'.")
    else:
        print(f"Otsing lõpetatud. Kuupäevaga {OTSITAV_PAEV}.{OTSITAV_KUU} seotud isikuid ei leitud.")