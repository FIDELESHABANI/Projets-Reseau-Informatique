from xml.sax.saxutils import escape
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'img') + os.sep
FONT = "Consolas, Menlo, 'DejaVu Sans Mono', 'Courier New', monospace"
COL = {'p':'#7ee787','c':'#e6edf3','o':'#b1bac4','ok':'#7ee787','err':'#ff7b72','hl':'#f2cc60','dim':'#6e7681'}

def terminal(name, title, lines, accent='#3b82f6'):
    """lines: str or list of (text, class) segments."""
    norm = []
    for l in lines:
        if isinstance(l, str): l = [(l, 'o')]
        norm.append(l)
    maxlen = max(sum(len(t) for t, _ in l) for l in norm)
    cw, lh = 8.6, 21
    w = int(max(560, maxlen*cw + 48))
    h = 44 + len(norm)*lh + 22
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">',
         f'<title>{escape(title)}</title>',
         f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="10" fill="#0d1117" stroke="#30363d"/>',
         f'<path d="M0.5 10.5a10 10 0 0 1 10-10H{w-10.5}a10 10 0 0 1 10 10V34H0.5z" fill="#161b22"/>',
         f'<rect x="0.5" y="33" width="{w-1}" height="2" fill="{accent}"/>',
         '<circle cx="20" cy="17" r="6" fill="#ff5f56"/><circle cx="40" cy="17" r="6" fill="#ffbd2e"/><circle cx="60" cy="17" r="6" fill="#27c93f"/>',
         f'<text x="82" y="21" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#8b949e">{escape(title)}</text>']
    y = 58
    for l in norm:
        spans = ''.join(f'<tspan fill="{COL[c]}">{escape(t)}</tspan>' for t, c in l)
        s.append(f'<text x="22" y="{y}" font-family="{FONT}" font-size="14" xml:space="preserve">{spans}</text>')
        y += lh
    s.append('</svg>')
    open(OUT+name, 'w', encoding='utf-8').write('\n'.join(s))

W = 'Serveur2019 – Invite de commandes'
R = 'IPCop – console (root)'

terminal('01-ipconfig-statique.svg', W, [
 [('C:\\> ', 'p'), ('ipconfig /all', 'c')],
 '',
 'Nom de l’hôte . . . . . . . . . . : Serveur2019',
 'Carte Ethernet Ethernet :',
 [('   DHCP activé. . . . . . . . . . . . : ', 'o'), ('Non', 'hl')],
 '   Adresse IPv4. . . . . . . . . . . . : 192.168.1.10(préféré)',
 '   Masque de sous-réseau. . . . . . . . : 255.255.255.0',
 [('   Passerelle par défaut. . . . . . . . : ', 'o'), ('192.168.1.1', 'ok')],
 '   Serveurs DNS. . . . . . . . . . . . : 192.168.1.1',
 '                                          8.8.8.8',
], '#3b82f6')

terminal('02-ping-refuse.svg', W, [
 [('C:\\> ', 'p'), ('ping 8.8.8.8', 'c')],
 '',
 'Envoi d’une requête \'Ping\'  8.8.8.8 avec 32 octets de données :',
 [('Réponse de 192.168.1.1 : Impossible de joindre le port de destination.', 'err')],
 [('Réponse de 192.168.1.1 : Impossible de joindre le port de destination.', 'err')],
 [('Réponse de 192.168.1.1 : Impossible de joindre le port de destination.', 'err')],
 [('Réponse de 192.168.1.1 : Impossible de joindre le port de destination.', 'err')],
 '',
 [('→ la réponse vient d’IPCop (192.168.1.1) : c’est lui qui refuse.', 'hl')],
], '#ef4444')

terminal('03-ifconfig-ipcop.svg', R, [
 [('root@ipcop:~ # ', 'p'), ('ifconfig -a', 'c')],
 [('lan-1', 'hl'), (': flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500', 'o')],
 '        inet 192.168.1.1  netmask 255.255.255.0',
 'lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 16436',
 '        inet 127.0.0.1  netmask 255.0.0.0',
 [('wan-1', 'hl'), (': flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500', 'o')],
 '        inet 10.0.2.15  netmask 255.255.255.0',
 [('(extrait : l’interface rouge s’appelle wan-1, pas red0)', 'dim')],
], '#f59e0b')

