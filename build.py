#!/usr/bin/env python3
"""
Static site generator for the Neatly Nash marketing site.
No Node/npm required — stitches templates/ + static/ into dist/.
Run: python3 build.py
"""
import hashlib
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path
from string import Template

ROOT = Path(__file__).parent
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
DIST = ROOT / "dist"

SITE_URL = "https://neatlynash.com"
SITE_NAME = "Neatly Nash"
PHONE_DISPLAY = "(615) 555-0148"
PHONE_TEL = "+16155550148"
EMAIL = "hello@neatlynash.com"

# Order matches the service-area line used across the site (README + mockups).
SERVICE_AREA_TOWNS = [
    "Nashville", "Franklin", "Brentwood", "Nolensville",
    "Hendersonville", "Mount Juliet", "Gallatin", "Lebanon",
]

# ---------------------------------------------------------------------------
# Town page content — extracted verbatim from
# "Neatly Nash 07 Town Pages.dc.html". Each town is genuinely different:
# different neighborhoods, different job story, different FAQ question.
# Do NOT collapse this into a single generic paragraph with the name swapped —
# that's the one thing the handoff doc explicitly warns will tank rankings.
# ---------------------------------------------------------------------------
TOWNS = [
    dict(
        slug="home-organizer-franklin-tn", name="Franklin",
        h1="Home organizing in Franklin",
        intro="I work all over Franklin, from the newer builds in Westhaven and Berry Farms to the older houses off Lewisburg Pike and around downtown. The two need opposite things. New construction here tends to have a huge pantry and almost no drop zone, so everything piles up on the kitchen island. The older homes have the closets but not the kitchen space, so the pantry has to earn every inch.",
        c1t="No travel fee", c1b="Franklin is inside my regular service area. The quote you get is the quote you pay.",
        c2t="Donations stay local", c2b="Everything goes to a Franklin drop-off the same day, and the receipt comes to you.",
        c3t="School-hours work", c3b="I start after drop-off and finish before pickup, so the house is yours again by three.",
        jobtitle="A recent Franklin project",
        jobbody="A Cool Springs family with three kids under ten and a pantry nobody could reach past the second shelf. We moved the everyday food down, gave each kid a labeled snack bin, and put the bulk backstock up high where it belongs. Afternoons stopped running through Mom.",
        faqq="What does a home organizer cost in Franklin?",
        faqa="You get one flat price for the whole job, quoted the same day as your free twenty-minute walkthrough. Bins and baskets are separate, bought at cost, and I use whatever you already own first.",
        cta="Book a Franklin walkthrough",
    ),
    dict(
        slug="home-organizer-brentwood-tn", name="Brentwood",
        h1="Home organizing in Brentwood",
        intro="Brentwood houses are big, which sounds like it should make this easier and usually makes it harder. More square footage means more places for a thing to end up, and a bonus room that quietly becomes storage. I work in Governors Club, Annandale, Sunset Hills, and the older streets near Maryland Farms, and the job here is almost always about giving things one obvious home instead of four possible ones.",
        c1t="Big houses, real plans", c1b="Whole-home work here runs in phases so you're never living in a construction zone.",
        c2t="Discreet and insured", c2b="One person, in and out, no crew in your house and nothing photographed without your okay.",
        c3t="Twenty-five minutes away", c3b="Close enough that a follow-up visit is easy, which is when most of this actually gets fine-tuned.",
        jobtitle="A recent Brentwood project",
        jobbody="A bonus room off the garage that had become the place everything went to be dealt with later. Two days, four categories, one carload of donations, and the family got a working playroom back out of it.",
        faqq="Do you do whole-home organizing in Brentwood?",
        faqa="Yes, and in a house this size I recommend it in phases over four to six weeks rather than all at once. We start with the rooms your weekday actually touches and work outward, so the house stays livable the entire time.",
        cta="Book a Brentwood walkthrough",
    ),
    dict(
        slug="home-organizer-nolensville-tn", name="Nolensville",
        h1="Home organizing in Nolensville",
        intro="Nolensville is mostly young families in newer neighborhoods like Bent Creek, Silver Stream Farm, and Burkitt Place, and the houses have a very particular problem. The builder pantry is a deep rectangle with wire shelving and no zones, and the mudroom is a bench with three hooks for a family of five. Both are fixable in a day, and both give back more morning time than anything else in the house.",
        c1t="Builder pantry fixes", c1b="The deep wire-shelf pantry in most of these homes is the single most common job I do out here.",
        c2t="Growing families", c2b="Set up to survive a kid moving up a size, a sport starting, and a baby arriving.",
        c3t="Twenty minutes away", c3b="Nolensville is a short drive from me, so scheduling is flexible and follow-ups are easy.",
        jobtitle="A recent Nolensville project",
        jobbody="A Bent Creek family with two kids in fall sports and a mudroom bench you couldn't sit on. One labeled bin per kid, a hook at their height instead of Mom's, and a basket by the door for whatever has to go back to school tomorrow.",
        faqq="How long does a pantry take in Nolensville?",
        faqa="One day for almost every pantry in these neighborhoods, because the layouts repeat. I've done enough of the same builder floorplans out here to know where things want to go before I walk in.",
        cta="Book a Nolensville walkthrough",
    ),
    dict(
        slug="home-organizer-mount-juliet-tn", name="Mount Juliet",
        h1="Home organizing in Mount Juliet",
        intro="This is home. I live here, my kids go to school here, and I know the difference between organizing a house in Providence, in Nichols Vale, and in one of the older places off Lebanon Road. Being ten minutes away changes what I can offer: I can come back, I can drop off labels, and I can take the donation tote when it fills up again.",
        c1t="I live here", c1b="Mount Juliet is my home town, not a service area I drive to.",
        c2t="Easy follow-ups", c2b="Ten minutes away means I can swing back when something stops working, not schedule it for next month.",
        c3t="Donation pickups", c3b="When your tote fills up again, text me. I'll come get it.",
        jobtitle="A recent Mount Juliet project",
        jobbody="A Providence kitchen where the lunch supplies lived in four different cabinets. Everything for breakfast and lunch moved to one shelf by the fridge, at a height the nine-year-old could reach. She packs her own now, most mornings.",
        faqq="Are you local to Mount Juliet?",
        faqa="Yes, I live here. Neatly Nash is based in Mount Juliet, so there's no travel charge, scheduling is flexible, and coming back for a follow-up is a ten-minute drive instead of a project.",
        cta="Book a Mount Juliet walkthrough",
    ),
    dict(
        slug="home-organizer-hendersonville-tn", name="Hendersonville",
        h1="Home organizing in Hendersonville",
        intro="Hendersonville comes with lake gear. Houses around Old Hickory Lake, Indian Lake, and Sanders Ferry have life jackets, towels, coolers, and folding chairs that need somewhere to live for eight months of the year and somewhere reachable for four. That seasonal swing is the whole job out here, and it's the reason a quarterly reset makes more sense in this town than most.",
        c1t="Lake gear storage", c1b="A real place for the life jackets, coolers, and towels, in season and out.",
        c2t="Seasonal swaps", c2b="The quarterly tune-up exists for houses like these, where half the stuff changes twice a year.",
        c3t="Garages included", c3b="Most Hendersonville jobs start in the garage, which is where the lake things actually live.",
        jobtitle="A recent Hendersonville project",
        jobbody="A garage near Sanders Ferry where the boat gear and the Christmas bins had merged into one pile. We split it into in-season and out-of-season, put the out-of-season up on a shelf, and gave every kid's life jacket a labeled hook they could reach themselves.",
        faqq="Do you organize garages in Hendersonville?",
        faqa="Yes, and out here the garage is usually where I'd start. Lake and seasonal gear is what fills a Hendersonville house, and once the garage has zones, the rest of the house stops absorbing the overflow.",
        cta="Book a Hendersonville walkthrough",
    ),
    dict(
        slug="home-organizer-gallatin-tn", name="Gallatin",
        h1="Home organizing in Gallatin",
        intro="Gallatin runs from historic houses around the downtown square to new construction out by Station Camp and the lake neighborhoods at Fairvue and Foxland Harbor. The old houses have beautiful rooms and almost no closets, which means storage has to be built rather than found. The new ones have the closets and no plan for them. Both are solvable, but not the same way.",
        c1t="Old houses welcome", c1b="Historic homes near the square need built storage, not more bins. I plan around what the house doesn't have.",
        c2t="New builds too", c2b="Out toward Station Camp it's the opposite problem: plenty of space, no plan for it.",
        c3t="Half an hour out", c3b="Gallatin is a regular route for me, with no travel fee and full-day availability.",
        jobtitle="A recent Gallatin project",
        jobbody="A 1940s house near the square with one closet for two kids. We added a low rod and labeled drawers, moved off-season clothes to under-bed storage, and got the daily clothes down to what actually fits right now.",
        faqq="Can you organize an older home in Gallatin?",
        faqa="Yes, and older homes are some of my favorite work. When a house has no closets, the answer is usually vertical storage and honest editing rather than more containers, and I'll tell you which one your house needs before you spend anything.",
        cta="Book a Gallatin walkthrough",
    ),
    dict(
        slug="home-organizer-lebanon-tn", name="Lebanon",
        h1="Home organizing in Lebanon",
        intro="Lebanon is fifteen minutes from my house, so I'm out here often. The neighborhoods around Five Oaks, Hunters Point, and the streets near Castle Heights range from older homes with small kitchens to newer places with more room than plan. What I hear most in Lebanon is that the house works fine until school starts, and then the mornings fall apart.",
        c1t="Closest to home", c1b="Fifteen minutes from me, so scheduling is easy and so is coming back.",
        c2t="Back-to-school resets", c2b="The drop zone, the lunch station, and the laundry, done in the two weeks before school starts.",
        c3t="Whole house or one room", c3b="Start with one space and see how it holds. Most people here do a pantry first.",
        jobtitle="A recent Lebanon project",
        jobbody="A family near Five Oaks whose entry table was carrying backpacks, mail, shoes, and sports gear all at once. We gave each of those four things its own spot, three of them at kid height, and the table went back to being a table.",
        faqq="How much notice do you need in Lebanon?",
        faqa="Usually a week or two, and less than that in the off season. Lebanon is my closest service area after Mount Juliet, so I can often fit in a walkthrough within a few days of you reaching out.",
        cta="Book a Lebanon walkthrough",
    ),
]

