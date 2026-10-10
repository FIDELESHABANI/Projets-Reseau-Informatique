# Projet : routage statique entre deux LAN avec VLAN (1841, 819, 2960, 3550)

## Contexte

Deux sites, chacun avec ses VLAN, sont reliés par deux routeurs. Rien ne circule d'un site à l'autre tant que chaque routeur ne connaît pas les réseaux de l'autre : ce projet met en place le **routage statique** (routes précises, puis route par défaut) et montre pourquoi une route statique est **unidirectionnelle**.

Il combine les deux méthodes de routage inter-VLAN déjà vues : **router-on-a-stick** sur le LAN1 (le 1841 a plusieurs ports routés) et **SVI** sur le LAN2 (le 819 n'a qu'un port routé, Gi0, qui sert à la liaison).

Les images reproduisent les sorties console relevées lors de la pratique sur du matériel réel. Les photos (câblage, pings, tracert, incident) sont de vraies captures.

## Objectifs

- Construire deux LAN avec deux VLAN chacun (VLAN 10 et 20, VLAN 30 et 40).
- Relier deux routeurs et prouver la liaison en couche 1, 2 et 3.
- Constater l'échec sans route, ajouter les routes statiques une par une et prouver l'aller et le retour.
- Remplacer les routes précises d'un routeur « feuille » par une route par défaut.
- Diagnostiquer un incident volontaire du bas vers le haut et prouver la réparation par un test.

## Matériel

| Équipement | Nom | Rôle |
|---|---|---|
| Switch Cisco Catalyst 2960 | SW-2960 | Switch du LAN1 (VLAN 10 et 20, trunk) |
| Routeur Cisco 1841, IOS 12.4(24)T3 | R1-1841 | Passerelle du LAN1 (router-on-a-stick), liaison vers R2 |
| Routeur Cisco C819G-4G, IOS 15.5(3)M | R2-819 | Passerelle du LAN2 (SVI), liaison vers R1 |
| Switch Cisco Catalyst 3550 | SW-3550 | Switch du LAN2 en couche 2 (VLAN 30 et 40, trunk) |
| PC-A (PC avec Git Bash) | | Machine du LAN1 |
| PC-B (portable Dell) | | Machine du LAN2 |
| Câbles Ethernet droits, un câble croisé, câble console RJ45 vers USB | | Liaisons et configuration |

## Plan d'adressage

| VLAN | Nom | Réseau | Passerelle | Équipement |
|---|---|---|---|---|
| 10 | COMPTA | 192.168.10.0/24 | 192.168.10.1 | R1 Fa0/0.10 |
| 20 | IT | 192.168.20.0/24 | 192.168.20.1 | R1 Fa0/0.20 |
| 30 | HR | 192.168.30.0/24 | 192.168.30.1 | R2 Vlan30 |
| 40 | FIN | 192.168.40.0/24 | 192.168.40.1 | R2 Vlan40 |
| Liaison | | 10.0.0.0/30 | R1 : 10.0.0.1, R2 : 10.0.0.2 | R1 Fa0/1, R2 Gi0 |

PC-A : 192.168.10.10 (passerelle 192.168.10.1), sur Fa0/1 du 2960.
PC-B : 192.168.30.10 (passerelle 192.168.30.1), sur Fa0/1 du 3550.

## Topologie

```mermaid
graph LR
    PCA["PC-A<br/>192.168.10.10"] --- SW2960["SW-2960<br/>VLAN 10 COMPTA / VLAN 20 IT"]
    SW2960 -- "Gi0/1 : trunk 802.1Q" --- R1["R1-1841<br/>Fa0/0.10 : 192.168.10.1<br/>Fa0/0.20 : 192.168.20.1<br/>Fa0/1 : 10.0.0.1"]
    R1 -- "liaison 10.0.0.0/30<br/>câble croisé" --- R2["R2-819<br/>Gi0 : 10.0.0.2<br/>Vlan30 : 192.168.30.1<br/>Vlan40 : 192.168.40.1"]
    R2 -- "Fa0 : trunk 802.1Q" --- SW3550["SW-3550 (couche 2)<br/>VLAN 30 HR / VLAN 40 FIN"]
    SW3550 --- PCB["PC-B<br/>192.168.30.10"]
```

![Photo du câblage](assets/photo-cablage.jpeg)

## Ordre de câblage