terminal('04-ping-ipcop-ok.svg', R, [
 [('root@ipcop:~ # ', 'p'), ('ping -c 4 8.8.8.8', 'c')],
 'PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.',
 [('64 bytes from 8.8.8.8: icmp_seq=1 ttl=114 time=23.7 ms', 'ok')],
 [('64 bytes from 8.8.8.8: icmp_seq=2 ttl=114 time=23.8 ms', 'ok')],
 [('64 bytes from 8.8.8.8: icmp_seq=3 ttl=114 time=35.2 ms', 'ok')],
 [('64 bytes from 8.8.8.8: icmp_seq=4 ttl=114 time=28.0 ms', 'ok')],
 '--- 8.8.8.8 ping statistics ---',
 '4 packets transmitted, 4 received, 0% packet loss',
 [('→ IPCop a bien internet : le blocage est dans son pare-feu / NAT.', 'hl')],
], '#f59e0b')

terminal('05-fw-outgoing-vide.svg', R, [
 [('root@ipcop:~ # ', 'p'), ('iptables -L FW_OUTGOING -n -v', 'c')],
 'Chain FW_OUTGOING (1 references)',
 ' pkts bytes target     prot opt in     out     source      destination',
 [('(aucune règle : rien n’autorise le trafic du réseau vert vers internet)', 'err')],
], '#ef4444')

terminal('06-rednat-vide.svg', R, [
 [('root@ipcop:~ # ', 'p'), ('iptables -t nat -L REDNAT -n -v', 'c')],
 'Chain REDNAT (1 references)',
 ' pkts bytes target     prot opt in     out     source      destination',
 [('(aucune règle : pas de traduction d’adresses, internet ne sait pas répondre)', 'err')],
], '#ef4444')

terminal('07-regles-ajoutees.svg', R, [
 [('root@ipcop:~ # ', 'p'), ('iptables -I FW_OUTGOING -i lan-1 -o wan-1 -j ACCEPT', 'c')],
 [('root@ipcop:~ # ', 'p'), ('iptables -t nat -A REDNAT -s 192.168.1.0/24 -o wan-1 -j MASQUERADE', 'c')],
 [('root@ipcop:~ # ', 'p'), ('iptables -t nat -L REDNAT -n -v', 'c')],
 'Chain REDNAT (1 references)',
 ' pkts bytes target      prot opt in  out    source           destination',
 [('    0     0 MASQUERADE  all  --  *   wan-1  192.168.1.0/24   0.0.0.0/0', 'ok')],
 [('(les noms d’interface respectent la casse : lan-1, pas LAN-1)', 'dim')],
], '#22c55e')

terminal('08-ping-ok.svg', W, [
 [('C:\\> ', 'p'), ('ping 8.8.8.8', 'c')],
 '',
 'Envoi d’une requête \'Ping\'  8.8.8.8 avec 32 octets de données :',
 [('Réponse de 8.8.8.8 : octets=32 temps=22 ms TTL=113', 'ok')],
 [('Réponse de 8.8.8.8 : octets=32 temps=24 ms TTL=113', 'ok')],
 [('Réponse de 8.8.8.8 : octets=32 temps=22 ms TTL=113', 'ok')],
 [('Réponse de 8.8.8.8 : octets=32 temps=19 ms TTL=113', 'ok')],
 '',
 'Paquets : envoyés = 4, reçus = 4, perdus = 0 (perte 0%)',
], '#22c55e')

terminal('09-rc-firewall-local.svg', R, [
 [('root@ipcop:~ # ', 'p'), ('grep -n iptables /etc/rc.d/rc.firewall.local', 'c')],
 [('17:', 'dim'), ('iptables -t nat -A REDNAT -s 192.168.1.0/24 -o wan-1 -j MASQUERADE', 'ok')],
 [('18:', 'dim'), ('iptables -I FW_OUTGOING -i lan-1 -o wan-1 -j ACCEPT', 'ok')],
 [('(règles rejouées à chaque démarrage du pare-feu)', 'dim')],
], '#22c55e')

terminal('10-dhcp-client-seul.svg', R, [
 [('root@ipcop:~ # ', 'p'), ('ps aux | grep dhcp', 'c')],
 'root   1120  0.0  0.1  2196  580 ?  Ss  10:36  0:00 /usr/sbin/dhcpcd --hostname=ipcop wan-1',
 [('(seul dhcpcd, le client de wan-1 : aucun serveur DHCP pour le réseau local)', 'hl')],
], '#f59e0b')

