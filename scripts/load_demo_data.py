"""Demo data loader for Dragon Watch Taiwan Strait escalation scenario.

Generates and loads 72-hour escalation scenario into Supabase:
- GREEN (Hours 0-24): Normal diplomatic coverage
- AMBER (Hours 24-48): Coordinated sovereignty messaging
- RED (Hours 48-72): Military readiness posturing

Run directly: python scripts/load_demo_data.py
"""

import asyncio
import random
from datetime import datetime, timedelta

from src.database.client import get_supabase
from src.models.schemas import ArticleCreate, SocialPostCreate, VesselPositionCreate

# Base timestamp for scenario
BASE_TIME = datetime(2026, 2, 5, 0, 0, 0)

# Chinese state media domains
DOMAINS = ["xinhuanet.com", "globaltimes.cn", "people.com.cn", "cctv.com"]

# OSINT Telegram channels
CHANNELS = [
    "@OSINTtechnical",
    "@IntelDoge",
    "@militarymap",
    "@ChinaOSINT",
    "@TaiwanWatch",
]


def generate_demo_articles(base_time: datetime, count: int = 60) -> list[dict]:
    """Generate articles showing narrative escalation over 72 hours.

    GREEN (0-24h): Normal coverage, tone 0 to -2
    AMBER (24-48h): Sovereignty messaging, tone -3 to -6
    RED (48-72h): Military readiness, tone -5 to -10
    """
    articles = []

    # GREEN PHASE articles (0-24 hours)
    green_titles = [
        ("China, ASEAN nations hold routine maritime cooperation meeting", -0.5),
        ("Taiwan tourism sector reports strong mainland visitor growth", 1.2),
        ("Cross-strait cultural exchange program concludes in Xiamen", 0.8),
        ("Foreign Ministry: China committed to peaceful development", 0.3),
        ("Fujian province expands trade ties with Southeast Asia", -0.2),
        ("Cross-strait family reunion events planned for Spring Festival", 1.5),
        ("Taiwan scholars visit Beijing for academic symposium", 0.6),
        ("Economic cooperation across strait benefits both sides: expert", 0.9),
        ("Chinese coast guard conducts routine patrol in East China Sea", -1.2),
        ("Taiwan agricultural products popular in mainland markets", 1.1),
        ("Cross-strait aviation routes see increased capacity", 0.4),
        ("One China principle is foundation of peace: spokesperson", -0.8),
        ("China welcomes continued economic exchanges with Taiwan", 0.7),
        ("Cross-strait youth exchange program launches new initiatives", 1.0),
        ("Taiwan business leaders meet mainland counterparts in Shanghai", 0.5),
        ("Peaceful dialogue only way forward for cross-strait relations", 0.2),
        ("Fujian improves ferry services to Taiwanese-administered islands", 0.9),
        ("Cross-strait trade volume reaches new high in January", 1.3),
        ("Taiwan students studying in mainland exceed 10,000", 0.8),
        ("China reiterates commitment to peaceful reunification", 0.1),
    ]

    for idx, (title, tone) in enumerate(green_titles):
        domain = DOMAINS[idx % len(DOMAINS)]
        hours_offset = idx * 1.2  # Spread over 24 hours

        url = _generate_url(domain, idx + 1)
        published_at = base_time + timedelta(hours=hours_offset)

        articles.append({
            "url": url,
            "title": title,
            "domain": domain,
            "published_at": published_at,
            "tone_score": tone,
            "language": "en",
            "source_country": "CN",
        })

    # AMBER PHASE articles (24-48 hours)
    amber_titles = [
        ("Taiwan reunification is historical inevitability: white paper", -4.2),
        ("Separatist forces will not succeed in dividing China: expert", -5.1),
        ("National sovereignty and territorial integrity non-negotiable", -4.8),
        ("One China principle wins overwhelming international support", -3.5),
        ("Reunification serves fundamental interests of Chinese nation", -4.6),
        ("Taiwan question is purely China's internal affair: spokesperson", -5.3),
        ("Foreign interference will not obstruct reunification process", -5.8),
        ("Historical facts prove Taiwan is inalienable part of China", -4.1),
        ("Chinese people's resolve to achieve reunification unshakeable", -5.5),
        ("Separatist activities threaten peace and stability in region", -6.2),
        ("Reunification by peaceful means is preferred but not sole option", -5.9),
        ("Taiwan independence means war, compatriots warned", -6.4),
        ("National unity is sacred duty of every Chinese citizen", -4.4),
        ("Separatist politicians will be held accountable for actions", -5.6),
        ("Taiwan independence attempts doomed to fail: commentary", -5.2),
        ("China has full confidence in achieving complete reunification", -3.9),
        ("External forces playing with fire on Taiwan question", -6.1),
        ("Separatism runs counter to interests of Taiwan compatriots", -4.7),
        ("Reunification timeline accelerating as separatists provoke", -5.9),
        ("Chinese military will not tolerate continued provocations", -6.3),
    ]

    for idx, (title, tone) in enumerate(amber_titles):
        domain = DOMAINS[idx % len(DOMAINS)]
        hours_offset = 24 + (idx * 1.2)  # 24-48 hours

        url = _generate_url(domain, idx + 100)
        published_at = base_time + timedelta(hours=hours_offset)

        articles.append({
            "url": url,
            "title": title,
            "domain": domain,
            "published_at": published_at,
            "tone_score": tone,
            "language": "en",
            "source_country": "CN",
        })

    # RED PHASE articles (48-72 hours)
    red_titles = [
        ("PLA Eastern Theater Command announces live-fire exercises", -7.2),
        ("Military drills demonstrate resolve to safeguard sovereignty", -8.1),
        ("Armed forces at high combat readiness to counter separatism", -8.5),
        ("Joint military operations commence in Taiwan Strait region", -9.0),
        ("Navy, air force units conduct coordinated strike drills", -8.7),
        ("Rocket Force on standby as exercises escalate around Taiwan", -9.3),
        ("Military declares no-sail zones in six areas surrounding island", -9.5),
        ("Combat aircraft patrol airspace, simulating blockade operations", -9.8),
        ("Amphibious assault units mobilized to coastal staging areas", -10.0),
        ("PLA demonstrates capability to seize control of island by force", -9.7),
        ("Electronic warfare systems activated to blind enemy defenses", -9.2),
        ("Military spokesperson: Forces prepared for decisive action", -10.0),
        ("Missile units assume highest alert status in Eastern Theater", -8.9),
        ("Naval blockade exercise demonstrates encirclement capability", -9.4),
        ("Paratroop divisions conduct airborne assault rehearsals", -9.1),
        ("Cyber warfare units activated to disable enemy command systems", -8.8),
        ("Military reserves called up for large-scale mobilization drill", -9.6),
        ("Satellite imagery shows military buildup along coast: analysts", -8.3),
        ("Joint command structure activated for Taiwan contingency", -9.9),
        ("Air defense forces conduct live-fire missile intercept tests", -8.6),
    ]

    for idx, (title, tone) in enumerate(red_titles):
        domain = DOMAINS[idx % len(DOMAINS)]
        hours_offset = 48 + (idx * 1.2)  # 48-72 hours

        url = _generate_url(domain, idx + 200)
        published_at = base_time + timedelta(hours=hours_offset)

        articles.append({
            "url": url,
            "title": title,
            "domain": domain,
            "published_at": published_at,
            "tone_score": tone,
            "language": "en",
            "source_country": "CN",
        })

    return articles[:count]