FAQS = [
    ("How much does a home organizer cost in Nashville?",
     "You get one flat price for the whole job, and you get it the same day as your walkthrough. The walkthrough takes about twenty minutes, at your house or over video, and it's free. Bins and baskets are quoted separately and bought at cost, so you can see exactly what you're paying for."),
    ("How long does a pantry take?",
     "One day, start to finish, for most kitchens. That includes emptying every shelf, throwing out what expired, grouping what's left, labeling the bins, and taking the donations with me when I go."),
    ("Do I need to clean up before you come?",
     "No, and please don't. Seeing the space the way it actually gets used is how I figure out where things should live. A pre-cleaned room tells me nothing."),
    ("What happens to the things I don't keep?",
     "I load them in my car and drop them off the same day, and I send you the donation receipt. Nothing leaves your house without you saying yes to it first."),
    ("Do you bring the bins and baskets?",
     "Yes. I measure during the walkthrough, send you the list with prices before I buy anything, and we use whatever you already own first. You are never charged a markup on containers."),
    ("Do I have to be home the whole time?",
     "No. Most clients are on calls or out of the house. I'll need you for about fifteen minutes at the start and twenty minutes at the end, and I'll text you photos if anything needs a decision."),
    ("What areas do you serve?",
     "Nashville, Franklin, Brentwood, Nolensville, Hendersonville, Mount Juliet, Gallatin, and Lebanon. I'm based in Mount Juliet, and there's no travel fee anywhere in that list."),
    ("Will it actually stay organized?",
     "That depends on whether the setup fits how your family already moves, which is the part I care most about getting right. I leave a printed card with five habits specific to your house, plus blank labels, and I come back a few months later to see how it held."),
]