terminal('11-ipconfig-dhcp.svg', W, [
 [('C:\\> ', 'p'), ('ipconfig /all', 'c')],
 '',
 'Carte Ethernet Ethernet :',
 [('   DHCP activé. . . . . . . . . . . . : ', 'o'), ('Oui', 'ok')],
 [('   Adresse IPv4. . . . . . . . . . . . : ', 'o'), ('192.168.1.104(préféré)', 'ok')],
 '   Masque de sous-réseau. . . . . . . . : 255.255.255.0',
 '   Passerelle par défaut. . . . . . . . : 192.168.1.1',
 [('   Serveur DHCP . . . . . . . . . . . . : ', 'o'), ('192.168.1.1', 'ok')],
 '   Serveurs DNS. . . . . . . . . . . . : 192.168.1.1',
], '#22c55e')

# ---------- Schéma d'architecture ----------
def box(x, y, w, h, title, lines, fill, stroke, dash=False):
    d = ' stroke-dasharray="6 4"' if dash else ''
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"{d}/>'
    s += f'<text x="{x+w/2}" y="{y+26}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="bold" fill="#1f2937">{escape(title)}</text>'
    for i, l in enumerate(lines):
        s += f'<text x="{x+w/2}" y="{y+50+i*19}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#374151">{escape(l)}</text>'
    return s