1. PC-A sur **Fa0/1** du 2960 (VLAN 10).
2. **Gi0/1 du 2960** vers **Fa0/0 du 1841** (trunk), câble droit.
3. **Fa0 du 819** vers **Fa0/24 du 3550** (trunk), câble droit : le lien est monté.
4. PC-B sur **Fa0/1** du 3550 (VLAN 30).
5. **Fa0/1 du 1841** vers **Gi0 du 819** : câble **croisé** (liaison de routeur à routeur), le lien est monté.
6. Wi-Fi coupé sur les deux PC pendant tous les tests.

## Remise à zéro préalable

Avant de commencer, les quatre équipements ont été remis à zéro pour repartir d'une configuration vierge.

- **1841** : `write erase`, puis `reload` (réponse `no` à la question sur la sauvegarde).
- **2960** : `erase startup-config`.
- **3550** : `write erase`, `delete flash:vlan.dat`, puis `reload`.
- **819** : aucune ancienne configuration (startup-config à 0 octet), mais d'anciens VLAN étaient stockés dans `vlan.dat` (voir les incidents).

## Commandes tapées

Remarque : certaines commandes (affectation des ports du 3550, interface physique Fa0/0 du 1841, effacements) sont données sous leur forme standard. Leur effet est prouvé par les sorties des commandes `show`.

### Switch 2960

```
enable
configure terminal
hostname SW-2960
vlan 10
 name COMPTA
 exit
vlan 20
 name IT
 exit
interface range fa0/1-12
 switchport mode access
 switchport access vlan 10
 exit
interface range fa0/13-24
 switchport mode access
 switchport access vlan 20
 exit
interface gi0/1
 switchport mode trunk
 description TRUNK-VERS-R1
 end
show vlan brief
show interfaces gi0/1 switchport | include Administrative Mode
show interfaces trunk
write memory
show startup-config | include hostname|trunk|access vlan
```

### Routeur 1841 (R1)

```
configure terminal
hostname R1-1841
interface fa0/0
 no ip address
 no shutdown
 exit
interface fa0/0.10
 description GW-VLAN10-COMPTA
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
 exit
interface fa0/0.20
 description GW-VLAN20-IT
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
 end
show ip interface brief
show ip route
write memory
show startup-config | include hostname|encapsulation
configure terminal
interface fa0/1
 description LIAISON-VERS-R2
 ip address 10.0.0.1 255.255.255.252
 no shutdown
 end
ping 10.0.0.2
ping 192.168.30.1
show ip route 192.168.30.1
configure terminal
ip route 192.168.30.0 255.255.255.0 10.0.0.2
ip route 192.168.40.0 255.255.255.0 10.0.0.2
do show ip route static
end
write memory
show startup-config | include ip route
```

### Switch 3550 (couche 2)

```
enable
configure terminal
hostname SW-3550
vlan 30
 name HR
 exit
vlan 40
 name FIN
 exit
interface range fa0/1-12
 switchport mode access
 switchport access vlan 30
 exit
interface range fa0/13-23
 switchport mode access
 switchport access vlan 40
 exit
interface fa0/24
 switchport trunk encapsulation dot1q
 switchport mode trunk
 description TRUNK-VERS-R2
 end
show vlan brief
show interfaces trunk
write memory
show startup-config | include hostname|trunk|access vlan
```

### Routeur 819 (R2)

```
enable
show version | include register
dir nvram:
configure terminal
config-register 0x2102
hostname R2-819
vlan 30
 name HR
 exit
vlan 40
 name FIN
 exit
interface fa0
 switchport mode trunk
 description TRUNK-VERS-SW-3550
 exit
interface vlan 30
 description GW-VLAN30-HR
 ip address 192.168.30.1 255.255.255.0
 no shutdown
 exit
interface vlan 40
 description GW-VLAN40-FIN
 ip address 192.168.40.1 255.255.255.0
 no shutdown
 exit
interface gi0
 description LIAISON-VERS-R1
 ip address 10.0.0.2 255.255.255.252
 no shutdown
 end
show vlan-switch brief
show ip interface brief
write memory
configure terminal
ip route 192.168.10.0 255.255.255.0 10.0.0.1
ip route 192.168.20.0 255.255.255.0 10.0.0.1
do show ip route static
ip route 0.0.0.0 0.0.0.0 10.0.0.1
no ip route 192.168.10.0 255.255.255.0 10.0.0.1
no ip route 192.168.20.0 255.255.255.0 10.0.0.1
end
write memory
show startup-config | include ip route
configure terminal
no vlan 10
no vlan 20
no vlan 50
end
show vlan-switch brief
```

