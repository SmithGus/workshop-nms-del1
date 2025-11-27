# Network Report

Detta projekt innehåller ett Python-script som läser nätverksdata från `network_devices.json` och skapar en rapport i `network_report.txt`.

## Funktioner

Scriptet gör följande:

- Läser in alla enheter från JSON-filen  
- Sammanställer en Executive Summary  
- Skapar en Eisenhower-matris över prioriterade åtgärder  
- Kopplar nätverksstatus till ITIL-processer  
- Visar offline- och varningsenheter  
- Identifierar enheter med låg uptime  
- Räknar antal enheter per typ  
- Analyserar portanvändning för switchar  
- Listar switchar med >80% belastning  
- Samlar alla VLAN  
- Skapar en översikt per site  

## Körning

python network_report.py

Rapporten genereras automatiskt som: network_report.txt