def generate_demo_posts(base_time: datetime, count: int = 120) -> list[dict]:
    """Generate social posts showing movement signals over 72 hours.

    GREEN (0-24h): Normal OSINT chatter
    AMBER (24-48h): Military activity mentions
    RED (48-72h): High military activity
    """
    posts = []
    telegram_id = 100001

    # GREEN PHASE posts (0-24 hours) - 40 posts
    green_texts = [
        "Routine maritime patrol observed in East China Sea. Nothing unusual.",
        "Commercial shipping volumes normal in Taiwan Strait this week.",
        "Chinese coast guard conducting standard patrol near Fujian.",
        "Cross-strait ferry services operating on regular schedule.",
        "Weather conditions favorable for shipping in strait. All clear.",
        "No significant military movements observed past 48 hours.",
        "Fishing fleet activity normal for this time of year.",
        "Commercial aviation traffic steady across strait.",
        "Port activity in Xiamen and Fuzhou showing typical patterns.",
        "Maritime safety broadcasts routine. No special notices.",
        "Quiet day in Taiwan Strait. Shipping lanes clear.",
        "No significant naval movements past 24 hours.",
        "Standard coast guard patrol observed near Matsu.",
        "Cross-strait cargo vessels on schedule. All normal.",
        "Weather forecast clear for strait transit next 72 hours.",
        "Routine military training observed inland Fujian. Nothing new.",
        "Commercial aviation traffic steady. No diversions.",
        "Port calls by PLAN vessels following typical pattern.",
        "Fishing fleets active throughout strait. Business as usual.",
        "Standard surveillance flights by both sides. Nothing abnormal.",
        "Maritime boundary patrols routine for this season.",
        "No unusual submarine activity detected this week.",
        "Cargo throughput at strait ports normal for February.",
        "Coast guard exercises announced. Routine annual training.",
        "Ferry cancellations due to weather only. No security issues.",
        "Naval port visits following published schedule.",
        "Air defense radar activity normal baseline levels.",
        "No military aircraft crossing median line past week.",
        "Shipping insurance rates unchanged. Market calm.",
        "Port agents report normal booking patterns.",
        "No unusual requests for bunker fuel supplies.",
        "Harbor pilots working regular schedules. No surge.",
        "Tugboat availability normal. No sudden demand.",
        "Maritime traffic separation schemes functioning normally.",
        "VTS reports no unusual vessel behaviors.",
        "AIS transponder compliance rates typical.",
        "Weather routing services reporting standard traffic flows.",
        "No unusual port security measures observed.",
        "Crew change operations proceeding normally.",
        "Customs clearance times within normal range.",
    ]

    for idx, text in enumerate(green_texts):
        channel = CHANNELS[idx % len(CHANNELS)]
        hours_offset = idx * 0.6  # Spread over 24 hours
        views = random.randint(1500, 4500)

        posts.append({
            "telegram_id": telegram_id,
            "channel": channel,
            "text": text,
            "timestamp": base_time + timedelta(hours=hours_offset),
            "views": views,
        })
        telegram_id += 1

    # AMBER PHASE posts (24-48 hours) - 40 posts
    amber_texts = [
        "Multiple reports of increased military convoy activity near Xiamen. Unconfirmed.",
        "Naval vessels departing Ningbo port. At least 4 destroyers observed.",
        "Fujian MR units conducting exercises. Official announcement pending.",
        "Commercial flights avoiding certain airspace east of Fuzhou. Investigating.",
        "Local sources report military transport aircraft activity increased.",
        "Satellite imagery shows naval concentration near Zhoushan. Developing.",
        "NOTAM issued for restricted airspace. Coordinates suggest Taiwan Strait focus.",
        "PLA Eastern Theater Command raising readiness levels per OSINT indicators.",
        "Multiple Type 052D destroyers now south of Wenzhou. Pattern abnormal.",
        "Fishing boats ordered to return to port in some Fujian areas. Unverified.",
        "Amphibious ships loading at Zhanjiang. Unusual activity level.",
        "Military traffic on G15 expressway significantly increased.",
        "Xiamen port showing signs of military logistics surge.",
        "Transport aircraft making multiple trips coastal-inland. Rotation?",
        "Naval aviation base at Lingshui showing increased sorties.",
        "Submarine tender departing Yulin. At least 2 SSNs likely at sea.",
        "Military communications traffic up 40% on monitored frequencies.",
        "Fuel depot deliveries to military facilities accelerated.",
        "Hospital near Fuzhou canceling leave for military medical staff.",
        "Railway cars with military vehicles spotted heading southeast.",
        "Airborne early warning aircraft maintaining sustained patrols.",
        "Military police establishing checkpoints on coastal roads.",
        "Port authorities requesting civilian vessels expedite departures.",
        "Military charter flights increasing at civilian airports.",
        "Blood bank requests from military hospitals above normal.",
        "Coastal radar sites showing increased manning.",
        "Military family housing areas implementing access restrictions.",
        "Ammunition depot convoys observed moving toward coast.",
        "Naval infantry units recalled from leave. Not exercise season.",
        "Satellite ground stations near Fujian showing unusual activity.",
        "Military cyber activity indicators elevated per public sources.",
        "Coastal defense artillery units conducting readiness checks.",
        "Military ID checks intensified at Fujian Province borders.",
        "Emergency management drills announced for coastal cities. Sudden.",
        "Civil defense shelters being inspected by authorities.",
        "Military requisition notices issued to some shipping companies.",
        "Flight training at naval aviation schools suspended. Unusual.",
        "Reservist recall notices reported in several coastal cities.",
        "Military vehicles observed entering previously inactive facilities.",
        "Secure communications testing noted by radio monitoring community.",
    ]

    for idx, text in enumerate(amber_texts):
        channel = CHANNELS[idx % len(CHANNELS)]
        hours_offset = 24 + (idx * 0.6)  # 24-48 hours
        views = random.randint(8000, 20000)

        posts.append({
            "telegram_id": telegram_id,
            "channel": channel,
            "text": text,
            "timestamp": base_time + timedelta(hours=hours_offset),
            "views": views,
        })
        telegram_id += 1

    # RED PHASE posts (48-72 hours) - 40 posts
    red_texts = [
        "BREAKING: Large-scale PLA exercise announced for Taiwan Strait. Live-fire zones declared.",
        "Multiple amphibious assault ships departing Zhanjiang. This is significant.",
        "NOTAM indicates 6 no-sail zones surrounding Taiwan. Unprecedented scale.",
        "Combat aircraft sorties increased 300% past 12 hours. J-20s confirmed airborne.",
        "All civilian shipping diverted from strait. Military traffic only.",
        "Rocket Force TELs observed moving to coastal launch positions. Very concerning.",
        "Electronic warfare jamming detected across multiple frequencies. Active operations.",
        "Naval blockade formation visible on AIS. At least 20 major combatants deployed.",
        "Amphibious landing rehearsal underway. This is not a standard exercise.",
        "All indicators suggest imminent military action. Situation extremely tense.",
        "Carrier strike group Type 003 Fujian now in strait. Full battle group.",
        "Airborne assault forces loaded. IL-76 heavy airlift concentrated at bases.",
        "Live-fire missile launches confirmed. Anti-ship and land attack missiles.",
        "Fighter sweeps establishing air superiority. CAP barriers in place.",
        "Mine countermeasure vessels clearing lanes. Pre-assault sequence.",
        "Strategic bombers H-6K conducting long-range strike missions.",
        "Special forces insertion likely underway. Fast boats departed overnight.",
        "Naval guns firing. Shore bombardment preparation phase begun.",
        "Drone swarms deployed for ISR and targeting. Massive UAS presence.",
        "Electronic warfare aircraft jamming all civilian frequencies.",
        "Amphibious assault wave 1 launched. Landing craft in water.",
        "Helicopter assault groups airborne. Vertical envelopment in progress.",
        "Beach obstacles being cleared by combat engineers under fire.",
        "Airborne drop observed. Paratroopers seizing airfield objectives.",
        "Naval air defense engaging targets. SAM launches confirmed.",
        "Logistics ships following assault force. Sustainment echelon moving.",
        "Artillery fire support from coastal positions. Heavy bombardment.",
        "Air refueling tracks established. Sustained air operations enabled.",
        "Medical evacuation helicopters active. Casualties being extracted.",
        "Electronic attack on command and control networks. Cyber warfare active.",
        "Additional amphibious wave forming. Reinforcement echelon preparing.",
        "Port seizure operations in progress. Heli-borne forces at harbors.",
        "Beachhead established. Ground forces consolidating positions.",
        "Air superiority achieved. No enemy air activity observed.",
        "Naval blockade complete. No vessels can enter or exit.",
        "Strategic infrastructure being secured. Key sites under PLA control.",
        "Long-range precision strikes continuing. Cruise missile salvos.",
        "Hospital ships arriving. Casualty receiving stations operational.",
        "ISR assets providing real-time targeting. Full battlefield awareness.",
        "Situation critical. Full-scale invasion in progress. World watches.",
    ]

    for idx, text in enumerate(red_texts):
        channel = CHANNELS[idx % len(CHANNELS)]
        hours_offset = 48 + (idx * 0.6)  # 48-72 hours
        views = random.randint(40000, 180000)

        posts.append({
            "telegram_id": telegram_id,
            "channel": channel,
            "text": text,
            "timestamp": base_time + timedelta(hours=hours_offset),
            "views": views,
        })
        telegram_id += 1

    return posts[:count]