Sur ce 819, la commande des VLAN est `show vlan-switch brief` : `show vlan` est ambiguë.

### PC-A et PC-B

```
ipconfig
ping 192.168.10.1
ping 192.168.20.1
ping 192.168.30.10
ping 192.168.40.1
tracert 192.168.30.10
```

## LAN1 : switch 2960 et routeur 1841

![show vlan brief du 2960](assets/01-show-vlan-brief-2960.svg)

![Trunk du 2960](assets/02-trunk-2960.svg)

Avant le branchement, les interfaces du 1841 sont en `up/down` :

![R1 avant câblage](assets/03-r1-avant-cablage.svg)

Après le branchement, tout passe en `up/up` :

![R1 après câblage](assets/04-r1-apres-cablage.svg)

Les deux routes `C` sont apparues seules :

![Table de routage de R1 (LAN1)](assets/05-r1-route-lan1.svg)

![Pings de PC-A vers ses passerelles](assets/06-ping-pc-a-passerelles.svg)

Sauvegarde du LAN1 :

![Sauvegarde du 1841](assets/07-sauvegarde-r1.svg)

![Startup-config du 2960](assets/08-startup-2960.svg)

## LAN2 : routeur 819 et switch 3550

Le 819 contenait d'anciens VLAN (`lab1`, `lab2`, `lab4`) stockés dans `vlan.dat` :

![VLAN du 819 avant nettoyage](assets/09-vlan-819-avant-nettoyage.svg)

![Trunk et SVI du 819](assets/10-819-config-trunk-svi.svg)

Les deux SVI montent en `up/up` dès que le trunk est câblé :

![SVI du 819 en up/up](assets/11-819-svi-up.svg)

Le registre `0x2102` s'appliquera au prochain redémarrage :

![Sauvegarde du 819](assets/12-sauvegarde-819.svg)

![VLAN du 3550](assets/13-show-vlan-brief-3550.svg)

![Trunk du 3550](assets/14-trunk-3550.svg)

![Sauvegarde du 3550](assets/15-sauvegarde-3550.svg)

Les anciens VLAN du 819 sont supprimés en fin de projet :

![VLAN du 819 après nettoyage](assets/16-vlan-819-apres-nettoyage.svg)

## Liaison entre R1 et R2

