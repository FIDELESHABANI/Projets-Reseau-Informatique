# Corrigé : Quiz d'évaluation du bloc Switching

Ce fichier contient les réponses et les explications des 12 questions du `README.md`.

**Résultat obtenu : 11 / 12.** L'erreur portait sur la question 2 (802.1Q), revue et corrigée après le quiz.

---

## Partie 1 : Switching

**Question 1 : Réponse B**
Chaque VLAN forme un domaine de broadcast séparé, avec son propre sous-réseau IP. Un switch de couche 2 décide avec les adresses MAC et ne peut pas franchir cette frontière : il faut un équipement de couche 3.

**Question 2 : Réponse A** *(point revu)*
802.1Q insère un tag de 4 octets, contenant l'identifiant du VLAN, dans la trame Ethernet. Cela permet à plusieurs VLAN de circuler sur un seul lien. Regrouper des câbles, c'est EtherChannel. Bloquer les boucles, c'est STP.

**Question 3 : Réponse C**
Le Bridge ID combine la priorité et l'adresse MAC. Le plus petit gagne. En pratique, on baisse la priorité du switch voulu pour le forcer root bridge, plutôt que de laisser la MAC décider.

**Question 4 : Réponse D**
Sans STP, un broadcast tourne indéfiniment dans la boucle, car une trame de couche 2 n'a pas de TTL. Le port bloqué coupe la boucle et bascule en cas de panne du lien principal.

**Question 5 : Réponse A**
Sans Auto-MDIX, deux équipements de même type (switch vers switch) exigent un câble croisé, pour que l'émission de l'un tombe sur la réception de l'autre. Le 2960, plus récent, s'adapte automatiquement.

**Question 6 : Réponse B**
Le mode sticky apprend les adresses MAC autorisées sur le port et les ajoute à la running-config. Elles survivent au redémarrage si la configuration est sauvegardée (`write memory`).

**Question 7 : Réponse C**
Un port en err-disabled est désactivé logiciellement. Un `shutdown` suivi d'un `no shutdown` le réactive. Il retombera en err-disabled si l'appareil fautif est toujours branché.

**Question 8 : Réponse B**
Un port client voit une ou peu d'adresses MAC. Un trunk voit celles de tous les appareils situés derrière lui, donc la limite est vite dépassée et le port passe en violation.

**Question 9 : Réponse D**
Un côté `active` envoie des paquets LACP, un côté `passive` répond. Deux côtés `passive` attendent tous les deux et rien ne se forme. Le mode `on` est un EtherChannel statique, sans LACP.

**Question 10 : Réponse C**
Les deux câbles forment un lien logique unique (Po1). STP ne voit donc pas de boucle entre eux : les deux câbles transportent du trafic et, si l'un tombe, l'autre continue sans coupure.

---

## Partie 2 : DHCP

**Question 11 : Réponse C**
Ordre DORA : le client envoie un **D**iscover (broadcast), le serveur répond par un **O**ffer, le client accepte avec un **R**equest, puis le serveur confirme avec un **A**cknowledge et le bail est attribué.

**Question 12 : Réponse D**
`ip dhcp excluded-address` retire des adresses de la plage distribuable, par exemple la passerelle ou des équipements en IP fixe. Sans elle, le serveur pourrait attribuer une de ces adresses à un client et provoquer un conflit d'adresses.
