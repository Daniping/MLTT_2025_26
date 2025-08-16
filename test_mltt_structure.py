if date_text and time_text:
        datetime_str = f"{date_text.get_text(strip=True)} {time_text.get_text(strip=True)}"
        # On suppose que l'heure sur le site est en Californie
        start_dt = datetime.strptime(datetime_str, "%b %d, %Y %I:%M %p").replace(tzinfo=ZoneInfo("America/Los_Angeles"))
        start_dt = start_dt.astimezone(tz_paris)
else:
        continue

    lieu = location.get_text(strip=True) if location else "Lieu inconnu"

    event = Event()
    event.add("summary", "MLTT Match")
    event.add("dtstart", start_dt)
    event.add("dtend", start_dt + timedelta(hours=2))
    event.add("location", lieu)
    cal.add_component(event)

# Création du dossier et écriture du fichier ICS
os.makedirs("MLTT_2025_26_V5", exist_ok=True)
ics_filename = "MLTT_2025_26_V5/MLTT_2025_26_V5.ics"
with open(ics_filename, "wb") as f:
    f.write(cal.to_ical())

print(f"✅ Fichier ICS généré : {ics_filename}")