def generate_demo_positions(base_time: datetime, count: int = 200) -> list[dict]:
    """Generate vessel positions showing pattern changes over 72 hours.

    GREEN (0-24h): Normal merchant shipping
    AMBER (24-48h): Naval vessels appearing, merchant thinning
    RED (48-72h): Clear military pattern, civilians dispersed
    """
    positions = []

    # Taiwan Strait bounding box: 23-26N, 118-122E

    # GREEN PHASE (0-24 hours) - 70 merchant positions
    for i in range(1, 71):
        mmsi = 412000000 + i  # Merchant vessel MMSI
        ship_name = _generate_merchant_name(i)

        # Random position in strait
        lat = random.uniform(23.4, 25.8)
        lon = random.uniform(118.4, 121.5)
        speed = random.uniform(10.0, 15.0)  # Normal merchant speed
        course = random.uniform(70, 110)  # Generally eastward/westward

        hours_offset = (i - 1) * 0.34  # Spread over 24 hours

        positions.append({
            "mmsi": mmsi,
            "ship_name": ship_name,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "speed": round(speed, 1),
            "course": round(course, 0),
            "timestamp": base_time + timedelta(hours=hours_offset),
        })

    # AMBER PHASE (24-48 hours) - 70 positions (30 naval + 40 merchant)
    # Naval vessels appearing
    for i in range(1, 31):
        mmsi = 412100000 + i  # Naval vessel MMSI
        ship_name = f"PLAN {random.choice(['DESTROYER', 'FRIGATE', 'CORVETTE'])} {i:03d}"

        # Concentrate near Fujian coast
        lat = random.uniform(23.5, 25.5)
        lon = random.uniform(118.5, 120.0)  # Western side
        speed = random.uniform(18.0, 24.0)  # Higher naval speed
        course = random.uniform(80, 100)

        hours_offset = 24 + ((i - 1) * 0.8)

        positions.append({
            "mmsi": mmsi,
            "ship_name": ship_name,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "speed": round(speed, 1),
            "course": round(course, 0),
            "timestamp": base_time + timedelta(hours=hours_offset),
        })

    # Merchant traffic thinning
    for i in range(71, 111):
        mmsi = 412000000 + i
        ship_name = _generate_merchant_name(i)

        # Moving toward edges of strait (leaving)
        lat = random.uniform(23.3, 26.0)
        lon = random.uniform(118.2, 121.8)
        speed = random.uniform(11.0, 14.0)
        course = random.choice([60, 70, 120, 130])  # Moving away

        hours_offset = 24 + ((i - 71) * 0.6)

        positions.append({
            "mmsi": mmsi,
            "ship_name": ship_name,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "speed": round(speed, 1),
            "course": round(course, 0),
            "timestamp": base_time + timedelta(hours=hours_offset),
        })

    # RED PHASE (48-72 hours) - 60 positions (mostly naval)
    for i in range(31, 71):
        mmsi = 412100000 + i
        ship_name = f"PLAN {random.choice(['DESTROYER', 'FRIGATE', 'CORVETTE', 'LANDING SHIP', 'SUPPORT SHIP'])} {i:03d}"

        # Concentrated in staging areas
        lat = random.uniform(24.0, 25.5)
        lon = random.uniform(118.6, 119.8)
        speed = random.uniform(15.0, 25.0)
        course = random.uniform(85, 95)  # East toward Taiwan

        hours_offset = 48 + ((i - 31) * 0.6)

        positions.append({
            "mmsi": mmsi,
            "ship_name": ship_name,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "speed": round(speed, 1),
            "course": round(course, 0),
            "timestamp": base_time + timedelta(hours=hours_offset),
        })

    return positions[:count]


