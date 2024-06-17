from django.shortcuts import render


# Temporary
def upload_view(request):  # pragma: no cover
    """This is a temporary view to load existing data into the db."""

    from csv import reader
    from datetime import datetime
    from os import path

    from django.conf import settings
    from django.http import HttpResponse

    from apps.channels.models import Channel
    from apps.hosts.models import Host
    from apps.shows.models import Show
    from apps.videos.models import Video

    ch_prime, c = Channel.objects.get_or_create(name="Kinda Funny")
    ch_games, c = Channel.objects.get_or_create(name="Kinda Funny Games")
    ch_members, c = Channel.objects.get_or_create(
        name="Kinda Funny Membership"
    )

    CHANNELS = {
        "prime": ch_prime,
        "games": ch_games,
        "patreon": ch_members,
    }

    SHOWS = {
        "KFGD": "Kinda Funny Games Daily",
        "PSILY": "PS I Love You XOXO",
        "KFW": "Kinda Funny Wrestling",
        "GOG": "The GameOverGreggy Show",
        "Morning Show": "Kinda Funny Morning Show",
        "KF Podcast": "Kinda Funny Podcast",
        "Other": "Miscellaneous",
        "Kinda Funny Plays": "Gameplay",
        "KFFL": "Kinda Funny Football League",
    }

    KF = [
        "Greg Miller",
        "Nick Scarpino",
        "Tim Gettys",
        "Kevin Coello",
        "Andy Cortez",
        "Blessing Adeoye Jr.",
        "Mike Howard",
        "Joey Noelle",
        "Cool Greg",
        "Barrett Courtney",
        "Roger Pokorny",
    ]

    PT = [
        "Andrea Rene",
        "Danny O'Dwyer",
        "Fran Mirabella III",
        "Gary Whitta",
        "Janet Garcia",
        "Jared Petty",
        "Imran Khan",
        "Parris Lilly",
        "Tamoor Hussain",
    ]

    i = 0
    file_path = path.join(settings.BASE_DIR / "resources", "shows.csv")

    with open(file_path, "r", encoding="utf-8") as file:
        data = reader(file)
        for row in data:
            try:
                show_name = SHOWS[row[2]] if row[2] in SHOWS else row[2]
                show, c = Show.objects.get_or_create(name=show_name)
                patreon = row[1] == "patreon"
                url = row[6]
                video = Video.objects.create(
                    title=row[3],
                    release_date=datetime.fromisoformat(row[4]),
                    show=show,
                    channel=CHANNELS[row[1]] if row[1] in CHANNELS else None,
                    video_id=url[-11:] if not patreon else url.split("/")[-1],
                    link=url,
                    short=True if "/shorts/" in url else False,
                    members_only=False if not patreon else True,
                    blurb=row[8] if row[8].upper() != "NULL" else None,
                )

                host_batch, guest_batch = [], []

                for name in (
                    n
                    for n in (str(row[5]) + "," + str(row[7])).split(",")
                    if n.upper() != "NULL"
                ):
                    if not name:
                        continue
                    host, c = Host.objects.get_or_create(
                        name=name,
                        kf_crew=name in KF,
                        part_timer=name in PT,
                    )
                    if name in KF or name in PT:
                        host_batch.append(host)
                    else:
                        guest_batch.append(host)

                video.hosts.add(*host_batch)
                video.guests.add(*guest_batch)
                i += 1
            except Exception as e:
                if str(e) == (
                    "UNIQUE constraint failed: videos_video.video_id"
                ):
                    continue
                else:
                    raise e

    return HttpResponse(f"Videos added: {i}")
