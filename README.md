# Nätverksrapport

Detta projekt innehåller ett Python-script som läser nätverksdata från filen `network_devices.json` och skapar en textbaserad rapport som sparas i `network_report.txt`.

## Vad scriptet gör

Scriptet:

- Läser in alla enheter från JSON-filen
- Sammanfattar status i en "Executive Summary"
- Visar viktiga åtgärder i en enkel Eisenhower-matris
- Kopplar rapportens resultat till ITIL-processer
- Visar enheter som är offline eller har varningar
- Hittar enheter med låg uptime (t.ex. < 30 dagar)
- Räknar antal enheter av varje typ (switch, router, etc.)
- Visar hur mycket portar används på switchar
- Listar switchar med hög portbelastning (> 80%)
- Samlar alla VLAN som används i nätverket
- Ger överblick per site (t.ex. Huvudkontor, Datacenter)

## Så kör du scriptet

Kör kommandot i terminalen:

```bash
python network_report.py