def _generate_url(domain: str, idx: int) -> str:
    """Generate realistic URL for domain."""
    if domain == "xinhuanet.com":
        return f"https://www.xinhuanet.com/english/20260205/{idx:03d}.htm"
    elif domain == "globaltimes.cn":
        return f"https://www.globaltimes.cn/page/202602/123{idx:04d}.shtml"
    elif domain == "people.com.cn":
        return f"https://www.people.com.cn/en/202602/05/c_{idx:03d}.html"
    elif domain == "cctv.com":
        return f"https://english.cctv.com/2026/02/05/ARTIx{idx:03d}.shtml"
    return f"https://{domain}/article/{idx}"


def _generate_merchant_name(idx: int) -> str:
    """Generate merchant vessel name."""
    prefixes = [
        "MERCHANT", "PACIFIC", "EASTERN", "CARGO", "SILK",
        "CONTAINER", "BULK", "TANKER", "FREIGHTER", "VESSEL"
    ]
    prefix = prefixes[idx % len(prefixes)]

    # Number to word for more realistic names
    num_words = [
        "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN",
        "ELEVEN", "TWELVE", "THIRTEEN", "FOURTEEN", "FIFTEEN", "SIXTEEN", "SEVENTEEN",
        "EIGHTEEN", "NINETEEN", "TWENTY", "TWENTYONE", "TWENTYTWO", "TWENTYTHREE",
        "TWENTYFOUR", "TWENTYFIVE", "TWENTYSIX", "TWENTYSEVEN", "TWENTYEIGHT",
        "TWENTYNINE", "THIRTY", "THIRTYONE", "THIRTYTWO", "THIRTYTHREE", "THIRTYFOUR",
        "THIRTYFIVE", "THIRTYSIX", "THIRTYSEVEN", "THIRTYEIGHT", "THIRTYNINE", "FORTY"
    ]

    if idx <= len(num_words):
        return f"{prefix} {num_words[idx - 1]}"
    else:
        return f"{prefix} {idx}"


