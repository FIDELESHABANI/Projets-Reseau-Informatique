# Projet Réseau — Sécurisation des ports d'accès (Port Security)

## 🎯 Contexte

Ce projet s'inscrit dans la continuité du déploiement réseau d'une PME
fictive (voir projets précédents : VLAN, Trunking/DHCP, Spanning Tree). Une
des exigences du cahier des charges de la direction était :

> *"Les ports destinés aux postes utilisateurs doivent être sécurisés : un
> employé ne doit pas pouvoir débrancher son PC et brancher un appareil
> inconnu à la place sans que ça déclenche une alerte."*

## 🎯 Objectif

Mettre en place **Port Security** sur un port d'accès Cisco pour restreindre
son usage à une seule adresse MAC autorisée, avec apprentissage automatique
(sticky) et désactivation immédiate du port en cas de tentative de connexion
d'un appareil non autorisé — puis valider ce comportement par un test réel
avec un appareil intrus.

## 🧰 Matériel utilisé

| Équipement | Rôle |
|------------|------|
| Cisco Catalyst 2950 | Switch de distribution, port testé : Fa0/3 |
| PC légitime | Adresse MAC autorisée : `10e7.c66a.e513` |
| Appareil "intrus" | Adresse MAC non autorisée : `2047.4749.744e` |

## ⚙️ Configuration appliquée

```
interface fastethernet 0/3
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
```

**Explication des paramètres :**
- `maximum 1` : un seul appareil autorisé simultanément sur ce port
- `mac-address sticky` : le switch apprend automatiquement la première
  adresse MAC connectée et la mémorise comme adresse autorisée, sans avoir
  besoin de la saisir manuellement
- `violation shutdown` : en cas de détection d'une adresse MAC non
  autorisée, le port est immédiatement désactivé (état `err-disabled`),
  nécessitant une intervention manuelle pour le réactiver — comportement
  volontairement visible pour alerter l'équipe IT

## 🧪 Déroulement du test

**1. État initial — apprentissage de l'adresse légitime :**
```
show mac address-table interface fastethernet 0/3
Vlan    Mac Address       Type        Ports
10      10e7.c66a.e513    DYNAMIC     Fa0/3
```

**2. Après activation de Port Security — vérification :**
```
show port-security interface fastethernet 0/3
Port Security              : Enabled
Port Status                : Secure-up
Maximum MAC Addresses      : 1
Sticky MAC Addresses       : 1
Last Source Address        : 10e7.c66a.e513
Security Violation Count   : 0
```

**3. Test de violation — branchement d'un appareil non autorisé :**

Logs générés instantanément par le switch :
```
%PORT_SECURITY-2-PSECURE_VIOLATION: Security violation occurred,
caused by MAC address 2047.4749.744e on port FastEthernet0/3.
%PM-4-ERR_DISABLE: psecure-violation error detected on Fa0/3,
putting Fa0/3 in err-disable state
%LINEPROTO-5-UPDOWN: Line protocol on Interface FastEthernet0/3, changed state to down
%LINK-3-UPDOWN: Interface FastEthernet0/3, changed state to down
```

Vérification après violation :
```
show port-security interface fastethernet 0/3
Port Status                : Secure-shutdown
Last Source Address        : 2047.4749.744e
Security Violation Count   : 1
```

→ Le port a été désactivé automatiquement dès la détection de l'appareil
non autorisé, sans qu'aucune trame de cet appareil ne puisse atteindre le
réseau. L'adresse MAC de l'intrus a été journalisée, exploitable pour une
investigation de sécurité.

**4. Procédure de récupération :**

Après avoir reconnecté le PC légitime, réactivation manuelle du port :
```
interface fastethernet 0/3
shutdown
no shutdown
```

**5. Vérification finale — source de vérité (`show port-security address`) :**
```
show port-security address
Vlan    Mac Address       Type            Ports   Remaining Age
10      10e7.c66a.e513    SecureSticky    Fa0/3        -
```

→ Confirmation que seule l'adresse MAC légitime reste autorisée sur le
port après la procédure de récupération.

## 🐞 Point de vigilance rencontré

Après le cycle `shutdown`/`no shutdown`, le champ `Last Source Address` de
`show port-security interface` continuait d'afficher l'adresse de
l'appareil intrus, ce qui pouvait laisser croire à une mauvaise
configuration. Vérification faite avec `show port-security address` (qui
liste les adresses **réellement autorisées**, pas le dernier historique) :
seule l'adresse légitime `10e7.c66a.e513` y figurait. Leçon retenue :
`Last Source Address` est un champ d'historique, pas la source de vérité de
la configuration active — toujours croiser avec `show port-security
address` en cas de doute.

## 📚 Compétences démontrées

- Configuration de Port Security avec apprentissage sticky
- Compréhension des modes de violation (`shutdown`, `restrict`, `protect`) et choix argumenté du mode le plus adapté à une exigence de sécurité visible
- Test réel de sécurité physique : simulation d'une tentative de connexion non autorisée
- Lecture et interprétation des logs de sécurité générés par le switch en temps réel
- Procédure de récupération d'un port en état `err-disabled`
- Distinction entre un champ d'historique et la source de vérité d'une configuration active

---
*Projet réalisé dans le cadre d'une formation pratique réseau — Bloc 3 : Switching, Phase C (Port Security) du projet PME multi-switch.*
