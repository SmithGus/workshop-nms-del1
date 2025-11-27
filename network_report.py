import json


def load_data(filename):
    """Läs in JSON-datan från fil."""
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_all_devices(data):
    """
    Plocka ut alla devices från alla locations
    och lägg dem i en gemensam lista.
    """
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


def write_header(f, data):
    """Skriv ut rubrik och grundinfo i rapporten."""
    company = data.get("company", "Okänt företag")
    last_updated = data.get("last_updated", "Okänt datum")

    f.write("=" * 80 + "\n")
    f.write(f"NÄTVERKSRAPPORT - {company}\n")
    f.write("=" * 80 + "\n")
    f.write(f"Datauppdatering: {last_updated}\n\n")


def write_executive_summary(f, devices):
    """Kort översikt över läget i nätet."""
    offline = [d for d in devices if d.get("status") == "offline"]
    warning = [d for d in devices if d.get("status") == "warning"]
    low_uptime = [d for d in devices if d.get("uptime_days", 9999) < 30]

    # Hög portanvändning (switchar >80%)
    high_port_switches = []
    for d in devices:
        if d.get("type") == "switch" and isinstance(d.get("ports"), dict):
            total = d["ports"].get("total", 0)
            used = d["ports"].get("used", 0)
            if total > 0:
                usage = used / total * 100
                if usage > 80:
                    high_port_switches.append(d)

    datacenter_switches = [
        d for d in high_port_switches if d.get("site") == "Datacenter"
    ]
    hq_switches = [
        d for d in high_port_switches if d.get("site") == "Huvudkontor"
    ]

    f.write("EXECUTIVE SUMMARY\n")
    f.write("------------------\n")
    f.write(f"- Kritiskt: {len(offline)} enheter offline.\n")
    f.write(f"- Varning : {len(warning)} enheter med varningsstatus.\n")
    f.write(f"- Stabilitet: {len(low_uptime)} enheter har låg uptime (< 30 dagar).\n")
    f.write(
        f"- Kapacitet: {len(high_port_switches)} switchar har hög portanvändning (> 80%).\n\n"
    )

    f.write("Sammanfattning:\n")

    if offline:
        f.write(
            f"  Det finns {len(offline)} offline-enheter som behöver felsökas direkt,\n"
        )
        f.write("  eftersom de påverkar driften och användarnas tillgång till nätet.\n")
    else:
        f.write("  Det finns inga offline-enheter just nu.\n")

    if datacenter_switches:
        f.write(
            "  Datacentret har mycket hög belastning på flera switchar. Detta kan\n"
        )
        f.write("  leda till kapacitetsproblem framöver om inget görs.\n")

    if hq_switches:
        f.write(
            "  På huvudkontoret ligger också flera switchar högt i portanvändning.\n"
        )
        f.write("  Det kan behöva ses över för att undvika framtida flaskhalsar.\n")

    if low_uptime:
        f.write(
            "  Flera enheter har kort uptime, vilket kan betyda att de startats om\n"
        )
        f.write("  nyligen eller att det finns någon form av instabilitet.\n")

    f.write("\n")


def write_eisenhower(f, devices):
    """
    Skriv en enkel Eisenhower-matris utifrån rapportens resultat.
    Här använder vi fasta formuleringar, men baserat på samma problemtyper.
    """
    f.write("EISENHOWER-MATRIS – ÅTGÄRDSÖVERSIKT\n")
    f.write("-----------------------------------\n\n")

    f.write("Viktigt & Bråttom (Do Now)\n")
    f.write("Åtgärder som påverkar drift, tillgänglighet eller säkerhet direkt.\n")
    f.write("- Felsöka de två offline-enheterna (SW-ACCESS-03, AP-LAGER-02).\n")
    f.write(
        "- Kontrollera varningsenheterna (AP-FLOOR2-02, RT-LAGER-01, SW-DC-TOR-02).\n"
    )
    f.write(
        "- Följa upp enheter med extremt låg uptime (0–5 dagar) för att säkerställa stabilitet.\n\n"
    )

    f.write("Viktigt men Inte Bråttom (Plan)\n")
    f.write("Åtgärder som kräver planering, budget eller kapacitetsbeslut.\n")
    f.write(
        "- Utreda kapacitetsproblem i Datacenter (flera switchar >95% portanvändning).\n"
    )
    f.write("- Planera eventuell portexpansion eller omfördelning av trafik.\n")
    f.write("- Överväga bättre lastbalansering kring AP-FLOOR2-02 (45 klienter).\n\n")

    f.write("Mindre Viktigt men Bråttom (Delegate)\n")
    f.write("Kan hanteras av 1st line-support eller driftpersonal.\n")
    f.write(
        "- Följa upp enheter med 8–30 dagars uptime för att se om omstarter varit planerade.\n"
    )
    f.write("- Dubbelkolla dokumentation för VLAN-fördelning.\n\n")

    f.write("Mindre Viktigt och Inte Bråttom (Monitor)\n")
    f.write("Inget akut – håll koll men inga åtgärder behövs just nu.\n")
    f.write("- Switchar under 80% portbelastning.\n")
    f.write(
        "- Sites där alla enheter är online och stabila (t.ex. Kontor Malmö, Säkerhetskopia).\n\n"
    )


