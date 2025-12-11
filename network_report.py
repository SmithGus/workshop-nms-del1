import json
from datetime import datetime

def load_data(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def get_all_devices(data):
    devices = []
    for location in data.get("locations", []):
        site = location.get("site")
        city = location.get("city")
        for dev in location.get("devices", []):
            d = dev.copy()
            d["site"] = site
            d["city"] = city
            devices.append(d)
    return devices

def skriv_header(f, data):
    company = data.get("company", "Okänt företag")
    updated = data.get("last_updated", "okänt")

    f.write("------------------------------------\n")
    f.write(f"Nätverksrapport för {company}\n")
    f.write("Uppdaterad av NMS: " + updated + "\n")
    f.write("Skapad av script: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n")
    f.write("------------------------------------\n\n")

def skriv_summary(f, devices):
    offline = [d for d in devices if d.get("status") == "offline"]
    warning = [d for d in devices if d.get("status") == "warning"]
    low_uptime = [d for d in devices if d.get("uptime_days", 9999) < 30]
    high_ports = []
    for d in devices:
        if d.get("type") == "switch" and isinstance(d.get("ports"), dict):
            t = d["ports"].get("total", 0)
            u = d["ports"].get("used", 0)
            if t > 0 and u / t > 0.8:
                high_ports.append(d)

    f.write("== Sammanfattning ==\n\n")
    f.write(f"- Offline: {len(offline)}\n")
    f.write(f"- Varning: {len(warning)}\n")
    f.write(f"- Kort uptime (<30 dagar): {len(low_uptime)}\n")
    f.write(f"- Switchar med hög portanvändning: {len(high_ports)}\n\n")

    if offline:
        f.write("OBS: Det finns enheter som är offline, behöver kollas.\n")
    if high_ports:
        f.write("Flera switchar har nästan fulla portar.\n")
    if low_uptime:
        f.write("Enheter har startats om nyligen eller är ostabila.\n")
    f.write("\n")

def skriv_offline_warning(f, devices):
    f.write("Offline och varning:\n---------------------\n")
    for d in devices:
        if d.get("status") in ["offline", "warning"]:
            f.write(f"{d.get('hostname')} - {d.get('status')} - {d.get('ip_address')} - {d.get('site')}\n")
    f.write("\n")

def skriv_low_uptime(f, devices):
    f.write("Uptime under 30 dagar:\n------------------------\n")
    for d in devices:
        if d.get("uptime_days", 9999) < 30:
            f.write(f"{d['hostname']} ({d['uptime_days']} dagar) - {d['type']} - {d['site']}\n")
    f.write("\n")

def skriv_enhetstyper(f, devices):
    f.write("Enhetstyper i nätet:\n---------------------\n")
    typer = {}
    for d in devices:
        t = d.get("type", "okänd")
        typer[t] = typer.get(t, 0) + 1
    for t, count in typer.items():
        f.write(f"{t}: {count} st\n")
    f.write("\n")

def skriv_portstat(f, devices):
    f.write("Portanvändning (switchar):\n---------------------------\n")
    tot = 0
    used = 0
    for d in devices:
        if d.get("type") == "switch" and isinstance(d.get("ports"), dict):
            tot += d["ports"].get("total", 0)
            used += d["ports"].get("used", 0)

    if tot > 0:
        procent = (used / tot) * 100
        f.write(f"Totalt: {used}/{tot} portar använda ({procent:.1f}%)\n")
    else:
        f.write("Ingen portdata hittades\n")
    f.write("\n")

    f.write("Switchar med över 80% portar använda:\n")
    for d in devices:
        if d.get("type") == "switch":
            p = d.get("ports", {})
            if p and p.get("total", 0) > 0:
                percent = p["used"] / p["total"] * 100
                if percent > 80:
                    f.write(f"- {d['hostname']} ({p['used']}/{p['total']}) {percent:.1f}% - {d['site']}\n")
    f.write("\n")

def skriv_vlans(f, devices):
    f.write("VLAN-lista:\n------------\n")
    vlan_set = set()
    for d in devices:
        if isinstance(d.get("vlans"), list):
            vlan_set.update(d["vlans"])
    vlans = sorted(list(vlan_set))
    f.write(f"Antal VLANs: {len(vlans)}\n")
    f.write("VLANs: " + ", ".join(str(v) for v in vlans) + "\n\n")

def skriv_sites(f, data):
    f.write("Enhetsstatus per plats:\n------------------------\n")
    for loc in data.get("locations", []):
        site = loc.get("site", "okänd")
        city = loc.get("city", "")
        kontakt = loc.get("contact", "ingen angiven")
        devices = loc.get("devices", [])
        tot = len(devices)
        online = len([d for d in devices if d.get("status") == "online"])
        offline = len([d for d in devices if d.get("status") == "offline"])
        warning = len([d for d in devices if d.get("status") == "warning"])
        f.write(f"{site} ({city}) - Totalt: {tot}, Online: {online}, Offline: {offline}, Warning: {warning}\n")
        f.write(f"Kontaktperson: {kontakt}\n\n")

def skriv_eisenhower(f, devices):
    f.write("Att göra – enligt Eisenhower:\n=============================\n\n")

    f.write("Viktigt och Bråttom:\n")
    f.write("- Kolla enheter som är offline.\n")
    f.write("- Titta på enheter med varningsstatus.\n")
    f.write("- Se över enheter med väldigt kort uptime.\n\n")

    f.write("Viktigt men inte Bråttom:\n")
    f.write("- Planera för att hantera switchar med nästan fulla portar.\n\n")

    f.write("Inte så viktigt men Bråttom:\n")
    f.write("- Uppdatera dokumentation för VLAN.\n\n")

    f.write("Inte viktigt och inte bråttom:\n")
    f.write("- Håll koll på platser där allt funkar bra.\n\n")

def skriv_itil(f, devices):
    f.write("ITIL-koppling:\n==============\n\n")

    f.write("Incident Management:\n")
    f.write("- Offline-enheter är incidenter som måste fixas snabbt.\n\n")

    f.write("Problem Management:\n")
    f.write("- Enheter med låg uptime kan ha problem som måste undersökas.\n\n")

    f.write("Capacity Management:\n")
    f.write("- Vissa switchar är nästan fulla – kanske behövs fler portar.\n\n")

    f.write("Availability Management:\n")
    f.write("- Varningar och instabil uptime kan påverka nätets tillgänglighet.\n\n")

def main():
    data = load_data("network_devices.json")
    devices = get_all_devices(data)

    with open("network_report.txt", "w", encoding="utf-8") as f:
        skriv_header(f, data)
        f.write(f"Totalt antal enheter: {len(devices)}\n\n")
        skriv_summary(f, devices)
        skriv_offline_warning(f, devices)
        skriv_low_uptime(f, devices)
        skriv_enhetstyper(f, devices)
        skriv_portstat(f, devices)
        skriv_vlans(f, devices)
        skriv_sites(f, data)
        skriv_eisenhower(f, devices)
        skriv_itil(f, devices)

    print("✅ Rapport skapad: network_report.txt")

if __name__ == "__main__":
    main()