def local_business_schema():
    # NOTE: phone/email are the placeholders flagged in the handoff README as
    # not-yet-real. Street address and opening hours are intentionally
    # omitted rather than invented — both are still blocked on the client.
    # `url` is deliberately the same on every page (the homepage) since this
    # schema describes one business entity (@id) — varying it per page would
    # be inconsistent data about the same entity.
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": f"{SITE_URL}/#business",
        "name": SITE_NAME,
        "image": f"{SITE_URL}/images/og-image.jpg",
        "url": f"{SITE_URL}/",
        "telephone": PHONE_TEL,
        "email": EMAIL,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Mount Juliet",
            "addressRegion": "TN",
            "addressCountry": "US",
        },
        "areaServed": [{"@type": "City", "name": t} for t in SERVICE_AREA_TOWNS],
        "sameAs": ["https://instagram.com/neatly_nash"],
    }


def faq_schema():
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in FAQS
        ],
    }


def faq_items_html():
    return "\n".join(
        f'  <div class="faq-item">\n'
        f'    <h2>{html.escape(q, quote=False)}</h2>\n'
        f'    <p class="body-md">{html.escape(a, quote=False)}</p>\n'
        f'  </div>'
        for q, a in FAQS
    )


def schema_script(*schemas):
    tags = []
    for s in schemas:
        tags.append(
            '<script type="application/ld+json">'
            + json.dumps(s, ensure_ascii=False)
            + "</script>"
        )
    return "\n".join(tags)