def write_itil(f):
    """Kort koppling till ITIL-processer utifrån rapportens fynd."""
    f.write("ITIL-ÖVERSIKT – KOPPLING TILL NÄTVERKSRAPPORTEN\n")
    f.write("-----------------------------------------------\n\n")

    f.write("Incident Management\n")
    f.write(
        "- Offline-enheterna (t.ex. SW-ACCESS-03, AP-LAGER-02) räknas som incidenter\n"
    )
    f.write("  eftersom de påverkar tillgänglighet och behöver åtgärdas direkt.\n\n")

    f.write("Problem Management\n")
    f.write(
        "- Enheter med låg uptime (0–5 dagar) kan tyda på underliggande problem,\n"
    )
    f.write(
        "  till exempel instabilitet eller återkommande omstarter. Dessa bör följas upp.\n\n"
    )

    f.write("Capacity Management\n")
    f.write(
        "- Switchar med mycket hög portbelastning i Datacenter (>90%) visar att\n"
    )
    f.write(
        "  kapaciteten börjar nå sin gräns och att planering för utbyggnad kan behövas.\n\n"
    )

    f.write("Availability Management\n")
    f.write(
        "- Varningsenheter och hög belastning kan påverka nätets tillgänglighet och SLA.\n"
    )
    f.write(
        "  Det är viktigt att dessa följs upp i driftmöten och övervakas över tid.\n\n"
    )



def write_problem_devices(f, devices):
    """Lista enheter som har status offline eller warning."""
    offline = [d for d in devices if d.get("status") == "offline"]
    warning = [d for d in devices if d.get("status") == "warning"]

    f.write("\nENHETER MED PROBLEM\n")
    f.write("-------------------\n")

    f.write("Status: OFFLINE\n")
    if not offline:
        f.write("  Inga enheter offline.\n")
    else:
        for d in offline:
            f.write(
                f"  {d.get('hostname', ''):15} "
                f"{d.get('ip_address', 'okänd IP'):15} "
                f"{d.get('type', 'okänd typ'):12} "
                f"{d.get('site', 'okänd site')}\n"
            )

    f.write("\nStatus: WARNING\n")
    if not warning:
        f.write("  Inga enheter med varningsstatus.\n")
    else:
        for d in warning:
            f.write(
                f"  {d.get('hostname', ''):15} "
                f"{d.get('ip_address', 'okänd IP'):15} "
                f"{d.get('type', 'okänd typ'):12} "
                f"{d.get('site', 'okänd site')}\n"
            )

    f.write("\n")




def write_low_uptime(f, devices):
    """Lista enheter som har mindre än 30 dagars uptime."""
    low = [d for d in devices if d.get("uptime_days", 9999) < 30]

    f.write("ENHETER MED LÅG UPTIME (< 30 dagar)\n")
    f.write("------------------------------------\n")

    if not low:
        f.write("  Inga enheter har låg uptime.\n\n")
        return

    for d in low:
        f.write(
            f"  {d.get('hostname', ''):15} "
            f"{str(d.get('uptime_days')):5} dagar   "
            f"{d.get('type', 'okänd typ'):12} "
            f"{d.get('site', 'okänd site')}\n"
        )
    f.write("\n")



def write_device_type_stats(f, devices):
    """Räkna hur många enheter det finns av varje typ."""
    stats = {}
    for d in devices:
        t = d.get("type", "okänd")
        stats[t] = stats.get(t, 0) + 1

    f.write("STATISTIK PER ENHETSTYP\n")
    f.write("------------------------\n")

    for t, count in stats.items():
        f.write(f"  {t.capitalize():12}: {count} st\n")

    f.write("\n")



