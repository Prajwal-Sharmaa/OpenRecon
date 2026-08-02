"""Curated public-search patterns and the official toolkit catalog."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

import streamlit as st

from .models import Dork, ToolkitItem


# A curated set of public-source patterns per category. Field profiles below
# select only the categories that make sense for each investigation type.
CATEGORY_SOURCES: dict[str, list[tuple[str, str]]] = {
    "Social Media": [("LinkedIn", "linkedin.com"), ("X", "x.com"), ("Facebook", "facebook.com"), ("Instagram", "instagram.com"), ("Mastodon", "mastodon.social"), ("Reddit", "reddit.com"), ("TikTok", "tiktok.com"), ("YouTube", "youtube.com"), ("Threads", "threads.net"), ("Bluesky", "bsky.app"), ("Pinterest", "pinterest.com"), ("Tumblr", "tumblr.com")],
    "Professional": [("LinkedIn", "linkedin.com/in"), ("Crunchbase", "crunchbase.com"), ("Wellfound", "wellfound.com"), ("Glassdoor", "glassdoor.com"), ("Indeed", "indeed.com"), ("Xing", "xing.com"), ("Behance", "behance.net"), ("Dribbble", "dribbble.com"), ("AngelList", "angel.co"), ("G2", "g2.com"), ("Clutch", "clutch.co"), ("GoodFirms", "goodfirms.co")],
    "Developer": [("GitHub", "github.com"), ("GitLab", "gitlab.com"), ("Stack Overflow", "stackoverflow.com"), ("Bitbucket", "bitbucket.org"), ("PyPI", "pypi.org"), ("npm", "npmjs.com"), ("Hugging Face", "huggingface.co"), ("Docker Hub", "hub.docker.com"), ("CodePen", "codepen.io"), ("Replit", "replit.com"), ("Dev.to", "dev.to"), ("Kaggle", "kaggle.com")],
    "Documents": [("PDF documents", ""), ("Word documents", ""), ("Excel documents", ""), ("PowerPoint documents", ""), ("Google Docs", "docs.google.com"), ("Google Drive", "drive.google.com"), ("SlideShare", "slideshare.net"), ("Scribd", "scribd.com"), ("Issuu", "issuu.com"), ("DocDroid", "docdroid.net"), ("Academia", "academia.edu"), ("ResearchGate", "researchgate.net")],
    "Resume": [("LinkedIn profiles", "linkedin.com/in"), ("Indeed resumes", "indeed.com"), ("VisualCV", "visualcv.com"), ("LiveCareer", "livecareer.com"), ("Resume.io", "resume.io"), ("Zety", "zety.com"), ("Jobcase", "jobcase.com"), ("Monster", "monster.com"), ("CareerBuilder", "careerbuilder.com"), ("Naukri", "naukri.com"), ("Google Drive", "drive.google.com"), ("PDF resumes", "")],
    "Portfolio": [("Behance", "behance.net"), ("Dribbble", "dribbble.com"), ("ArtStation", "artstation.com"), ("Adobe Portfolio", "portfolio.adobe.com"), ("Cargo", "cargo.site"), ("Squarespace", "squarespace.com"), ("Wix", "wixsite.com"), ("GitHub Pages", "github.io"), ("Medium", "medium.com"), ("WordPress", "wordpress.com"), ("Notion", "notion.site"), ("Webflow", "webflow.io")],
    "Email": [("Gravatar", "gravatar.com"), ("GitHub", "github.com"), ("GitLab", "gitlab.com"), ("Stack Overflow", "stackoverflow.com"), ("Pastebin", "pastebin.com"), ("Google Groups", "groups.google.com"), ("Google Docs", "docs.google.com"), ("Keybase", "keybase.io"), ("OpenStreetMap", "openstreetmap.org"), ("Mastodon", "mastodon.social"), ("Discourse", "discourse.org"), ("Reddit", "reddit.com")],
    "Phone": [("Public web", ""), ("Facebook", "facebook.com"), ("LinkedIn", "linkedin.com"), ("X", "x.com"), ("Google Groups", "groups.google.com"), ("Pastebin", "pastebin.com"), ("GitHub", "github.com"), ("Reddit", "reddit.com"), ("Instagram", "instagram.com"), ("YouTube", "youtube.com"), ("Public PDFs", ""), ("Public business sites", "")],
    "Domain": [("Indexed domain", ""), ("Subdomain references", ""), ("Public documents", ""), ("GitHub", "github.com"), ("GitLab", "gitlab.com"), ("Stack Overflow", "stackoverflow.com"), ("Reddit", "reddit.com"), ("Wayback references", "web.archive.org"), ("Public APIs", ""), ("Media mentions", ""), ("Job listings", ""), ("Public forums", "")],
    "Research": [("Google Scholar", "scholar.google.com"), ("Semantic Scholar", "semanticscholar.org"), ("arXiv", "arxiv.org"), ("Crossref", "crossref.org"), ("PubMed", "pubmed.ncbi.nlm.nih.gov"), ("ResearchGate", "researchgate.net"), ("Academia", "academia.edu"), ("SSRN", "ssrn.com"), ("DOAJ", "doaj.org"), ("Zenodo", "zenodo.org"), ("OSF", "osf.io"), ("Google Books", "books.google.com")],
    "Media": [("YouTube", "youtube.com"), ("Vimeo", "vimeo.com"), ("Flickr", "flickr.com"), ("SoundCloud", "soundcloud.com"), ("Spotify", "open.spotify.com"), ("Podcast sites", ""), ("News sites", ""), ("Image references", "images.google.com"), ("Dailymotion", "dailymotion.com"), ("Twitch", "twitch.tv"), ("Mixcloud", "mixcloud.com"), ("Internet Archive", "archive.org")],
    "Government": [("US .gov", "gov"), ("UK .gov", "gov.uk"), ("EU Europa", "europa.eu"), ("UN", "un.org"), ("World Bank", "worldbank.org"), ("SEC", "sec.gov"), ("US Congress", "congress.gov"), ("Companies House", "gov.uk"), ("Data.gov", "data.gov"), ("Public records", ""), ("Government PDFs", ""), ("Official press releases", "")],
    "Blogs": [("Medium", "medium.com"), ("Substack", "substack.com"), ("WordPress", "wordpress.com"), ("Blogger", "blogspot.com"), ("Dev.to", "dev.to"), ("Hashnode", "hashnode.com"), ("Ghost", "ghost.io"), ("Tumblr", "tumblr.com"), ("Hackernoon", "hackernoon.com"), ("Vocal", "vocal.media"), ("Quora Spaces", "quora.com"), ("Personal blogs", "")],
    "Forums": [("Reddit", "reddit.com"), ("Stack Overflow", "stackoverflow.com"), ("Quora", "quora.com"), ("Discourse", "discourse.org"), ("Hacker News", "news.ycombinator.com"), ("XDA", "xdaforums.com"), ("Kaggle", "kaggle.com"), ("GitHub Discussions", "github.com"), ("Google Groups", "groups.google.com"), ("Steam Community", "steamcommunity.com"), ("Mastodon", "mastodon.social"), ("Public forums", "")],
    "Paste Sites": [("Pastebin", "pastebin.com"), ("GitHub Gists", "gist.github.com"), ("GitLab snippets", "gitlab.com"), ("Rentry", "rentry.co"), ("PrivateBin public pages", "privatebin.net"), ("Paste.ee", "paste.ee"), ("ControlC", "controlc.com"), ("JustPaste", "justpaste.it"), ("Hastebin", "hastebin.com"), ("dpaste", "dpaste.org"), ("0bin", "0bin.net"), ("Public paste references", "")],
    "Code Repositories": [("GitHub code", "github.com"), ("GitLab projects", "gitlab.com"), ("Bitbucket", "bitbucket.org"), ("Codeberg", "codeberg.org"), ("SourceHut", "sr.ht"), ("Gitea instances", "gitea.com"), ("Apache Git", "gitbox.apache.org"), ("KDE Invent", "invent.kde.org"), ("GNOME GitLab", "gitlab.gnome.org"), ("Launchpad", "launchpad.net"), ("SourceForge", "sourceforge.net"), ("Google Source", "source.google.com")],
    "Public Files": [("PDF", ""), ("DOCX", ""), ("XLSX", ""), ("PPTX", ""), ("CSV", ""), ("TXT", ""), ("Public Google Drive", "drive.google.com"), ("Dropbox links", "dropbox.com"), ("OneDrive links", "onedrive.live.com"), ("Box links", "box.com"), ("Internet Archive", "archive.org"), ("DocumentCloud", "documentcloud.org")],
    "CCTV & Cameras": [("Hikvision", "hikvision.com"), ("Dahua", "dahua.com"), ("Axis Communications", "axis.com"), ("Bosch Security", "boschsecurity.com"), ("Hanwha Vision", "hanwha-techwin.com"), ("Uniview", "uniview.com"), ("TP-Link VIGI", "tp-link.com"), ("Reolink", "reolink.com"), ("Ubiquiti", "ubiquiti.com"), ("CP Plus", "cpplus.co.in"), ("VIVOTEK", "vivotek.com"), ("Device manuals", "")],
    "Indian Public Records": [("Government websites", "gov.in"), ("Ministry PDFs", ""), ("Court judgments", "indiankanoon.org"), ("Gazette publications", "egazette.nic.in"), ("Public tenders", "tenders.gov.in"), ("RTI publications", ""), ("Election documents", "eci.gov.in"), ("Parliamentary records", "loksabha.gov.in"), ("Company filings", "mca.gov.in"), ("Official manuals", ""), ("Policy documents", ""), ("Public notices", "")],
}

# Extra reviewed lenses per category. Declarative only: the app builds search
# links, it never crawls the listed services.
CATEGORY_EXPANSIONS: dict[str, list[tuple[str, str]]] = {
    "Social Media": [("Telegram public web", "t.me"), ("Discord public web", "discord.com"), ("Linktree", "linktr.ee"), ("Ko-fi", "ko-fi.com")],
    "Professional": [("Company directory", "theorg.com"), ("Speaker profile", "sessionize.com"), ("Conference profile", "speakerdeck.com"), ("Professional news", "prnewswire.com")],
    "Developer": [("Packagist", "packagist.org"), ("RubyGems", "rubygems.org"), ("Maven Central", "central.sonatype.com"), ("NuGet", "nuget.org")],
    "Documents": [("PDF archive", "archive.org"), ("DocumentCloud", "documentcloud.org"), ("Public S3 references", "s3.amazonaws.com"), ("OneDrive documents", "onedrive.live.com")],
    "Resume": [("GitHub profile", "github.com"), ("Speaker Deck", "speakerdeck.com"), ("SlideShare", "slideshare.net"), ("Public CV files", "")],
    "Portfolio": [("Read.cv", "read.cv"), ("Contra", "contra.com"), ("Figma Community", "figma.com"), ("Awwwards", "awwwards.com")],
    "Email": [("Google Groups", "groups.google.com"), ("Public mailing lists", "lists.apache.org"), ("GitHub commits", "github.com"), ("Keybase", "keybase.io")],
    "Phone": [("LinkedIn mentions", "linkedin.com"), ("Business directory", "yellowpages.com"), ("Public documents", ""), ("Public contact pages", "")],
    "Domain": [("Certificate references", "crt.sh"), ("Internet Archive", "web.archive.org"), ("DNS documentation", "docs.aws.amazon.com"), ("Public source code", "github.com")],
    "Research": [("OpenAlex", "openalex.org"), ("CORE", "core.ac.uk"), ("BASE", "base-search.net"), ("Google Patents", "patents.google.com")],
    "Media": [("Unsplash", "unsplash.com"), ("Getty Images", "gettyimages.com"), ("Bandcamp", "bandcamp.com"), ("TuneIn", "tunein.com")],
    "Government": [("US Federal Register", "federalregister.gov"), ("UK Parliament", "parliament.uk"), ("EU TED", "ted.europa.eu"), ("OpenCorporates", "opencorporates.com")],
    "Blogs": [("Blogger", "blogger.com"), ("Write.as", "write.as"), ("Tealfeed", "tealfeed.com"), ("Bear Blog", "bearblog.dev")],
    "Forums": [("Lobsters", "lobste.rs"), ("Product Hunt", "producthunt.com"), ("Dev Community", "dev.to"), ("Hashnode", "hashnode.com")],
    "Paste Sites": [("GitHub code search", "github.com"), ("SourceHut paste", "sr.ht"), ("Public text files", "gist.github.com"), ("Archive references", "archive.org")],
    "Code Repositories": [("Hugging Face", "huggingface.co"), ("Kaggle", "kaggle.com"), ("Bitbucket", "bitbucket.org"), ("GitHub Gists", "gist.github.com")],
    "Public Files": [("ODT", ""), ("RTF", ""), ("JSON", ""), ("XML", "")],
}

FILE_TYPES = {"PDF": "pdf", "DOCX": "docx", "XLSX": "xlsx", "PPTX": "pptx", "CSV": "csv", "TXT": "txt", "ODT": "odt", "RTF": "rtf", "JSON": "json", "XML": "xml"}

# Documentation lenses for owned CCTV / network-camera assets. These target
# publicly indexed vendor material (datasheets, manuals, firmware notices),
# never live devices or camera feeds.
CCTV_DOC_ASPECTS = [
    "datasheet", "user manual", "firmware release notes", "configuration guide",
    "quick start guide", "installation manual", "specification sheet",
    "knowledge base", "support documentation", "product family overview",
    "hardening guide", "compatibility list",
]

# Public-record lenses when a source has no fixed host. All stay on officially
# published, non-personal material (gazettes, tenders, policy PDFs).
INDIAN_RECORD_ASPECTS = [
    'filetype:pdf site:gov.in', '"gazette notification" filetype:pdf',
    '"public tender" filetype:pdf', '"office memorandum" filetype:pdf',
    '"annual report" site:gov.in filetype:pdf', '"notification" site:nic.in',
    '"policy document" filetype:pdf', '"circular" site:gov.in filetype:pdf',
    '"RTI" filetype:pdf', '"committee report" filetype:pdf',
    '"press release" site:pib.gov.in', '"official report" filetype:pdf',
]

FIELD_DORK_PROFILES: dict[str, list[str]] = {
    "full_name": ["Social Media", "Professional", "Resume", "Portfolio", "Media", "Blogs", "Forums", "Research"],
    "username": ["Social Media", "Developer", "Email", "Forums", "Paste Sites", "Code Repositories", "Professional", "Blogs"],
    "email": ["Email", "Developer", "Paste Sites", "Forums", "Documents", "Public Files", "Code Repositories"],
    "phone": ["Phone", "Social Media", "Forums", "Government", "Public Files", "Professional"],
    "company": ["Professional", "Domain", "Developer", "Government", "Media", "Research", "Blogs"],
    "website": ["Domain", "Developer", "Documents", "Public Files", "Media", "Forums", "Professional"],
    "domain": ["Domain", "Developer", "Documents", "Public Files", "Government", "Research", "Code Repositories"],
    "ip_address": ["Domain", "Developer", "Government", "Public Files", "Research", "Code Repositories"],
    "alias": ["Social Media", "Developer", "Forums", "Paste Sites", "Code Repositories", "Blogs", "Email", "Professional"],
    "cctv": ["CCTV & Cameras", "Documents", "Public Files", "Forums", "Code Repositories"],
    "indian_records": ["Indian Public Records", "Government", "Documents", "Public Files", "Research"],
    "keyword": ["Social Media", "Professional", "Developer", "Documents", "Research", "Media", "Government", "Blogs", "Forums", "Paste Sites", "Code Repositories", "Public Files"],
}


def _quoted(value: str) -> str:
    return f'"{value.strip().replace("\"", "")}"'


def _query(category: str, label: str, site: str, target: str, target_type: str, index: int) -> str:
    quoted = _quoted(target)
    domain_restricted = target_type in {"domain", "website"}
    target_domain = target.removeprefix("https://").removeprefix("http://").split("/")[0]
    if category in {"Documents", "Public Files"} and label in FILE_TYPES:
        prefix = f"site:{target_domain} " if domain_restricted else ""
        return f"{prefix}filetype:{FILE_TYPES[label]} {quoted}"
    if category == "CCTV & Cameras":
        aspect = CCTV_DOC_ASPECTS[index % len(CCTV_DOC_ASPECTS)]
        # Owned-asset documentation discovery: pair the vendor/keyword with a
        # documentation lens, scoped to the vendor site when one is known.
        if site:
            return f'site:{site} {quoted} "{aspect}"'
        return f'{quoted} "{aspect}" filetype:pdf'
    if category == "Indian Public Records":
        aspect = INDIAN_RECORD_ASPECTS[index % len(INDIAN_RECORD_ASPECTS)]
        if site:
            return f"site:{site} {quoted}"
        return f"{quoted} {aspect}"
    if category == "Domain" and domain_restricted:
        variants = [
            f"site:{target_domain}", f'"{target_domain}" -site:{target_domain}',
            f"site:*.{target_domain}", f'"{target_domain}" filetype:pdf',
        ]
        return variants[index % len(variants)]
    if site:
        suffix = "" if index % 3 else " -login -signup"
        return f"site:{site} {quoted}{suffix}"
    return quoted


def _rationale(category: str, platform: str) -> str:
    if category == "CCTV & Cameras":
        return f"Vendor documentation lens for {platform}; use only for owned or authorized assets. Opens public docs, not devices."
    if category == "Indian Public Records":
        return f"Officially published public record via {platform}; targets non-personal government material only."
    return f"Public-source discovery on {platform}; verify relevance before recording a finding."


def generate_dorks(target: str, target_type: str) -> list[Dork]:
    """Build the query catalog for a target of the given type."""
    dorks: list[Dork] = []
    category_order = FIELD_DORK_PROFILES.get(target_type, list(CATEGORY_SOURCES))
    for category in category_order:
        sources = [*CATEGORY_SOURCES[category], *CATEGORY_EXPANSIONS.get(category, [])]
        for index, (platform, site) in enumerate(sources):
            priority = "High" if index < 3 else "Standard" if index < 8 else "Review"
            query = _query(category, platform, site, target, target_type, index)
            dorks.append(Dork(
                id=f"{target_type}-{category.lower().replace(' ', '-')}-{index + 1}",
                platform=platform,
                category=category,
                priority=priority,
                query=query,
                rationale=_rationale(category, platform),
            ))
    return dorks


def launch_url(engine: str, query: str) -> str:
    encoded = quote_plus(query)
    endpoints = {
        "Google": f"https://www.google.com/search?q={encoded}",
        "Bing": f"https://www.bing.com/search?q={encoded}",
        "DuckDuckGo": f"https://duckduckgo.com/?q={encoded}",
    }
    return endpoints[engine]


@st.cache_data(ttl=3600)
@lru_cache(maxsize=1)
def toolkit_catalog() -> list[ToolkitItem]:
    """Load and cache the toolkit reference database."""
    data_path = Path(__file__).parent / "data" / "toolkit.json"
    values = json.loads(data_path.read_text(encoding="utf-8"))
    return [ToolkitItem.from_dict(item) for item in values]
