"""
Download and resize STS2 card/relic images from untapped.gg CDN.
Saves to sts2/assets/ at 156×156 (2× for retina, displayed at 78px).
Run from the repo root: python sts2/download_assets.py
"""
import os
import io
import urllib.request
import urllib.error
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

BASE_CDN  = "https://sts2json.untapped.gg/art"
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
SIZE      = 156   # px (2× the 78px display size)
WORKERS   = 12

# ── Card data ────────────────────────────────────────────────────────────────
DATA = {
    "ironclad": [
        "Barricade","Brand","Break","Burning Pact","Cascade","Corruption","Crimson Mantle",
        "Dark Embrace","Demon Form","Demonic Shield","Drum of Battle","Evil Eye","Feel No Pain",
        "Fiend Fire","Flame Barrier","Howl from Beyond","Impervious","Offering","Pact's End",
        "Rupture","Second Wind","Spite","Stoke","Taunt","Tear Asunder","Thrash","Vicious","Whirlwind",
        "Ashen Strike","Blood Wall","Colossus","Dominate","Feed","Fight Me!","Forgotten Ritual",
        "Hellraiser","Inferno","Inflame","Mangle","Not Yet","Rage","Shrug It Off","Stone Armor",
        "True Grit","Uppercut","Aggression","Armaments","Battle Trance","Bludgeon","Body Slam","Bully",
        "Cinder","Conflagration","Cruelty","Dismantle","Havoc","Hemokinesis","Iron Wave","One-Two Punch",
        "Primal Force","Setup Strike","Sword Boomerang","Tank","Twin Strike","Bloodletting","Breakthrough",
        "Expect a Fight","Infernal Blade","Juggernaut","Juggling","Molten Fist","Pillage","Pommel Strike",
        "Pyre","Rampage","Stomp","Thunderclap","Tremble","Unmovable","Unrelenting",
        "Anger","Bash","Defend","Headbutt","Perfected Strike","Stampede","Strike",
    ],
    "silent": [
        "Abrasive","Acrobatics","Bullet Time","Calculated Gamble","Corrosive Wave","Hand Trick","Haze",
        "Leg Sweep","Malaise","Murder","Nightmare","Reflex","Shadow Step","Skewer","Sneaky","Storm of Steel",
        "Suppress","Tactician","Tools of the Trade","Adrenaline","Afterimage","Assassinate","Blur",
        "Bouncing Flask","Bubble Bubble","Dagger Throw","Dash","Envenom","Escape Plan","Grand Finale",
        "Hidden Daggers","Master Planner","Memento Mori","Mirage","Noxious Fumes","Outbreak","Prepared",
        "Ricochet","Serpent Form","Snakebite","Untouchable","Wraith Form","Accelerant","Backflip",
        "Blade of Ink","Burst","Deadly Poison","Echoing Slash","Expose","Flick-Flack","Follow Through",
        "Footwork","Knife Trap","Phantom Blades","Poisoned Stab","Predator","Shadowmeld","Speedster",
        "Survivor","The Hunt","Well-Laid Plans","Accuracy","Anticipate","Backstab","Cloak and Dagger",
        "Dagger Spray","Deflect","Dodge and Roll","Expertise","Fan of Knives","Finisher","Flanking",
        "Flechettes","Infinite Blades","Pinpoint","Pounce","Precise Cut","Strangle","Sucker Punch",
        "Tracking","Up My Sleeve","Blade Dance","Defend","Leading Strike","Neutralize","Piercing Wail",
        "Slice","Strike",
    ],
    "defect": [
        "Biased Cognition","Bulk Up","Consuming Shadow","Coolant","Defragment","Echo Form","Fight Through",
        "Flak Cannon","Fusion","Glacier","Hyperbeam","Ice Lance","Ignition","Meteor Strike","Modded",
        "Multi-Cast","Null","Overclock","Quadcast","Rainbow","Refract","Shadow Shield","Shatter","Voltaic",
        "Boost Away","Boot Sequence","Capacitor","Chill","Compile Driver","Coolheaded","Creative AI",
        "Darkness","Genetic Algorithm","Iteration","Lightning Rod","Machine Learning","Reboot","Rocket Punch",
        "Scrape","Storm","Sunder","Synchronize","Tempest","Thunder","Trash to Treasure","Adaptive Strike",
        "All for One","Ball Lightning","Barrage","Cold Snap","Compact","Focused Strike","FTL","Glasswork",
        "Helix Drill","Hotfix","Scavenge","Signal Boost","Skim","Smokestack","Spinner","Supercritical","TURBO",
        "Beam Cell","Buffer","Chaos","Charge Battery","Double Energy","Dualcast","Energy Surge",
        "Go for the Eyes","Gunk Up","Hailstorm","Hologram","Leap","Loop","Subroutine","Sweeping Beam",
        "Synthesis","Tesla Coil","Uproar","White Noise","Zap","Claw","Defend","Feral","Momentum Strike","Strike",
    ],
    "regent": [
        "The Sealed Throne","Big Bang","Reflect","Void Form","Meteor Shower","Bulwark","GUARDS!!!",
        "Child of the Stars","Particle Wall","Tyranny","CHARGE!!","Comet","Astral Pulse","Pillar of Creation",
        "Arsenal","Gamma Blast","Royal Gamble","Orbit","Spectrum Shift","Glow","Crash Landing","Convergence",
        "Make It So","The Smith","Decisions, Decisions","Bombardment","Hidden Cache","Gather Light",
        "Dying Star","Manifest Authority","Cloak of Stars","BEGONE!","Summon Forth","Genesis","Sword Sage",
        "Quasar","Know Thy Place","Stardust","Collision Course","Cosmic Indifference","Seeking Edge",
        "Glitterstream","Bundle of Joy","Supermassive","Foregone Conclusion","Radiate","Parry","Black Hole",
        "Patter","Seven Stars","Heavenly Drill","Kingly Kick","I Am Invincible","Alignment","Glimmer",
        "Guiding Star","Royalties","Crush Under","Pale Blue Dot","Refine Blade","Spoils of Battle","Largesse",
        "Photon Cut","Furnace","Kingly Punch","Shining Strike","Devastate","Beat into Shape","Hammer Time",
        "Conqueror","Wrought in War","Hegemony","Solar Strike","Neutron Aegis","Celestial Might","Crescent Spear",
        "Heirloom Hammer","Terraforming","Knockout Blow","Monologue","Lunar Blast","Monarch's Gaze",
        "Prophesize","Resonance",
    ],
    "necrobinder": [
        "Bone Shards","Capture Spirit","Cleanse","Demesne","Devour Life","Dirge","Eidolon","Eradicate",
        "Fetch","Glimpse Beyond","Melancholy","Necro Mastery","Protector","Rattle","Reanimate","Sacrifice",
        "Seance","Severance","Spirit of Ash","Spur","Squeeze","Banshee's Cry","Calcify","Delay","End of Days",
        "Grave Warden","High Five","Legion of Bone","Neurosurge","Pagestorm","Parse","Pull Aggro","Putrefy",
        "Reave","Right Hand Hand","Sic 'Em","Snap","Soul Storm","Undeath","Afterlife","Bury","Call of the Void",
        "Danse Macabre","Death's Door","Debilitate","Defy","Enfeebling Touch","Fear","Flatten",
        "Forbidden Grimoire","Hang","Invoke","Lethality","Misery","Oblivion","Poke","Pull from Below","Reap",
        "Reaper Form","Sculpting Strike","Shared Fate","Shroud","The Scythe","Time's Up","Transfigure",
        "Bodyguard","Borrowed Time","Countdown","Death March","Deathbringer","Defile","Dredge","Friendship",
        "Haunt","Negative Pulse","No Escape","Scourge","Sentry Mode","Sow","Unleash","Veilpiercer",
        "Blight Strike","Defend","Drain Power","Graveblast","Sleight of Flesh","Strike","Wisp",
    ],
    "colorless": [
        "Hidden Gem","Gold Axe","Fisticuffs","Salvo","Panache","Master of Strategy","Scrawl",
        "Dark Shackles","Secret Technique","Shockwave","Hand of Greed","Finesse","Discovery","Secret Weapon",
        "Thinking Ahead","Jackpot","Flash of Steel","Omnislice","Splash","Alchemize","Stratagem","Production",
        "Catastrophe","Prolong","Automation","Prep Time","Prowess","Mayhem","Panic Button","The Bomb",
        "Equilibrium","Purity","Seeker Strike","Dramatic Entrance","Rolling Boulder","Mimic","Calamity",
        "Mind Blast","Impatience","Jack of All Trades","Beat Down","Bolas","Rend","Entropy","Coordinate",
        "Huddle Up","Intercept","Knockdown","Lift","Rally","Tag Team","The Gambit","Nostalgia",
        "Fasten","Anointed","Beacon of Hope","Believe in You","Eternal Armor","Gang Up","Restlessness",
    ],
}

