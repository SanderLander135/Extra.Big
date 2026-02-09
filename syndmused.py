import csv
from datetime import datetime

# ==========================================================
# 1. SEADISTUSED - Siit saad muuta kuupäeva
# ==========================================================
MINU_PAEV = 21
MINU_KUU = 8

sisend_fail = 'andmed.csv'
valjund_fail = 'filtreeritud_tulemus.csv'


# ==========================================================
# 2. ABIFUNKTSIOONID
# ==========================================================

def tekita_kp_objekt(kp_string):
    """Proovib muuta teksti kuupäevaks (toetab nii . kui - eraldajat)"""
    if not kp_string or not kp_string.strip():
        return None

    kp_string = kp_string.strip()
    for vorming in ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y']:
        try:
            return datetime.strptime(kp_string, vorming)
        except ValueError:
            continue
    return None


def arvuta_vanus(synd, surm):
    """Arvutab täpse vanuse (arvestades kuud ja päeva)"""
    vanus = surm.year - synd.year
    if (surm.month, surm.day) < (synd.month, synd.day):
        vanus -= 1
    return vanus


# ==========================================================
# 3. ANDMETE TÖÖTLEMINE
# ==========================================================

tulemused = []

with open(sisend_fail, mode='r', encoding='utf-8-sig') as f:
    # Tuvastame eraldaja (koma või semikoolon)
    test_rida = f.readline()
    f.seek(0)
    eraldaja = ';' if ';' in test_rida else ','

    lugeja = csv.DictReader(f, delimiter=eraldaja)
    # Eemaldame päistest tühikud
    lugeja.fieldnames = [n.strip() for n in lugeja.fieldnames]

    # Uue faili päis (lisame Vanuse veeru)
    uus_pais = lugeja.fieldnames + ['Vanus']

    for rida in lugeja:
        # Kasutame sinu faili päiseid: 'Sünniaeg' ja 'Surmaaeg'
        synd_kp = tekita_kp_objekt(rida.get('Sünniaeg'))
        surm_kp = tekita_kp_objekt(rida.get('Surmaaeg'))

        if not synd_kp:
            continue

        # KONTROLL: Kas sündis või suri 21. augustil
        on_synnipaev = (synd_kp.day == MINU_PAEV and synd_kp.month == MINU_KUU)
        on_surmapaev = (surm_kp and surm_kp.day == MINU_PAEV and surm_kp.month == MINU_KUU)

        if on_synnipaev or on_surmapaev:
            vanus_lahter = ""

            # Kui isik on surnud, arvutame vanuse
            if surm_kp:
                vanus_lahter = arvuta_vanus(synd_kp, surm_kp)

            # MUUDAME KUUPÄEVAD EESTI FORMAATI (PP.KK.AAAA)
            rida['Sünniaeg'] = synd_kp.strftime('%d.%m.%Y')
            if surm_kp:
                rida['Surmaaeg'] = surm_kp.strftime('%d.%m.%Y')
            else:
                rida['Surmaaeg'] = ""

            rida['Vanus'] = vanus_lahter
            tulemused.append(rida)

# ==========================================================
# 4. SALVESTAMINE
# ==========================================================

with open(valjund_fail, mode='w', encoding='utf-8', newline='') as f:
    kirjutaja = csv.DictWriter(f, fieldnames=uus_pais, delimiter=';')
    kirjutaja.writeheader()
    kirjutaja.writerows(tulemused)

print(f"Valmis! Leiti {len(tulemused)} isikut.")
print(f"Tulemused salvestati faili: {valjund_fail}")