async def load_demo_data() -> dict[str, int]:
    """Load all demo data into Supabase.

    Returns:
        Dict with counts of loaded records
    """
    print("Generating demo data...")
    articles = generate_demo_articles(BASE_TIME, count=60)
    posts = generate_demo_posts(BASE_TIME, count=120)
    positions = generate_demo_positions(BASE_TIME, count=200)

    print(f"Generated {len(articles)} articles, {len(posts)} posts, {len(positions)} positions")

    # Validate through Pydantic models
    print("Validating data through Pydantic models...")
    validated_articles = [ArticleCreate(**article).model_dump() for article in articles]
    validated_posts = [SocialPostCreate(**post).model_dump() for post in posts]
    validated_positions = [VesselPositionCreate(**position).model_dump() for position in positions]

    print("Validation complete. Connecting to Supabase...")
    supabase = await get_supabase()

    # Insert articles (upsert on URL to be rerunnable)
    print("Inserting articles...")
    for article in validated_articles:
        # Convert datetime to ISO string for Supabase
        article["published_at"] = article["published_at"].isoformat()
        await supabase.table("articles").upsert(article, on_conflict="url").execute()

    # Insert social posts (plain insert)
    print("Inserting social posts...")
    for post in validated_posts:
        post["timestamp"] = post["timestamp"].isoformat()
        await supabase.table("social_posts").insert(post).execute()

    # Insert vessel positions (plain insert)
    print("Inserting vessel positions...")
    # Batch insert in chunks to avoid overwhelming Supabase
    chunk_size = 50
    for i in range(0, len(validated_positions), chunk_size):
        chunk = validated_positions[i : i + chunk_size]
        for pos in chunk:
            pos["timestamp"] = pos["timestamp"].isoformat()
        await supabase.table("vessel_positions").insert(chunk).execute()
        print(f"  Inserted positions {i+1}-{min(i+chunk_size, len(validated_positions))}")

    return {
        "articles": len(validated_articles),
        "posts": len(validated_posts),
        "positions": len(validated_positions),
    }