RELICS = [
    "Anchor","Bag of Preparation","Funerary Mask","Gambling Chip","Ghost Seed","Gorget","History Course",
    "Horn Cleat","Ice Cream","Lizard Tail","Mango","Mercury Hourglass","Molten Egg","Mr. Struggles",
    "Razor Tooth","Red Mask","Toxic Egg","Tuning Fork","Amethyst Aubergine","Art of War","Bellows",
    "Big Hat","Byrdpip","Captain's Wheel","Charon's Ashes","Festive Popper","Fragrant Mushroom",
    "Frozen Egg","Gremlin Horn","Happy Flower","Lantern","Lava Lamp","Lee's Waffle","Lost Wisp",
    "Lunar Pastry","Maw Bank","Meal Ticket","Meat on the Bone","Membership Card","Mummified Hand",
    "Pantograph","Pear","Pen Nib","Pocketwatch","Prayer Wheel","Shovel","Stone Calendar","Stone Cracker",
    "Sturdy Clamp","The Chosen Cheese","Tungsten Rod","Unsettling Lamp","Vajra","Vambrace",
    "Venerable Tea Set","War Paint","Whetstone","White Star","Wongo's Mystery Ticket","Akabeko",
    "Bag of Marbles","Blood Vial","Bone Tea","Bowler Hat","Bread","Bronze Scales","Candelabra",
    "Centennial Puzzle","Chandelier","Cloak Clasp","Data Disk","Demon Tongue","Dolly's Mirror",
    "Dragon Fruit","Dream Catcher","Ember Tea","Eternal Feather","Fresnel Lens","Game Piece","Girya",
    "Hand Drill","Kunai","Kusarigama","Lasting Candy","Letter Opener","Lucky Fysh","Miniature Tent",
    "Ninja Scroll","Nunchaku","Oddly Smooth Stone","Old Coin","Orichalcum","Ornamental Fan","Orrery",
    "Paper Krane","Pendulum","Petrified Toad","Pollinous Core","Regal Pillow","Ringing Triangle",
    "Runic Capacitor","Shuriken","Sling of Courage","Sparkling Rouge","Strawberry","Sword of Stone",
    "The Abacus","The Boot","The Courier","Tough Bandages","Vexing Puzzlebox","White Beast Statue",
    "Wing Charm","Beating Remnant","Belt Buckle","Big Mushroom","Bone Flute","Bookmark","Brimstone",
    "Burning Sticks","Cauldron","Chemical X","Darkstone Periapt","Daughter of the Wind","Dingy Rug",
    "Emotion Chip","Fencing Manual","Forgotten Soul","Galactic Dust","Gnarled Hammer","Gold-Plated Cables",
    "Helical Dart","Ivory Tile","Joss Paper","Juzu Bracelet","Kifuda","Metronome","Miniature Cannon",
    "Mini Regent","Mystic Lighter","Paper Phrog","Permafrost","Planisphere","Potion Belt","Power Cell",
    "Punch Dagger","Rainbow Ring","Red Skull","Reptile Trinket","Ripple Basin","Royal Stamp",
    "Ruined Helmet","Self-Forming Clay","Snecko Skull","Strike Dummy","Tingsha","Tiny Mailbox",
    "Vitruvian Minion","Bing Bong","Book of Five Rings","Book Repair Knife","Intimidating Helmet",
    "Parrying Shield","Regalite","Royal Poison","Screaming Flagon",
]