def write_port_usage_stats(f, devices):
    """Beräkna portanvändning för switchar (totalt och per site)."""
    total_ports = 0
    used_ports = 0
    per_site = {}

    for d in devices:
        if d.get("type") != "switch":
            continue

        ports = d.get("ports")
        if not isinstance(ports, dict):
            continue

        total = ports.get("total", 0)
        used = ports.get("used", 0)

        total_ports += total
        used_ports += used

        site = d.get("site", "Okänd site")
        if site not in per_site:
            per_site[site] = {"switches": 0, "used": 0, "total": 0}
        per_site[site]["switches"] += 1
        per_site[site]["used"] += used
        per_site[site]["total"] += total

    f.write("PORTANVÄNDNING FÖR SWITCHAR\n")
    f.write("----------------------------\n")

    if total_ports == 0:
        f.write("  Inga portdata hittades för switchar.\n\n")
        return

    total_percent = used_ports / total_ports * 100
    f.write(
        f"Totalt används {used_ports} av {total_ports} portar "
        f"({total_percent:.1f}% användning).\n\n"
    )

    f.write("Per site:\n")
    for site, s in per_site.items():
        if s["total"] == 0:
            percent = 0
        else:
            percent = s["used"] / s["total"] * 100
        f.write(
            f"  {site:15} "
            f"Switchar: {s['switches']:2d}  "
            f"Portar: {s['used']}/{s['total']} ({percent:.1f}%)\n"
        )

    f.write("\n")

    f.write("SWITCHAR MED HÖG PORTANVÄNDNING (> 80%)\n")
    f.write("----------------------------------------\n")
    high_found = False
    for d in devices:
        if d.get("type") == "switch" and isinstance(d.get("ports"), dict):
            ports = d["ports"]
            total = ports.get("total", 0)
            used = ports.get("used", 0)
            if total > 0:
                percent = used / total * 100
                if percent > 80:
                    high_found = True
                    f.write(
                        f"  {d.get('hostname', ''):15} "
                        f"{used:2d}/{total:2d} portar  "
                        f"({percent:.1f}%)  "
                        f"{d.get('site', 'okänd site')}\n"
                    )
    if not high_found:
        f.write("  Inga switchar har hög portanvändning.\n")
    f.write("\n")



def write_vlan_overview(f, devices):
    """Lista alla unika VLAN i nätet."""
    vlans = set()

    for d in devices:
        dev_vlans = d.get("vlans")
        if isinstance(dev_vlans, list):
            for v in dev_vlans:
                vlans.add(v)

    f.write("VLAN-ÖVERSIKT\n")
    f.write("-------------\n")

    if not vlans:
        f.write("  Inga VLAN hittades i datan.\n\n")
        return

    sorted_vlans = sorted(vlans)
    f.write(f"Totalt antal unika VLAN: {len(sorted_vlans)}\n")
    f.write("VLANs: " + ", ".join(str(v) for v in sorted_vlans) + "\n\n")




def write_site_overview(f, data):
    """Översikt per site (antal enheter och status)."""
    f.write("STATISTIK PER SITE\n")
    f.write("------------------\n")

    for loc in data.get("locations", []):
        site = loc.get("site", "Okänd site")
        city = loc.get("city", "Okänd stad")
        contact = loc.get("contact", "Okänd kontakt")

        devices = loc.get("devices", [])
        total = len(devices)
        online = sum(1 for d in devices if d.get("status") == "online")
        offline = sum(1 for d in devices if d.get("status") == "offline")
        warning = sum(1 for d in devices if d.get("status") == "warning")

        f.write(f"{site} ({city}):\n")
        f.write(
            f"  Enheter: {total} "
            f"(online: {online}, offline: {offline}, warning: {warning})\n"
        )
        f.write(f"  Kontakt: {contact}\n\n")


def main():
    data = load_data("network_devices.json")
    devices = get_all_devices(data)

    with open("network_report.txt", "w", encoding="utf-8") as f:
        write_header(f, data)
        f.write(f"Totalt antal enheter i nätet: {len(devices)}\n\n")



        # Del A
        write_problem_devices(f, devices)
        write_low_uptime(f, devices)
        write_device_type_stats(f, devices)

        # Del B
        write_port_usage_stats(f, devices)
        write_vlan_overview(f, devices)
        write_site_overview(f, data)

        # Del C – sammanfattning + rekommendationer
        write_executive_summary(f, devices)
        write_eisenhower(f, devices)
        write_itil(f)


if __name__ == "__main__":
    main()