async def main() -> None:
    """Main entry point."""
    print("=" * 60)
    print("Dragon Watch Demo Data Loader")
    print("Taiwan Strait 72-hour Escalation Scenario")
    print("=" * 60)
    print()

    try:
        counts = await load_demo_data()

        print()
        print("=" * 60)
        print("Demo data loaded successfully!")
        print("=" * 60)
        print(f"Articles:  {counts['articles']:>3} (GREEN/AMBER/RED narrative escalation)")
        print(f"Posts:     {counts['posts']:>3} (Civilian movement signals)")
        print(f"Positions: {counts['positions']:>3} (Vessel pattern changes)")
        print()
        print("Scenario timeline:")
        print(f"  Start:  {BASE_TIME.isoformat()}")
        print(f"  GREEN:  Hours 0-24  (Normal coverage)")
        print(f"  AMBER:  Hours 24-48 (Sovereignty messaging)")
        print(f"  RED:    Hours 48-72 (Military readiness)")
        print()
        print("Demo ready for testing!")

    except Exception as e:
        print()
        print("=" * 60)
        print("ERROR loading demo data")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("Check that:")
        print("  1. Supabase credentials in .env are correct")
        print("  2. Database migrations have been run")
        print("  3. All required tables exist")
        raise


if __name__ == "__main__":
    asyncio.run(main())