# ── Helpers ──────────────────────────────────────────────────────────────────
def slugify(name):
    s = name.lower()
    s = s.replace('-', '_')                  # hyphens → underscores
    s = re.sub(r'[^a-z0-9_\s]', '', s)      # strip remaining specials
    s = re.sub(r'\s+', '_', s.strip())       # spaces → underscores
    s = re.sub(r'_+', '_', s)               # collapse double underscores
    return s

def cdn_url(char, name):
    slug = slugify(name)
    if char == "relics":
        return f"{BASE_CDN}/relics/{slug}.png"
    return f"{BASE_CDN}/card_portraits/{char}/{slug}.png"

def local_path(char, name):
    slug = slugify(name)
    if char == "relics":
        return os.path.join(ASSET_DIR, "relics", f"{slug}.png")
    return os.path.join(ASSET_DIR, "card_portraits", char, f"{slug}.png")

def download_and_resize(char, name):
    dest = local_path(char, name)
    if os.path.exists(dest):
        return (name, "skip")
    url = cdn_url(char, name)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        img = Image.open(io.BytesIO(data)).convert("RGBA")
        # Center-crop to square
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top  = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize((SIZE, SIZE), Image.LANCZOS)
        # Save as PNG (convert RGBA→RGB for smaller file if no transparency)
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (17, 17, 26))  # match --bg-card
            bg.paste(img, mask=img.split()[3])
            img = bg
        img.save(dest, "PNG", optimize=True)
        return (name, "ok")
    except Exception as e:
        return (name, f"err: {e}")

# ── Build job list ────────────────────────────────────────────────────────────
jobs = []
for char, names in DATA.items():
    for name in names:
        jobs.append((char, name))
for name in RELICS:
    jobs.append(("relics", name))

total = len(jobs)
print(f"Downloading {total} images with {WORKERS} workers...")

done = skipped = errors = 0
with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    futures = {pool.submit(download_and_resize, char, name): (char, name) for char, name in jobs}
    for i, fut in enumerate(as_completed(futures), 1):
        name, status = fut.result()
        if status == "ok":      done += 1
        elif status == "skip":  skipped += 1
        else:                   errors += 1; print(f"  FAIL {name}: {status}")
        if i % 50 == 0 or i == total:
            print(f"  {i}/{total}  done={done} skip={skipped} err={errors}")

print(f"\nFinished. {done} downloaded, {skipped} skipped, {errors} errors.")