def read(path):
    return (TEMPLATES / path).read_text()


def mark_current_nav(header_html, url_path):
    link = f'class="nav-link" href="/{url_path}/"'
    return header_html.replace(link, f'{link} aria-current="page"')


def render_page(*, url_path, title, description, header_partial, content_html, extra_schema=None, noindex=False, extra_head=""):
    if noindex:
        indexing = '<meta name="robots" content="noindex">'
    else:
        canonical = f"{SITE_URL}/{url_path}".rstrip("/") + "/" if url_path else f"{SITE_URL}/"
        indexing = (
            f'<link rel="canonical" href="{canonical}">\n'
            f'<meta property="og:url" content="{canonical}">'
        )
    schemas = [local_business_schema()]
    if extra_schema:
        schemas.append(extra_schema)

    base = Template(read("base.html"))
    page = base.substitute(
        TITLE=html.escape(title),
        DESCRIPTION=html.escape(description),
        INDEXING=indexing,
        EXTRA_HEAD=extra_head,
        OG_TITLE=html.escape(title),
        SCHEMA=schema_script(*schemas),
        HEADER=mark_current_nav(read(f"partials/{header_partial}"), url_path),
        CONTENT=content_html,
        FOOTER=Template(read("partials/footer.html")).substitute(YEAR=date.today().year),
    )
    return page


def write_page(url_path, html):
    if url_path:
        out_dir = DIST / url_path
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "index.html"
    else:
        out_file = DIST / "index.html"
    out_file.write_text(html)
    return out_file


ASSET_URL = re.compile(r"(?<![\w.])/(?:css|js|images|fonts)/[\w./-]+\.(?:css|js|jpe?g|png|webp|svg|woff2)")