Le câble croisé est monté, et le ping de 10.0.0.1 vers 10.0.0.2 réussit (le premier paquet est perdu à cause de l'ARP) :

![Liaison R1-R2](assets/17-liaison-r1-r2.svg)

## Routage statique

### Sans route : l'échec attendu

R1 ne connaît que ses réseaux directement connectés. Il affiche des points, car il n'envoie même pas le paquet :

![Ping sans route](assets/18-sans-route.svg)

### Première route sur R1

Un ping lancé depuis R1 prend l'adresse 10.0.0.1 comme source : R2 la connaît déjà, donc la réponse revient sans route de retour.

![Première route de R1](assets/19-premiere-route-r1.svg)

### Une route sur R1 seulement : timeout depuis PC-A

La demande arrive chez PC-B, mais R2 n'a aucune route vers le LAN1 et jette la réponse. PC-A voit un timeout.

![Ping de PC-A sans route de retour](assets/20-ping-pc-a-sans-retour.svg)

### Routes de retour sur R2

![Routes de retour de R2](assets/21-routes-retour-r2.svg)

Le ping de PC-A vers PC-B réussit alors avec un TTL de 126 (128 moins 2 routeurs) :

![Ping de PC-A vers PC-B (texte)](assets/22-ping-pc-a-vers-pc-b.svg)

![Ping de PC-A vers PC-B (capture)](assets/statique-ping-pc-a-vers-pc-b.jpg)

Le tracert montre trois sauts : R1, R2, PC-B. Les switches n'apparaissent pas.

![Tracert de PC-A vers PC-B (texte)](assets/23-tracert-pc-a-vers-pc-b.svg)

![Tracert de PC-A vers PC-B (capture)](assets/statique-tracert-pc-a-vers-pc-b.jpg)

Test du VLAN 40 depuis PC-A (TTL 254 : le 819 répond, et la réponse traverse R1) :

![Ping de PC-A vers le VLAN 40 (texte)](assets/24-ping-pc-a-vlan40.svg)

![Ping de PC-A vers le VLAN 40 (capture)](assets/statique-ping-pc-a-vers-vlan40.jpg)

Test du VLAN 20 depuis PC-B (TTL 254 : R1 répond, et la réponse traverse R2) :

![Ping de PC-B vers le VLAN 20](assets/statique-ping-pc-b-vers-vlan20.jpeg)

## Route par défaut sur R2

R2 est un site « feuille » : tout ce qui n'est pas son LAN passe par R1. Une route par défaut est ajoutée, puis les deux routes précises sont retirées. La ligne `Gateway of last resort`, qui affichait `is not set` jusqu'ici, se remplit.

![Route par défaut sur R2](assets/25-route-defaut-r2.svg)

Les pings de PC-B continuent de fonctionner avec la seule route par défaut :

![Ping de PC-B vers PC-A (route par défaut)](assets/defaut-ping-pc-b-vers-pc-a.jpeg)

![Ping de PC-B vers le VLAN 20 (route par défaut)](assets/defaut-ping-pc-b-vers-vlan20.jpeg)

Les routes enregistrées en fin de projet :

![Routes dans les startup-config](assets/26-startup-routes.svg)

## Incident volontaire : retour cassé sur R2

La route par défaut de R2 est retirée **sans sauvegarder**.

### Symptôme

Le ping de PC-A vers PC-B donne 4 timeouts, et le tracert reste muet après R1. Les statistiques affichent `Received = 0`, donc aucun message d'erreur caché.

![Ping et tracert de l'incident (texte)](assets/27-incident-ping-tracert.svg)

![Ping de PC-A en timeout](assets/incident-ping-pc-a-timeout.jpg)

![Tracert de PC-A pendant l'incident](assets/incident-tracert-pc-a.jpg)

### Diagnostic, du bas vers le haut

- La liaison R1-R2 répond (ping 10.0.0.2 : 5/5).
- R1 a une route vers le LAN2 (`show ip route 192.168.30.10`).
- R2 n'a aucune route vers le LAN1 (`% Network not in table`).

![Diagnostic](assets/28-incident-diagnostic.svg)

### Cause et réparation

La route par défaut de R2 avait été retirée : R2 ne savait pas renvoyer les réponses vers le LAN1. Correction : `ip route 0.0.0.0 0.0.0.0 10.0.0.1` sur R2.

### Preuve

Le ping de PC-A vers PC-B redonne 4 réponses avec un TTL de 126. Seule la route par défaut a changé entre l'échec et la réussite.

![Réparation et preuve (texte)](assets/29-incident-reparation.svg)

![Ping de PC-A après réparation](assets/incident-ping-pc-a-reparation.jpg)

## Autres constats

- **Anciens VLAN dans le 819** : `lab1` (10), `lab2` (20) et `lab4` (50) étaient stockés dans `vlan.dat`, que ni `write erase` ni un changement de configuration n'effacent. Ils portaient les mêmes numéros que ceux du LAN1 et ont été supprimés avec `no vlan`.
- **Commande des VLAN sur le 819** : `show vlan brief` est « ambiguë » ; la bonne commande est `show vlan-switch brief`.
- **Filtres `include`** : un filtre mal écrit (espaces autour des `|`, mauvaise casse) ne prouve rien quand il ne retourne rien.
- **Ping sans route** : R1 affiche des points (`.....`) et non des `U`. Les `U` n'apparaissent que si un autre routeur renvoie un « destination unreachable ».
- **Câbles** : le trunk entre le 3550 et le 819 est monté avec un câble droit, et la liaison R1-R2 avec un câble croisé. Je n'ai pas testé l'autre type de câble sur chacun de ces liens.
- **ipconfig de PC-B** : l'image `30-ipconfig-pc-b.svg` reproduit le texte de la capture d'origine. Seul le bloc Ethernet y figure.

![ipconfig et pings de PC-B](assets/30-ipconfig-pc-b.svg)

### Points non élucidés

- La ligne `clock rate 2000000` est revenue sur `Serial0/0/0` du 1841 après effacement, sans câble série branché.
- Le registre `0x2102` du 819 est configuré mais n'a pas été vérifié après un `reload`.
- `Cellular0` est `up/up` sur le 819 alors que la carte SIM est absente du slot 0.

## Tableau des tests

| Test | Depuis | Vers | Résultat | Lecture |
|---|---|---|---|---|
| Ping passerelle | PC-A | 192.168.10.1 | 4/4, TTL 255 | R1 répond lui-même |
| Ping passerelle | PC-A | 192.168.20.1 | 4/4, TTL 255 | R1 répond lui-même (autre sous-interface) |
| Ping passerelles | PC-B | 192.168.30.1 et 192.168.40.1 | 4/4, TTL 255 | R2 répond lui-même via ses SVI |
| Ping de liaison | R1 | 10.0.0.2 | 5/5 (le premier paquet est perdu : ARP) | Liaison R1-R2 en couche 3 |
| Ping sans route | R1 | 192.168.30.1 | 0/5 | Aucune route : `% Network not in table` |
| Ping avec route sur R1 | R1 | 192.168.30.1 | 5/5 | Source 10.0.0.1, connue de R2 |
| Ping avec route sur R1 seulement | PC-A | 192.168.30.10 | 0/4, timeout | R2 n'a pas de route de retour |
| Ping avec routes dans les deux sens | PC-A | 192.168.30.10 | 4/4, TTL 126 | 128 moins 2 routeurs |
| Tracert | PC-A | 192.168.30.10 | 3 sauts : 192.168.10.1, 10.0.0.2, 192.168.30.10 | Chemin R1, R2, PC-B |
| Ping vers le VLAN 40 | PC-A | 192.168.40.1 | 4/4, TTL 254 | R2 répond, la réponse traverse R1 |
| Ping vers le VLAN 20 | PC-B | 192.168.20.1 | 4/4, TTL 254 | R1 répond, la réponse traverse R2 |
| Ping avec route par défaut seule | PC-B | 192.168.10.10 | 4/4, TTL 126 | La route par défaut suffit |
| Incident : retour cassé | PC-A | 192.168.30.10 | 0/4, timeout | Route par défaut de R2 retirée |
| Réparation | PC-A | 192.168.30.10 | 4/4, TTL 126 | Preuve par le test |

## Ce que j'ai retenu

- Un routeur ne connaît que ses réseaux directement connectés : tout autre réseau demande une route.
- Une route statique est **unidirectionnelle** : il en faut une sur chaque routeur, une pour l'aller et une pour le retour.
- Quand la route de retour manque, le routeur qui jette la réponse envoie l'erreur à PC-B, et PC-A voit seulement un timeout.
- Devant un timeout, le problème se trouve au dernier saut qui répond ou juste derrière lui, et un `*` ne prouve pas que le paquet n'est pas arrivé.
- Sur Ethernet, une route statique doit pointer vers un **prochain saut** ; l'interface de sortie convient aux liaisons point à point.
- La route par défaut (`0.0.0.0/0`) ne s'applique qu'en dernier recours, grâce au préfixe le plus long ; elle remplit `Gateway of last resort`.
- Un routeur « feuille » n'a besoin que d'une route par défaut vers son voisin.
- Un SVI peut exister sur un routeur doté de ports de commutation (le 819), pas seulement sur un switch de couche 3.
- Le TTL aide à lire le chemin : 255 (l'équipement répond lui-même), 254 (un routeur traversé au retour), 126 (deux routeurs).
- `write erase` n'efface pas `vlan.dat` : les anciens VLAN peuvent revenir.
- Une réparation se prouve par un test, et on ne sauvegarde jamais pendant un incident.

## Compétences démontrées

- Construction de deux LAN avec VLAN, trunks 802.1Q, sous-interfaces et SVI.
- Configuration de routes statiques et d'une route par défaut sur deux routeurs Cisco.
- Lecture de la table de routage, du TTL et de l'origine de chaque ligne de ping et de tracert.
- Diagnostic méthodique d'un incident, du bas vers le haut, avec preuve de la réparation.
- Remise à zéro d'équipements Cisco, y compris `vlan.dat`.
- Sauvegarde et vérification de la startup-config.
- Documentation d'un projet réalisé sur du matériel réel.

## Remise en état

Sur chaque équipement :

```
write erase
reload
```

Sur le 2960, le 3550 et le 819, supprimer aussi les VLAN enregistrés :

```
delete flash:vlan.dat
```

Sur PC-A (invite de commandes en administrateur), supprimer la règle ICMP créée pendant un projet précédent :

```
netsh advfirewall firewall delete rule name="ICMP-TEST"
```

Sur les PC : remettre l'Ethernet en IP automatique et réactiver le Wi-Fi.
