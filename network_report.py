import json
from datetime import datetime


# =========================
# Inläsning av data
# =========================
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


# =========================
# Rapportdelar
# =========================
def skriv_header(f, data):
    company = data.get("company", "Okänt företag")
    updated = data.get("last_updated", "okänt")

    f.write("------------------------------------\n")
    f.write(f"Nätverksrapport för {company}\n")
    f.write(f"Uppdaterad av NMS: {updated}\n")
    f.write("Skapad av script: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n")
    f.write("------------------------------------\n\n")


def skriv_summary(f, devices):
    offline = [d for d in devices if d.get("status") == "offline"]
    warning = [d for d in devices if d.get("status") == "warning"]
    low_uptime = [d for d in devices if d.get("uptime_days", 9999) < 30]

    high_ports = []
    for d in devices:
        if d.get("type") == "switch" and isinstance(d.get("ports"), dict):
            total = d["ports"].get("total", 0)
            used = d["ports"].get("used", 0)
            if total > 0 and used / total > 0.8:
                high_ports.append(d)

    f.write("Sammanfattning\n")
    f.write("--------------------\n\n")
    f.write(f"- Offline-enheter: {len(offline)}\n")
    f.write(f"- Enheter med varning: {len(warning)}\n")
    f.write(f"- Enheter med kort uptime (<30 dagar): {len(low_uptime)}\n")
    f.write(f"- Switchar med hög portanvändning: {len(high_ports)}\n\n")

    if offline:
        f.write("Det finns enheter som är offline och bör följas upp.\n")
    if high_ports:
        f.write("Flera switchar har hög portbelastning.\n")
    if low_uptime:
        f.write("Vissa enheter har startats om nyligen eller uppvisar instabilitet.\n")
    f.write("\n")


def skriv_offline_warning(f, devices):
    f.write("Offline och varning\n")
    f.write("---------------------\n")
    for d in devices:
        if d.get("status") in ["offline", "warning"]:
            f.write(
                f"{d.get('hostname')} – {d.get('status')} – "
                f"{d.get('ip_address')} – {d.get('site')}\n"
            )
    f.write("\n")


def skriv_low_uptime(f, devices):
    f.write("Uptime under 30 dagar\n")
    f.write("----------------------\n")
    for d in devices:
        if d.get("uptime_days", 9999) < 30:
            f.write(
                f"{d['hostname']} ({d['uptime_days']} dagar) – "
                f"{d['type']} – {d['site']}\n"
            )
    f.write("\n")


def skriv_enhetstyper(f, devices):
    f.write("Enhetstyper i nätverket\n")
    f.write("-----------------------\n")
    typer = {}
    for d in devices:
        t = d.get("type", "okänd")
        typer[t] = typer.get(t, 0) + 1

    for t, count in typer.items():
        f.write(f"{t}: {count} st\n")
    f.write("\n")


def skriv_portstat(f, devices):
    f.write("Portanvändning (switchar)\n")
    f.write("---------------------------\n")

    total_ports = 0
    used_ports = 0

    for d in devices:
        if d.get("type") == "switch" and isinstance(d.get("ports"), dict):
            total_ports += d["ports"].get("total", 0)
            used_ports += d["ports"].get("used", 0)

    if total_ports > 0:
        percent = (used_ports / total_ports) * 100
        f.write(
            f"Totalt använda portar: {used_ports}/{total_ports} "
            f"({percent:.1f}%)\n\n"
        )
    else:
        f.write("Ingen portdata tillgänglig\n\n")

    f.write("Switchar med över 80 % portanvändning:\n")
    for d in devices:
        if d.get("type") == "switch":
            ports = d.get("ports", {})
            if ports.get("total", 0) > 0:
                percent = ports["used"] / ports["total"] * 100
                if percent > 80:
                    f.write(
                        f"- {d['hostname']} "
                        f"({ports['used']}/{ports['total']}) "
                        f"{percent:.1f}% – {d['site']}\n"
                    )
    f.write("\n")


def skriv_vlans(f, devices):
    f.write("VLAN-översikt\n")
    f.write("-------------\n")
    vlan_set = set()

    for d in devices:
        if isinstance(d.get("vlans"), list):
            vlan_set.update(d["vlans"])

    vlans = sorted(vlan_set)
    f.write(f"Antal VLAN: {len(vlans)}\n")
    f.write("VLAN: " + ", ".join(str(v) for v in vlans) + "\n\n")


def skriv_sites(f, data):
    f.write("Enhetsstatus per plats\n")
    f.write("------------------------\n")

    for loc in data.get("locations", []):
        site = loc.get("site", "okänd")
        city = loc.get("city", "")
        contact = loc.get("contact", "ingen angiven")
        devices = loc.get("devices", [])

        total = len(devices)
        online = len([d for d in devices if d.get("status") == "online"])
        offline = len([d for d in devices if d.get("status") == "offline"])
        warning = len([d for d in devices if d.get("status") == "warning"])

        f.write(
            f"{site} ({city}) – Totalt: {total}, "
            f"Online: {online}, Offline: {offline}, Warning: {warning}\n"
        )
        f.write(f"Kontaktperson: {contact}\n\n")


def skriv_eisenhower(f):
    f.write("Att göra – enligt Eisenhower\n")
    f.write("-----------------------------\n\n")

    f.write("Viktigt och bråttom:\n")
    f.write("- Följa upp offline-enheter\n")
    f.write("- Hantera enheter med varningsstatus\n")
    f.write("- Kontrollera enheter med mycket kort uptime\n\n")

    f.write("Viktigt men inte bråttom:\n")
    f.write("- Planera kapacitet för switchar med hög portbelastning\n\n")

    f.write("Inte bråttom:\n")
    f.write("- Fortsatt uppföljning av stabila platser\n\n")


def skriv_itil(f):
    f.write("ITIL-koppling\n")
    f.write("-------------\n\n")

    f.write("Incident Management:\n")
    f.write("- Offline- och varningsenheter hanteras som incidenter\n\n")

    f.write("Problem Management:\n")
    f.write("- Upprepade omstarter och låg uptime bör analyseras vidare\n\n")

    f.write("Capacity Management:\n")
    f.write("- Hög portanvändning indikerar framtida kapacitetsbehov\n\n")

    f.write("Availability Management:\n")
    f.write("- Stabil uptime och få varningar bidrar till hög tillgänglighet\n\n")


# =========================
# MAIN
# =========================
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
        skriv_eisenhower(f)
        skriv_itil(f)

    print("Rapport skapad: network_report.txt")


if __name__ == "__main__":
    main()