def arrow(x1, y1, x2, y2, color='#6b7280', label=None, dash=False):
    d = ' stroke-dasharray="6 4"' if dash else ''
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2.5" marker-end="url(#a)"{d}/>'
    if label:
        s += f'<text x="{(x1+x2)/2}" y="{y1-8}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#4b5563">{escape(label)}</text>'
    return s

defs = '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#6b7280"/></marker></defs>'

arch = [f'<svg xmlns="http://www.w3.org/2000/svg" width="980" height="330" viewBox="0 0 980 330" role="img" aria-label="Architecture du laboratoire">',
 '<title>Architecture du laboratoire VirtualBox</title>', defs,
 '<rect width="980" height="330" rx="12" fill="#ffffff" stroke="#d1d5db"/>',
 '<text x="490" y="30" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="bold" fill="#1f4e79">Architecture du laboratoire (PC hôte + VirtualBox)</text>',
 '<rect x="170" y="52" width="800" height="262" rx="12" fill="#f8fafc" stroke="#94a3b8" stroke-dasharray="8 5"/>',
 '<text x="186" y="74" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#64748b">VirtualBox</text>',
 box(14, 130, 130, 90, 'Internet', ['via le PC hôte', '(mode NAT)'], '#e0f2fe', '#0284c7'),
 box(250, 110, 200, 130, 'IPCop 2.1.8', ['wan-1 : 10.0.2.15  (rouge)', 'lan-1 : 192.168.1.1  (vert)', 'Routeur + pare-feu + DHCP'], '#fef3c7', '#d97706'),
 box(620, 90, 280, 100, 'Windows Server 2019', ['Serveur2019', '192.168.1.10 → 192.168.1.104 (DHCP)'], '#dcfce7', '#16a34a'),
 box(620, 215, 280, 80, 'Windows 11 (à venir)', ['poste client', 'adresse via DHCP IPCop'], '#f3f4f6', '#9ca3af', dash=True),
 arrow(144, 175, 250, 175, label='NAT'),
 arrow(450, 160, 620, 140),
 arrow(450, 200, 620, 250, dash=True),
 '<text x="535" y="128" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#4b5563">réseau interne</text>',
 '<text x="520" y="252" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#4b5563">192.168.1.0/24</text>',
 '</svg>']
open(OUT+'00-architecture.svg', 'w', encoding='utf-8').write('\n'.join(arch))

# ---------- Schéma de la cause ----------
def node(x, y, w, h, text, fill, stroke, sub=None):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    s += f'<text x="{x+w/2}" y="{y+(h/2 - (4 if sub else -5))}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="bold" fill="#1f2937">{escape(text)}</text>'
    if sub:
        s += f'<text x="{x+w/2}" y="{y+h/2+14}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#374151">{escape(sub)}</text>'
    return s

def row(y, label, states):
    # states: [ (text, sub, fill, stroke) ] for 5 nodes
    xs = [30, 215, 400, 585, 770]
    out = [f'<text x="30" y="{y-12}" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="bold" fill="#1f4e79">{escape(label)}</text>']
    for x, (t, sub, f, s) in zip(xs, states):
        out.append(node(x, y, 150, 62, t, f, s, sub))
    for i in range(4):
        out.append(f'<line x1="{xs[i]+150}" y1="{y+31}" x2="{xs[i+1]-2}" y2="{y+31}" stroke="#6b7280" stroke-width="2.5" marker-end="url(#a)"/>')
    return out

neutral = ('#f3f4f6', '#9ca3af'); bad = ('#fee2e2', '#dc2626'); good = ('#dcfce7', '#16a34a')
cause = [f'<svg xmlns="http://www.w3.org/2000/svg" width="950" height="330" viewBox="0 0 950 330" role="img" aria-label="Chemin des paquets dans IPCop, avant et après correction">',
 '<title>Chemin des paquets dans IPCop avant et après correction</title>', defs,
 '<rect width="950" height="330" rx="12" fill="#ffffff" stroke="#d1d5db"/>',
 '<text x="475" y="30" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="bold" fill="#1f4e79">Chemin d’un paquet du serveur vers internet</text>']
cause += row(90, 'Avant : les deux chaînes sont vides', [
  ('Serveur2019', '192.168.1.10', *neutral), ('lan-1', 'entrée IPCop', *neutral),
  ('FW_OUTGOING', 'vide : paquet rejeté', *bad), ('REDNAT', 'vide : pas de NAT', *bad), ('wan-1 → Internet', '', *neutral)])
cause += row(220, 'Après : règles ACCEPT et MASQUERADE', [
  ('Serveur2019', '192.168.1.10', *neutral), ('lan-1', 'entrée IPCop', *neutral),
  ('FW_OUTGOING', 'ACCEPT lan-1 → wan-1', *good), ('REDNAT', 'MASQUERADE', *good), ('wan-1 → Internet', 'réponses reçues', *good)])
cause.append('</svg>')
open(OUT+'12-chemin-des-paquets.svg', 'w', encoding='utf-8').write('\n'.join(cause))

# ---------- Maquette page DHCP ----------
dh = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="330" viewBox="0 0 760 330" role="img" aria-label="Page Services, Serveur DHCP d’IPCop">',
 '<title>IPCop – Services &gt; Serveur DHCP (section VERT)</title>',
 '<rect width="760" height="330" rx="10" fill="#e5e7eb" stroke="#9ca3af"/>',
 '<rect x="0" y="0" width="760" height="46" rx="10" fill="#1f2937"/><rect x="0" y="30" width="760" height="16" fill="#1f2937"/>',
 '<text x="20" y="29" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="bold" fill="#ffffff">IPCop  ›  Services  ›  Serveur DHCP</text>',
 '<text x="30" y="80" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#374151">Serveur DHCP :</text>',
 '<rect x="170" y="63" width="140" height="24" rx="3" fill="#16a34a"/><text x="240" y="80" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="bold" fill="#ffffff">En cours</text>',
 '<text x="30" y="118" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="bold" fill="#15803d">VERT</text>',
 '<text x="170" y="118" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#374151">Activé :</text>',
 '<rect x="240" y="104" width="16" height="16" fill="#ffffff" stroke="#374151"/><path d="M243 112l4 4 7-8" stroke="#16a34a" stroke-width="2.5" fill="none"/>']
fields = [('Adresse de départ', '192.168.1.2'), ('Adresse de fin', '192.168.1.254'), ('Durée du bail (minutes)', '60'),
          ('Suffixe de domaine', 'localdomain'), ('DNS primaire', '192.168.1.1')]
for i, (k, v) in enumerate(fields):
    y = 150 + i*30
    dh.append(f'<text x="30" y="{y+16}" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#374151">{escape(k)} :</text>')
    dh.append(f'<rect x="250" y="{y}" width="190" height="24" fill="#ffffff" stroke="#6b7280"/><text x="258" y="{y+17}" font-family="{FONT}" font-size="13" fill="#111827">{escape(v)}</text>')
dh.append('<rect x="560" y="270" width="150" height="34" rx="4" fill="#f9fafb" stroke="#6b7280"/><text x="635" y="292" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="#111827">Enregistrer</text>')
dh.append('</svg>')
open(OUT+'13-ipcop-dhcp.svg', 'w', encoding='utf-8').write('\n'.join(dh))
print(sorted(os.listdir(OUT)))