def fingerprint_asset_urls():
    """Append ?v=<content hash> to local asset URLs in the built HTML and CSS.

    netlify.toml caches /css, /js, /images and /fonts as immutable for a year,
    so a changed file must get a new URL or returning visitors keep the old one.
    """
    hashes = {}

    def versioned(match):
        url = match.group(0)
        if url not in hashes:
            asset = DIST / url.lstrip("/")
            if not asset.is_file():
                return url
            hashes[url] = hashlib.sha256(asset.read_bytes()).hexdigest()[:10]
        return f"{url}?v={hashes[url]}"

    for path in [*DIST.glob("css/*.css"), *DIST.rglob("*.html"), DIST / "site.webmanifest"]:
        path.write_text(ASSET_URL.sub(versioned, path.read_text()))


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # Static assets
    shutil.copytree(STATIC / "css", DIST / "css")
    shutil.copytree(STATIC / "js", DIST / "js")
    shutil.copytree(STATIC / "images", DIST / "images")
    shutil.copytree(STATIC / "fonts", DIST / "fonts")
    shutil.copy(STATIC / "site.webmanifest", DIST / "site.webmanifest")
    shutil.copy(STATIC / "favicon.ico", DIST / "favicon.ico")

    urls = []

    # -- Main pages ---------------------------------------------------------
    main_pages = [
        dict(
            url_path="", title="Home Organizer in Nashville, TN | Neatly Nash",
            description="Home organizing for kitchens, closets, and drop zones across Nashville, Franklin, Brentwood, and five nearby towns. Free walkthrough, same-day quote.",
            content="pages/index.html",
            # The hero headline's italic line is the only above-the-fold use of this face.
            extra_head='<link rel="preload" href="/fonts/cormorant-garamond-500-italic.woff2" as="font" type="font/woff2" crossorigin>',
        ),
        dict(
            url_path="services", title="Home Organizing Services | Neatly Nash",
            description="The Reset, The Weekday Fix, Whole Home, Move-In Ready, and dorm room setup — home organizing services in Greater Nashville, plus a seasonal tune-up retainer.",
            content="pages/services.html",
        ),
        dict(
            url_path="the-work", title="Before & After Home Organizing Projects | Neatly Nash",
            description="See what changed: real before-and-after home organizing projects in Mount Juliet, Franklin, and across Greater Nashville.",
            content="pages/the-work.html",
        ),
        dict(
            url_path="faq", title="Home Organizer FAQ — Cost, Process & Service Area | Neatly Nash",
            description="What does a home organizer cost in Nashville, how long does a pantry take, and what areas does Neatly Nash serve? Answers to the questions asked most.",
            content="pages/faq.html", content_vars=dict(FAQ_ITEMS=faq_items_html()),
            extra_schema=faq_schema(),
        ),
        dict(
            url_path="about", title="About Neatly Nash | Book a Free Organizing Walkthrough",
            description="Meet the founder of Neatly Nash and book a free twenty-minute walkthrough. You'll have a price the same day, no sales call.",
            content="pages/about.html",
        ),
    ]

    for p in main_pages:
        content = read(p["content"])
        if "content_vars" in p:
            content = Template(content).substitute(p["content_vars"])
        page_html = render_page(
            url_path=p["url_path"],
            title=p["title"],
            description=p["description"],
            header_partial="header.html",
            content_html=content,
            extra_schema=p.get("extra_schema"),
            extra_head=p.get("extra_head", ""),
        )
        write_page(p["url_path"], page_html)
        urls.append(p["url_path"])

    # -- Town pages -----------------------------------------------------------
    town_template = Template(read("pages/town.html"))
    for t in TOWNS:
        content = town_template.substitute(
            TOWNNAME=t["name"], H1=t["h1"], INTRO=t["intro"],
            C1T=t["c1t"], C1B=t["c1b"], C2T=t["c2t"], C2B=t["c2b"],
            C3T=t["c3t"], C3B=t["c3b"], JOBTITLE=t["jobtitle"], JOBBODY=t["jobbody"],
            FAQQ=t["faqq"], FAQA=t["faqa"], CTA=t["cta"],
        )
        page_html = render_page(
            url_path=t["slug"],
            title=f"Home Organizer in {t['name']}, TN | Neatly Nash",
            description=f"{t['h1']}. {t['faqq']} Free walkthrough, same-day quote, no travel fee in {t['name']}.",
            header_partial="header-town.html",
            content_html=content,
        )
        write_page(t["slug"], page_html)
        urls.append(t["slug"])

    # -- 404 page --------------------------------------------------------------
    # Not added to `urls`/sitemap.xml — it isn't a real content page to index.
    # Netlify serves dist/404.html automatically for any unmatched route.
    not_found_html = render_page(
        url_path="404",
        title="Page Not Found | Neatly Nash",
        description="The page you're looking for doesn't exist. Head back to Neatly Nash home organizing in Nashville, TN.",
        header_partial="header.html",
        content_html=read("pages/404.html"),
        noindex=True,
    )
    (DIST / "404.html").write_text(not_found_html)

    # -- robots.txt & sitemap.xml --------------------------------------------
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"
    )

    # No <lastmod>: stamping every URL with the build date on each deploy
    # misreports unchanged pages, and Google stops trusting the field.
    entries = []
    for u in urls:
        loc = f"{SITE_URL}/{u}".rstrip("/") + "/" if u else f"{SITE_URL}/"
        entries.append(f"  <url>\n    <loc>{loc}</loc>\n  </url>")
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    (DIST / "sitemap.xml").write_text(sitemap)

    fingerprint_asset_urls()

    print(f"Built {len(urls)} pages to {DIST}")


if __name__ == "__main__":
    build()
