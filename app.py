"""OSINT Investigation Suite — local, defensive public-search workspace."""

from __future__ import annotations

import csv
import io
import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import quote_plus

import streamlit as st
import streamlit.components.v1 as components

from osint_suite.catalog import CATEGORY_SOURCES, generate_dorks, launch_url, toolkit_catalog
from osint_suite.models import Bookmark, Dork, Investigation, ToolkitItem, utc_now
from osint_suite.storage import LocalStore
from osint_suite.styles import APP_CSS
from osint_suite.validation import escape, validate_typed_target


PROJECT_ROOT = Path(__file__).parent
STORE = LocalStore(PROJECT_ROOT / ".osint_data")

CHECKLIST_ITEMS = [
    "Username searched", "Email searched", "Phone searched", "Domain searched",
    "GitHub searched", "LinkedIn searched", "HIBP checked", "Shodan checked",
]
TARGET_FIELDS = [
    ("Full Name", "full_name"), ("Username", "username"), ("Email", "email"),
    ("Phone", "phone"), ("Domain", "domain"), ("Website", "website"),
    ("Company", "company"), ("IP Address", "ip_address"), ("Alias", "alias"),
    ("CCTV / Camera Asset", "cctv"), ("Indian Public Record", "indian_records"),
    ("Keyword", "keyword"),
]
SEARCH_ENGINES = ["Google", "Bing", "DuckDuckGo"]

DORK_CACHE_VERSION = 3

# Input types each field can search with, used to match toolkit tools.
TARGET_FIELD_INPUTS: dict[str, list[str]] = {
    "full_name": ["Keyword", "Username", "Company"],
    "username": ["Username", "Keyword"],
    "email": ["Email"],
    "phone": ["Phone"],
    "domain": ["Domain", "Website"],
    "website": ["Website", "Domain"],
    "company": ["Company", "Keyword"],
    "ip_address": ["IP Address", "Domain"],
    "alias": ["Username", "Keyword"],
    "cctv": ["Domain", "Website", "Keyword"],
    "indian_records": ["Keyword", "Company"],
    "keyword": ["Keyword", "Company"],
}

# Guidance under fields where analysts commonly misread the expected input.
TARGET_FIELD_HINTS: dict[str, str] = {
    "cctv": "Vendor, model, or firmware of an owned/authorized asset (e.g. Hikvision DS-2CD2143)",
    "indian_records": "Ministry, scheme, or public entity (e.g. Ministry of Finance)",
}

# Display labels for builder fields, so "cctv" is not title-cased to "Cctv".
FIELD_LABELS: dict[str, str] = {key: label for label, key in TARGET_FIELDS}


def field_display_name(field_key: str) -> str:
    """Return a polished label for a target-type key, e.g. cctv -> CCTV / Camera Asset."""
    return FIELD_LABELS.get(field_key, field_key.replace("_", " ").title())


def init_state() -> None:
    st.session_state.setdefault("active_investigation_id", None)
    st.session_state.setdefault("nav", "Home")


def get_investigations() -> list[Investigation]:
    return sorted(STORE.investigations(), key=lambda item: item.updated_at, reverse=True)


@st.cache_data(ttl=3600)
def cached_dorks(cache_version: int, target: str, target_type: str) -> list[Dork]:
    """Generate dorks for a target, cached for the session."""
    return generate_dorks(target, target_type)


def active_investigation(records: list[Investigation]) -> Investigation | None:
    selected = st.session_state.get("active_investigation_id")
    investigation = next((item for item in records if item.id == selected), None)
    if investigation:
        return investigation
    if records:
        st.session_state.active_investigation_id = records[0].id
        return records[0]
    return None


def persist_investigation(updated: Investigation) -> None:
    records = get_investigations()
    replacement = [updated if record.id == updated.id else record for record in records]
    STORE.save_investigations(replacement)


def clear_investigations() -> None:
    STORE.save_investigations([])
    st.session_state.active_investigation_id = None


def target_dork_groups(targets: dict[str, str]) -> list[tuple[str, str, list[Dork]]]:
    """Generate dork groups for each target field value entered."""
    groups: list[tuple[str, str, list[Dork]]] = []
    for label, key in TARGET_FIELDS:
        value = targets.get(key, "").strip()
        if value:
            groups.append((label, key, cached_dorks(DORK_CACHE_VERSION, value, key)))
    return groups


# Categories most relevant to each field, used to boost tool ranking.
FIELD_TOOLKIT_AFFINITY: dict[str, set[str]] = {
    "full_name": {"Username", "General"},
    "username": {"Username", "Developer"},
    "email": {"Email"},
    "phone": {"Phone"},
    "domain": {"Domain"},
    "website": {"Domain"},
    "company": {"Domain", "Developer", "General"},
    "ip_address": {"Domain"},
    "alias": {"Username"},
    "cctv": {"CCTV"},
    "indian_records": {"Indian Records", "General"},
    "keyword": {"General", "Developer"},
}


def recommended_tools_for_field(field_key: str) -> list[ToolkitItem]:
    """Return the top 3 tools for a field, ranked by input overlap and category affinity."""
    desired_inputs = set(TARGET_FIELD_INPUTS.get(field_key, ["Keyword"]))
    affinity = FIELD_TOOLKIT_AFFINITY.get(field_key, set())

    def sort_key(tool: ToolkitItem) -> tuple[int, int, float, str]:
        match_count = len(desired_inputs.intersection(tool.supported_inputs))
        category_bonus = 1 if tool.category in affinity else 0
        return (category_bonus, match_count, tool.rating, tool.name)

    candidates = [
        tool for tool in toolkit_catalog()
        if desired_inputs.intersection(tool.supported_inputs) or tool.category in affinity
    ]
    return sorted(candidates, key=sort_key, reverse=True)[:3]


def recommendation_block(field_label: str, field_key: str) -> None:
    """Render the top-3 tool recommendations for a field."""
    tools = recommended_tools_for_field(field_key)
    st.markdown(
        '<div class="section-head"><h2>Recommendations</h2>'
        '<p>Relevant investigation tools</p></div>',
        unsafe_allow_html=True,
    )
    if not tools:
        st.caption("No direct toolkit matches found for this field.")
        return
    columns = st.columns(min(3, len(tools)))
    for column, tool in zip(columns, tools):
        with column:
            st.markdown(
                '<div class="info-card" style="margin-bottom:.55rem">'
                '<div class="card-top">'
                '<div class="card-top-stack">'
                f'<span class="tool-meta">Recommended for {escape(field_label)}</span>'
                f'<h3>{escape(tool.name)}</h3>'
                '</div>'
                f'<span class="chip chip-blue">★ {tool.rating:.1f}</span>'
                '</div>'
                f'<p>{escape(tool.description)}</p>'
                '<div class="tool-chip-row">'
                f'<span class="chip chip-slate">{escape(tool.category)}</span>'
                f'<span class="chip chip-slate">{escape(", ".join(tool.supported_inputs[:2]))}</span>'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            st.link_button("Open tool ↗", tool.homepage, key=f"rec_{field_key}_{tool.id}")


def bookmark_index() -> set[tuple[str, str]]:
    """(item_type, id) pairs for O(1) bookmark lookups.

    Cached per script run in session state so a card grid does not re-read the
    bookmarks file for every card. Cleared whenever bookmarks are written.
    """
    cached = st.session_state.get("_bookmark_index")
    if cached is None:
        cached = {
            (bookmark.item_type, str(bookmark.payload.get("id", "")))
            for bookmark in STORE.bookmarks()
        }
        st.session_state["_bookmark_index"] = cached
    return cached


def invalidate_bookmark_index() -> None:
    st.session_state.pop("_bookmark_index", None)


def has_bookmark(item_type: str, item_id: str) -> bool:
    return (item_type, str(item_id)) in bookmark_index()


def add_bookmark(item_type: str, title: str, payload: dict[str, object]) -> None:
    if has_bookmark(item_type, str(payload.get("id", ""))):
        return
    bookmarks = STORE.bookmarks()
    bookmarks.append(Bookmark.create(item_type, title, payload))
    STORE.save_bookmarks(bookmarks)
    invalidate_bookmark_index()


def page_heading(title: str, subtitle: str) -> None:
    st.markdown(
        '<div class="eyebrow">OSINT Investigation Suite</div>'
        f'<h1 class="page-title">{escape(title)}</h1>'
        f'<p class="page-subtitle">{escape(subtitle)}</p>',
        unsafe_allow_html=True,
    )


def priority_class(priority: str) -> str:
    return {"High": "chip-amber", "Standard": "chip-blue", "Review": "chip-slate"}[priority]


def copy_button(query: str, element_id: str) -> None:
    """Copy button with clipboard API, execCommand fallback, and keyboard access."""
    safe_query = json.dumps(query)
    components.html(
        f'''<div style="width:100%">
        <button id="{element_id}" class="copy-query" type="button" aria-label="Copy query to clipboard">Copy</button>
        <script>
        (() => {{
            const button = document.getElementById("{element_id}");
            if (!button) return;
            const text = {safe_query};
            const reset = () => setTimeout(() => {{ button.textContent = "Copy"; button.classList.remove("copy-success"); }}, 2000);
            const copyText = async () => {{
                try {{
                    await navigator.clipboard.writeText(text);
                    button.textContent = "Copied";
                    button.classList.add("copy-success");
                    reset();
                }} catch (error) {{
                    console.error("Copy failed:", error);
                    try {{
                        const textarea = document.createElement("textarea");
                        textarea.value = text;
                        textarea.style.position = "fixed";
                        textarea.style.opacity = "0";
                        textarea.style.top = "0";
                        textarea.style.left = "0";
                        document.body.appendChild(textarea);
                        textarea.focus();
                        textarea.select();
                        const success = document.execCommand("copy");
                        textarea.remove();
                        if (success) {{
                            button.textContent = "Copied";
                            button.classList.add("copy-success");
                            reset();
                        }} else {{
                            button.textContent = "Copy failed";
                            button.classList.add("copy-error");
                        }}
                    }} catch (fallbackError) {{
                        button.textContent = "Copy failed";
                        button.classList.add("copy-error");
                        console.error("Copy fallback failed:", fallbackError);
                    }}
                }}
            }};
            button.addEventListener("click", copyText);
            button.addEventListener("keydown", (e) => {{
                if (e.key === "Enter" || e.key === " ") {{
                    e.preventDefault();
                    copyText();
                }}
            }});
        }})();
        </script>
        <style>
        body{{margin:0;background:transparent;font-family:'DM Sans',sans-serif}}
        .copy-query{{width:100%;height:38px;border-radius:12px;border:1px solid #D7E0EE;background:#fff;color:#24415F;font-size:12px;font-weight:700;cursor:pointer;transition:all .16s ease;box-shadow:0 1px 2px rgba(16,35,62,.02);position:relative;outline:none;touch-action:manipulation}}
        .copy-query:hover{{border-color:#1769E0;color:#1769E0;background:#F5F9FF;transform:translateY(-1px);box-shadow:0 8px 16px rgba(23,105,224,.08)}}
        .copy-query:active{{transform:translateY(0)}}
        .copy-query:focus-visible{{outline:3px solid rgba(23,105,224,.26);outline-offset:2px}}
        .copy-success{{border-color:#12845A !important;color:#12845A !important;background:#E8F7F0 !important}}
        .copy-error{{border-color:#C84141 !important;color:#C84141 !important;background:#FFE8E8 !important}}
        </style>
        </div>''',
        height=40,
    )


def dork_card(dork: Dork, key_prefix: str) -> None:
    st.markdown(
        '<div class="info-card dork-card">'
        '<div class="card-top">'
        '<div class="card-top-stack">'
        '<span class="tool-meta">Platform</span>'
        f'<h3>{escape(dork.platform)}</h3>'
        '</div>'
        f'<span class="chip {priority_class(dork.priority)}">{escape(dork.priority)}</span>'
        '</div>'
        '<div class="tool-chip-row">'
        f'<span class="chip chip-blue">{escape(dork.category)}</span>'
        '<span class="chip chip-slate">Generated query</span>'
        '</div>'
        f'<div class="query">{escape(dork.query)}</div>'
        f'<div class="rationale">{escape(dork.rationale)}</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    google, bing, duck = st.columns(3)
    with google:
        st.link_button("Google ↗", launch_url("Google", dork.query), key=f"g_{key_prefix}_{dork.id}")
    with bing:
        st.link_button("Bing ↗", launch_url("Bing", dork.query), key=f"b_{key_prefix}_{dork.id}")
    with duck:
        st.link_button("DuckDuckGo ↗", launch_url("DuckDuckGo", dork.query), key=f"d_{key_prefix}_{dork.id}")
    copy_col, bookmark_col = st.columns(2)
    with copy_col:
        copy_button(dork.query, f"copy_{key_prefix}_{dork.id}")
    with bookmark_col:
        label = "Saved" if has_bookmark("dork", dork.id) else "Bookmark"
        if st.button(label, key=f"bm_{key_prefix}_{dork.id}", disabled=label == "Saved"):
            add_bookmark("dork", f"{dork.platform} — {dork.category}", {
                "id": dork.id, "platform": dork.platform, "category": dork.category,
                "priority": dork.priority, "query": dork.query,
            })
            st.rerun()


def select_active_case(records: list[Investigation]) -> Investigation | None:
    current = active_investigation(records)
    if not current:
        return None
    labels = {item.id: f"{item.title} · {item.target_value}" for item in records}
    chosen_id = st.selectbox(
        "Active investigation", options=list(labels), index=list(labels).index(current.id),
        format_func=lambda item: labels[item], key="case_switcher",
    )
    st.session_state.active_investigation_id = chosen_id
    return next(item for item in records if item.id == chosen_id)


def home_page(records: list[Investigation]) -> None:
    current = active_investigation(records)
    bookmarks = STORE.bookmarks()
    current_dork_count = sum(len(dorks) for _, _, dorks in target_dork_groups(current.targets)) if current else 0
    st.markdown(
        '<section class="hero">'
        '<span class="hero-badge">LOCAL-FIRST • DEFENSIVE OSINT</span>'
        '<h1>Investigation workspace for scoped public-source research.</h1>'
        '<p>Track the current case, surface the active target, move into the next research step,'
        ' and keep recent activity visible without turning the home page into a dashboard.</p>'
        '</section>',
        unsafe_allow_html=True,
    )
    hero_left, hero_right = st.columns([1.35, 1])
    with hero_left:
        st.markdown(
            '<div class="home-workspace"><h2>Current Investigation</h2>'
            '<p>Everything below stays local and reflects the active case.</p></div>',
            unsafe_allow_html=True,
        )
        if current:
            current_username = current.targets.get("username") or "Not captured yet"
            details = [
                ("Target", current.target_value, current.case_ref or "No case reference attached"),
                ("Username", current_username, field_display_name(current.target_type)),
                ("Status", current.status, current.authorization_note or "No authorization note recorded"),
                ("Workspace", current.title, current.purpose or "No purpose recorded"),
            ]
            st.markdown('<div class="home-meta-grid">', unsafe_allow_html=True)
            for label, value, detail in details:
                st.markdown(
                    '<div class="home-meta-card">'
                    f'<div class="home-kicker">{escape(label)}</div>'
                    f'<div class="home-value">{escape(value)}</div>'
                    f'<div class="home-detail">{escape(detail)}</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="empty">Create an investigation to populate the workspace summary.</div>',
                unsafe_allow_html=True,
            )
    with hero_right:
        st.markdown(
            '<div class="home-workspace"><h2>Quick Actions</h2>'
            '<p>Continue the investigation flow from here.</p>'
            '<div class="workspace-track"></div></div>',
            unsafe_allow_html=True,
        )
        for label, target in [
            ("Open Investigation Builder", "Investigation Builder"),
            ("Open Dork Assistant", "Dork Assistant"),
            ("Open OSINT Toolkit", "OSINT Toolkit"),
            ("Open Reports", "Reports"),
        ]:
            if st.button(label, key=f"home_{target}"):
                st.session_state["_go_to"] = target
                st.rerun()
        st.markdown(
            '<div class="activity-panel" style="margin-top:1rem"><h2>Recent Activity</h2>'
            '<p>Latest records and bookmark updates.</p>'
            '<div class="activity-list">',
            unsafe_allow_html=True,
        )
        if current and current.notes:
            for note in reversed(current.notes[-3:]):
                st.markdown(
                    '<div class="activity-item"><div class="activity-row"><div>'
                    '<div class="home-kicker">Analyst note</div>'
                    f'<div class="home-value">{escape(note)}</div>'
                    '</div><span class="chip chip-green">Local</span></div></div>',
                    unsafe_allow_html=True,
                )
        elif records:
            for item in records[:3]:
                st.markdown(
                    '<div class="activity-item"><div class="activity-row"><div>'
                    '<div class="home-kicker">Updated investigation</div>'
                    f'<div class="home-value">{escape(item.title)}</div>'
                    f'<div class="home-detail">{escape(item.target_value)} · {escape(item.updated_at.replace("T", " ").replace("+00:00", " UTC"))}</div>'
                    '</div>'
                    f'<span class="chip chip-blue">{escape(item.status)}</span>'
                    '</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="empty">Recent activity will appear here after the first case is created.</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div></div>', unsafe_allow_html=True)
    stats = st.columns(4)
    stat_values = [
        ("Investigations", len(records), "local case records"),
        ("Curated dorks", current_dork_count or "0", "target-specific query cards"),
        ("Toolkit resources", len(toolkit_catalog()), "official source links"),
        ("Bookmarks", len(bookmarks), "saved research items"),
    ]
    for column, (label, value, detail) in zip(stats, stat_values):
        with column:
            st.markdown(
                '<div class="stat-line">'
                f'<div class="label">{label}</div>'
                f'<div class="value">{value}</div>'
                f'<div class="detail">{detail}</div>'
                '</div>',
                unsafe_allow_html=True,
            )
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown(
            '<div class="section-head"><h2>Recent investigations</h2>'
            '<p>Latest local activity</p></div>',
            unsafe_allow_html=True,
        )
        if records:
            for item in records[:4]:
                st.markdown(
                    '<div class="info-card">'
                    '<div class="card-top">'
                    f'<span class="chip chip-blue">{escape(field_display_name(item.target_type))}</span>'
                    f'<span class="chip chip-green">{escape(item.status)}</span>'
                    '</div>'
                    f'<h3>{escape(item.title)}</h3>'
                    f'<p><b>{escape(item.target_value)}</b> · {escape(item.case_ref or "No case reference")}</p>'
                    f'<p>Updated {escape(item.updated_at.replace("T", " ").replace("+00:00", " UTC"))}</p>'
                    '</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="empty">No investigations yet. Start with a target in Investigation Builder.</div>',
                unsafe_allow_html=True,
            )
    with right:
        st.markdown(
            '<div class="section-head"><h2>Quick start</h2>'
            '<p>A focused workflow</p></div>',
            unsafe_allow_html=True,
        )
        for label, target, helper in [
            ("1. Define target", "Investigation Builder", "Capture an authorized target and scope."),
            ("2. Generate queries", "Dork Assistant", "Choose transparent public-search patterns."),
            ("3. Save evidence trail", "Bookmarks", "Keep selected resources and analyst notes."),
            ("4. Export a brief", "Reports", "Create a local CSV, PDF, or Markdown handoff."),
        ]:
            st.markdown(
                '<div class="info-card">'
                f'<h3>{label}</h3><p>{helper}</p>'
                '</div>',
                unsafe_allow_html=True,
            )
            if st.button(f"Open {target}", key=f"quick_{target}"):
                st.session_state["_go_to"] = target
                st.rerun()
        st.markdown(
            '<div class="section-head"><h2>Saved bookmarks</h2>'
            '<p>Most recent</p></div>',
            unsafe_allow_html=True,
        )
        if bookmarks:
            for bookmark in reversed(bookmarks[-3:]):
                st.markdown(
                    '<div class="info-card">'
                    f'<span class="chip chip-slate">{escape(bookmark.item_type.title())}</span>'
                    f'<h3>{escape(bookmark.title)}</h3>'
                    '</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div class="empty">Bookmarks will appear here.</div>', unsafe_allow_html=True)


def builder_page(records: list[Investigation]) -> None:
    page_heading(
        "Investigation Builder",
        "Create a locally stored investigation record for an authorized target. No searches are run from this screen.",
    )
    st.markdown(
        '<div class="note">Use only targets you are authorized to investigate. This application generates'
        ' public search links and preserves your working notes; it does not scrape sources or bypass'
        ' access controls.</div>',
        unsafe_allow_html=True,
    )
    with st.form("new_investigation", clear_on_submit=True):
        title_col, ref_col = st.columns([1.5, 1])
        with title_col:
            title = st.text_input("Investigation title", placeholder="e.g. Acme public exposure review")
        with ref_col:
            case_ref = st.text_input("Case / reference", placeholder="Optional")
        purpose = st.text_area("Investigation purpose", placeholder="Describe the authorized defensive objective and intended outcome.", max_chars=600)
        authorization_note = st.text_input("Authorization / scope reference", placeholder="e.g. Internal approval reference or owned asset confirmation", max_chars=180)
        st.markdown("##### Target profile")
        st.caption("Enter one or more authorized targets. Each field generates its own independent, field-specific query catalog.")
        values: dict[str, str] = {}
        for start in range(0, len(TARGET_FIELDS), 3):
            chunk = TARGET_FIELDS[start:start + 3]
            columns = st.columns(len(chunk))
            for column, (label, key) in zip(columns, chunk):
                with column:
                    values[key] = st.text_input(label, key=f"target_{key}", help=TARGET_FIELD_HINTS.get(key))
        submitted = st.form_submit_button("Generate investigation workspace")
    if submitted:
        primary = next(((label, key) for label, key in TARGET_FIELDS if values[key].strip()), None)
        if primary is None:
            st.error("Add at least one target value before generating an investigation.")
        else:
            try:
                validated_targets = {
                    key: validate_typed_target(key, value)
                    for _, key in TARGET_FIELDS if (value := values[key].strip())
                }
            except ValueError as error:
                st.error(str(error))
                return
            label, target_key = primary
            investigation = Investigation.create(
                title, target_key, validated_targets[target_key], case_ref,
                targets=validated_targets, purpose=purpose, authorization_note=authorization_note,
            )
            investigation.checklist = {item: False for item in CHECKLIST_ITEMS}
            all_records = records + [investigation]
            STORE.save_investigations(all_records)
            st.session_state.active_investigation_id = investigation.id
            st.success(f"Workspace created for {label}: {validated_targets[target_key]}")
            st.rerun()
    if not records:
        return
    active = select_active_case(get_investigations())
    if not active:
        return
    tabs = st.tabs(["Workspace", "Analyst Notes", "Checklist"])
    with tabs[0]:
        st.markdown(
            '<div class="section-head"><h2>Investigation workspace</h2>'
            '<p>Current target and activity controls</p></div>',
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        for column, label, value in [(c1, "Primary target", active.target_value), (c2, "Target type", field_display_name(active.target_type)), (c3, "Case reference", active.case_ref or "Not assigned")]:
            with column:
                st.markdown(
                    '<div class="stat-line">'
                    f'<div class="label">{escape(label)}</div>'
                    f'<div class="value" style="font-size:1rem;word-break:break-word">{escape(value)}</div>'
                    f'<div class="detail">{escape(active.status)}</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
        targets_summary = " · ".join(f"{name.replace('_', ' ').title()}: {value}" for name, value in active.targets.items())
        st.markdown(
            '<div class="surface compact-surface">'
            '<b>Scoped target profile</b><br>'
            f'<span>{escape(targets_summary)}</span><br>'
            f'<span class="tool-meta">{escape(active.purpose or "No purpose recorded.")}</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Bookmark investigation", key=f"bookmark_inv_{active.id}", disabled=has_bookmark("investigation", active.id)):
            add_bookmark("investigation", active.title, {"id": active.id, "target": active.target_value, "target_type": active.target_type})
            st.rerun()
    with tabs[1]:
        note = st.text_area("New analyst note", placeholder="Record context, source caveats, or review decisions. Notes remain local to this project.")
        if st.button("Add note", key=f"add_note_{active.id}"):
            if note.strip():
                timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
                active.notes.append(f"[{timestamp}] {note.strip()}")
                active.updated_at = utc_now()
                persist_investigation(active)
                st.rerun()
        if active.notes:
            for note_text in reversed(active.notes):
                st.markdown(f'<div class="info-card"><p>{escape(note_text)}</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty">No analyst notes yet.</div>', unsafe_allow_html=True)
    with tabs[2]:
        updates: dict[str, bool] = {}
        for item in CHECKLIST_ITEMS:
            updates[item] = st.checkbox(item, value=active.checklist.get(item, False), key=f"check_{active.id}_{item}")
        if updates != active.checklist:
            active.checklist = updates
            active.updated_at = utc_now()
            persist_investigation(active)
        completed = sum(updates.values())
        st.caption(f"{completed} of {len(CHECKLIST_ITEMS)} review checks complete.")


def dork_page(records: list[Investigation]) -> None:
    page_heading(
        "Dork Assistant",
        "A transparent catalog of curated, defensive public-search queries. Review each query before opening it in a search engine.",
    )
    active = select_active_case(records)
    if not active:
        st.markdown('<div class="empty">Create an investigation first to generate a scoped dork workspace.</div>', unsafe_allow_html=True)
        return
    groups = target_dork_groups(active.targets)
    total_cards = sum(len(dorks) for _, _, dorks in groups)
    st.markdown(
        '<div class="filter-panel">'
        '<div class="home-kicker">Active target</div>'
        f'<div class="home-value">{total_cards} target-specific query cards</div>'
        '<div class="home-detail">Each section is field-specific — only your entered value is used for that field.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="note">Search links open an external search engine. Generated queries are prompts for'
        ' analyst review, not findings or validation of identity.</div>',
        unsafe_allow_html=True,
    )
    for field_label, field_key, dorks in groups:
        expander_title = f"{field_label} · {len(dorks)} dorks"
        with st.expander(expander_title, expanded=True):
            st.caption(f"Generated from the entered {field_label.lower()} value only")
            per_page = 8
            pages = max(1, (len(dorks) + per_page - 1) // per_page)
            # Plain (non-widget) state key so Prev/Next can update it directly.
            page_key = f"dork_page_{active.id}_{field_key}"
            page = max(1, min(st.session_state.get(page_key, 1), pages))
            st.session_state[page_key] = page

            if pages > 1:
                prev_col, status_col, next_col = st.columns([1, 1.4, 1])
                with prev_col:
                    if st.button("← Previous", key=f"prev_{page_key}", use_container_width=True, disabled=page <= 1):
                        st.session_state[page_key] = page - 1
                        st.rerun()
                with status_col:
                    start = (page - 1) * per_page + 1
                    end = min(page * per_page, len(dorks))
                    st.markdown(
                        f'<div class="page-status">Page {page} of {pages} · cards {start}–{end}</div>',
                        unsafe_allow_html=True,
                    )
                with next_col:
                    if st.button("Next →", key=f"next_{page_key}", use_container_width=True, disabled=page >= pages):
                        st.session_state[page_key] = page + 1
                        st.rerun()

            subset = dorks[(page - 1) * per_page: page * per_page]
            for row_start in range(0, len(subset), 2):
                columns = st.columns(2)
                for column, dork in zip(columns, subset[row_start:row_start + 2]):
                    with column:
                        dork_card(dork, f"{active.id}_{field_key}_{page}")
            recommendation_block(field_label, field_key)


def toolkit_card(tool: ToolkitItem, search_target: str | None = None) -> None:
    access = "Sign-in required" if tool.login_required else "No sign-in declared"
    supported_inputs = ''.join(f'<span class="chip chip-slate">{escape(input_type)}</span>' for input_type in tool.supported_inputs)
    search_availability = '<span class="chip chip-green">API available</span>' if tool.api_available else '<span class="chip chip-slate">No API declared</span>'
    login_badge = '<span class="chip chip-amber">Sign-in required</span>' if tool.login_required else '<span class="chip chip-green">No sign-in declared</span>'
    st.markdown(
        '<div class="info-card tool-card">'
        '<div class="card-top">'
        '<div style="display:flex;align-items:flex-start;gap:10px">'
        f'<div class="tool-mark">{escape(tool.logo)}</div>'
        '<div>'
        f'<div class="tool-title">{escape(tool.name)}</div>'
        f'<div class="tool-meta">★ {tool.rating:.1f} · {escape(tool.pricing)}</div>'
        '</div>'
        '</div>'
        f'<span class="chip chip-blue">{escape(tool.category)}</span>'
        '</div>'
        f'<p>{escape(tool.description)}</p>'
        '<div class="tool-chip-row">'
        '<span class="chip chip-purple">Official source</span>'
        f'{login_badge}{search_availability}{supported_inputs}'
        '</div>'
        f'<div class="tool-footer">{escape(access)} · {escape(tool.official_website)}</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    open_col, search_col, save_col = st.columns(3)
    with open_col:
        st.link_button("Open official tool ↗", tool.homepage, key=f"open_{tool.id}")
    with search_col:
        if tool.search_url and search_target:
            st.link_button("Official search ↗", tool.search_url.format(query=quote_plus(search_target)), key=f"search_{tool.id}")
        else:
            st.button("Official search", key=f"search_disabled_{tool.id}", disabled=True)
    with save_col:
        label = "Saved" if has_bookmark("tool", tool.id) else "Bookmark"
        if st.button(label, key=f"tool_bm_{tool.id}", disabled=label == "Saved"):
            add_bookmark("tool", tool.name, {"id": tool.id, "homepage": tool.homepage, "category": tool.category})
            st.rerun()


def toolkit_page(records: list[Investigation]) -> None:
    page_heading(
        "OSINT Toolkit",
        "A searchable local directory of official public-source resources. Each entry opens its official website in a new browser tab.",
    )
    tools = toolkit_catalog()
    current = active_investigation(records)
    query_col, category_col, input_col = st.columns([1.6, 1, 1])
    with query_col:
        query = st.text_input("Find a resource", placeholder="Search by name, category, or supported input")
    with category_col:
        category = st.selectbox("Category", ["All"] + sorted({item.category for item in tools}))
    with input_col:
        input_type = st.selectbox("Supported input", ["All"] + sorted({value for item in tools for value in item.supported_inputs}))
    lowered = query.lower().strip()
    filtered = [item for item in tools if (category == "All" or item.category == category) and (input_type == "All" or input_type in item.supported_inputs) and (not lowered or lowered in " ".join([item.name, item.description, item.category, *item.supported_inputs]).lower())]
    target_chip = f'<span class="chip chip-green">Target: {escape(current.target_value)}</span>' if current else ""
    st.markdown(
        '<div class="filter-panel">'
        '<div class="home-kicker">Search results</div>'
        f'<div class="home-value">{len(filtered)} official resources shown</div>'
        '<div class="home-detail">Catalog is local and does not call these services.</div>'
        '<div class="filter-summary">'
        f'<span class="chip chip-blue">Category: {escape(category)}</span>'
        f'<span class="chip chip-slate">Input: {escape(input_type)}</span>'
        f'{target_chip}'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    for row_start in range(0, len(filtered), 3):
        columns = st.columns(3)
        for column, tool in zip(columns, filtered[row_start:row_start + 3]):
            with column:
                toolkit_card(tool, current.target_value if current else None)
    if not filtered:
        st.markdown('<div class="empty">No toolkit resources match the current filter.</div>', unsafe_allow_html=True)


def bookmarks_page() -> None:
    page_heading("Bookmarks", "Saved dorks, tools, and investigations are retained locally with this project.")
    bookmarks = list(reversed(STORE.bookmarks()))
    if not bookmarks:
        st.markdown('<div class="empty">Save a dork, tool, or investigation to build a focused research queue.</div>', unsafe_allow_html=True)
        return
    kinds = st.multiselect("Show", ["dork", "tool", "investigation"], default=["dork", "tool", "investigation"])
    shown = [item for item in bookmarks if item.item_type in kinds]
    st.caption(f"{len(shown)} bookmark(s) shown · Stored locally in this project.")
    for bookmark in shown:
        payload = bookmark.payload
        content = payload.get("query", payload.get("target", payload.get("homepage", "")))
        st.markdown(
            '<div class="info-card">'
            '<div class="card-top">'
            '<div class="card-top-stack">'
            f'<span class="tool-meta">Saved {escape(bookmark.created_at[:10])}</span>'
            f'<h3>{escape(bookmark.title)}</h3>'
            '</div>'
            f'<span class="chip chip-blue">{escape(bookmark.item_type.title())}</span>'
            '</div>'
            f'<p>{escape(content)}</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        if bookmark.item_type == "dork":
            launches = st.columns(3)
            for column, engine in zip(launches, SEARCH_ENGINES):
                with column:
                    st.link_button(f"{engine} ↗", launch_url(engine, str(payload["query"])), key=f"bm_launch_{bookmark.id}_{engine}")
        elif bookmark.item_type == "tool":
            st.link_button("Open official tool ↗", str(payload["homepage"]), key=f"bm_open_{bookmark.id}")
        if st.button("Remove bookmark", key=f"remove_{bookmark.id}"):
            STORE.save_bookmarks([item for item in STORE.bookmarks() if item.id != bookmark.id])
            invalidate_bookmark_index()
            st.rerun()


def report_markdown(active: Investigation, dorks: Iterable[Dork], bookmarks: list[Bookmark]) -> str:
    dork_list = list(dorks)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M local time")
    query_lines = "\n".join(f"- **{dork.platform}** ({dork.category}, {dork.priority}): `{dork.query}`" for dork in dork_list)
    bookmark_lines = "\n".join(f"- {bookmark.item_type.title()}: {bookmark.title}" for bookmark in bookmarks) or "- None"
    note_lines = "\n".join(f"- {note}" for note in active.notes) or "- None"
    checks = sum(active.checklist.values())
    targets = "\n".join(f"- **{name.replace('_', ' ').title()}:** {value}" for name, value in active.targets.items())
    return f"""# OSINT Investigation Summary

**Generated:** {generated_at}  
**Investigation:** {active.title}  
**Case reference:** {active.case_ref or 'Not assigned'}  
**Target:** {active.target_value} ({field_display_name(active.target_type)})

## Target Profile

{targets}

## Scope and handling

This report summarizes analyst-selected public-source research planning. It does not represent scraped results, identity verification, or a conclusion about a person or organization. Use only with documented authorization and applicable law.

**Purpose:** {active.purpose or 'Not recorded'}  
**Authorization reference:** {active.authorization_note or 'Not recorded'}

## Coverage

- Curated query coverage: {len(dork_list)} generated public-search queries
- Query categories: {len(CATEGORY_SOURCES)}
- Checklist completion: {checks}/{len(CHECKLIST_ITEMS)}
- Saved bookmarks: {len(bookmarks)}

## Queries

{query_lines}

## Bookmarks

{bookmark_lines}

## Analyst Notes

{note_lines}
"""


def create_pdf(active: Investigation, dorks: list[Dork], bookmarks: list[Bookmark]) -> bytes | None:
    """Generate a PDF research brief when fpdf2 is available, else None."""
    try:
        from fpdf import FPDF
    except ImportError:
        return None

    INK = (16, 33, 62)
    BLUE = (23, 105, 224)
    MUTED = (102, 117, 142)
    SOFT = (243, 246, 251)

    def latin(text: str) -> str:
        return text.encode("latin-1", "replace").decode("latin-1")

    def wrapped_text(pdf: FPDF, text: str, font_size: int) -> None:
        usable_width = pdf.w - pdf.l_margin - pdf.r_margin
        if usable_width <= 0:
            usable_width = pdf.epw
        approx_chars = max(24, int(usable_width / (font_size * 0.42)))
        for paragraph in text.splitlines() or [""]:
            wrapped = textwrap.wrap(paragraph, width=approx_chars, break_long_words=True, break_on_hyphens=False) or [""]
            for chunk in wrapped:
                pdf.multi_cell(usable_width, font_size * 0.62, latin(chunk))

    def section_title(pdf: FPDF, text: str) -> None:
        pdf.ln(2)
        pdf.set_fill_color(*SOFT)
        pdf.set_text_color(*INK)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 9, latin(f"  {text}"), new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.ln(1.5)

    def cover_page(pdf: FPDF) -> None:
        pdf.add_page()
        pdf.set_fill_color(*INK)
        pdf.rect(0, 0, pdf.w, 78, style="F")
        pdf.set_fill_color(*BLUE)
        pdf.rect(0, 78, pdf.w, 3, style="F")
        pdf.set_xy(pdf.l_margin, 26)
        pdf.set_text_color(129, 194, 255)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, latin("OSINT INVESTIGATION SUITE"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(pdf.l_margin)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 26)
        pdf.multi_cell(0, 11, latin(active.title))
        pdf.set_x(pdf.l_margin)
        pdf.set_text_color(215, 230, 251)
        pdf.set_font("Helvetica", size=11)
        pdf.cell(0, 7, latin(f"Research-planning brief · {active.target_value}"), new_x="LMARGIN", new_y="NEXT")

        pdf.set_xy(pdf.l_margin, 96)
        pdf.set_text_color(*INK)
        cover_rows = [
            ("Target", f"{active.target_value} ({field_display_name(active.target_type)})"),
            ("Case reference", active.case_ref or "Not assigned"),
            ("Status", active.status),
            ("Purpose", active.purpose or "Not recorded"),
            ("Authorization", active.authorization_note or "Not recorded"),
            ("Generated", datetime.now().strftime("%Y-%m-%d %H:%M local time")),
        ]
        for label, value in cover_rows:
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*MUTED)
            pdf.cell(38, 7, latin(label.upper()))
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(*INK)
            pdf.multi_cell(0, 7, latin(value))
            pdf.ln(0.5)

        pdf.ln(4)
        pdf.set_draw_color(*BLUE)
        pdf.set_fill_color(240, 246, 255)
        pdf.set_text_color(*MUTED)
        pdf.set_font("Helvetica", size=9)
        pdf.multi_cell(0, 5.5, latin(
            "Scope: This report summarizes analyst-selected public-source research planning. It does not "
            "represent scraped results, identity verification, or a conclusion about any person or organization. "
            "Use only with documented authorization and applicable law."
        ), border=1, fill=True)

        coverage = [
            ("Curated queries", str(len(dorks))),
            ("Query categories", str(len(CATEGORY_SOURCES))),
            ("Bookmarks", str(len(bookmarks))),
            ("Checklist", f"{sum(active.checklist.values())}/{len(CHECKLIST_ITEMS)}"),
        ]
        pdf.ln(6)
        card_w = (pdf.w - pdf.l_margin - pdf.r_margin - 9) / 4
        x0 = pdf.l_margin
        y0 = pdf.get_y()
        for i, (label, value) in enumerate(coverage):
            x = x0 + i * (card_w + 3)
            pdf.set_xy(x, y0)
            pdf.set_fill_color(*SOFT)
            pdf.rect(x, y0, card_w, 20, style="F")
            pdf.set_xy(x, y0 + 3)
            pdf.set_font("Helvetica", "B", 15)
            pdf.set_text_color(*BLUE)
            pdf.cell(card_w, 8, latin(value), align="C")
            pdf.set_xy(x, y0 + 12)
            pdf.set_font("Helvetica", size=7)
            pdf.set_text_color(*MUTED)
            pdf.cell(card_w, 5, latin(label.upper()), align="C")

    def detail_pages(pdf: FPDF) -> None:
        pdf.add_page()
        pdf.set_text_color(*INK)
        section_title(pdf, f"Generated Queries ({len(dorks)})")
        current_category = None
        for dork in dorks:
            if dork.category != current_category:
                current_category = dork.category
                pdf.ln(1)
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(*BLUE)
                pdf.cell(0, 6, latin(current_category), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", size=8)
            pdf.set_text_color(*INK)
            wrapped_text(pdf, f"- {dork.platform} [{dork.priority}]: {dork.query}", font_size=8)

        section_title(pdf, "Analyst Notes")
        pdf.set_font("Helvetica", size=9)
        pdf.set_text_color(*INK)
        for note in active.notes or ["No analyst notes recorded."]:
            wrapped_text(pdf, f"- {note}", font_size=9)

        if bookmarks:
            section_title(pdf, f"Bookmarks ({len(bookmarks)})")
            pdf.set_font("Helvetica", size=9)
            pdf.set_text_color(*INK)
            for bookmark in bookmarks:
                wrapped_text(pdf, f"- [{bookmark.item_type.title()}] {bookmark.title}", font_size=9)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    cover_page(pdf)
    detail_pages(pdf)
    return bytes(pdf.output())


def reports_page(records: list[Investigation]) -> None:
    page_heading(
        "Reports",
        "Export a local research-planning summary. Reports contain targets, generated queries, bookmarks, notes, timestamps, and coverage—not search-engine results.",
    )
    active = select_active_case(records)
    if not active:
        st.markdown('<div class="empty">Create an investigation before generating a report.</div>', unsafe_allow_html=True)
        return
    dork_groups = target_dork_groups(active.targets)
    dorks = [item for _, _, group in dork_groups for item in group]
    bookmarks = STORE.bookmarks()
    st.markdown(
        '<div class="surface"><b>Report coverage</b><br>'
        f'<span style="color:#68758C;font-size:.84rem">{len(dorks)} queries · {len(bookmarks)} bookmarks'
        f' · {len(active.notes)} analyst notes · {sum(active.checklist.values())}/{len(CHECKLIST_ITEMS)} checklist checks</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    markdown = report_markdown(active, dorks, bookmarks)
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["platform", "category", "priority", "query", "target", "timestamp"])
    for item in dorks:
        writer.writerow([item.platform, item.category, item.priority, item.query, active.target_value, datetime.now().isoformat(timespec="seconds")])
    downloads = st.columns(3)
    with downloads[0]:
        st.download_button("Download CSV", csv_buffer.getvalue().encode("utf-8"), f"{active.id}_queries.csv", "text/csv")
    with downloads[1]:
        st.download_button("Download Markdown", markdown.encode("utf-8"), f"{active.id}_report.md", "text/markdown")
    with downloads[2]:
        pdf = create_pdf(active, dorks, bookmarks)
        if pdf:
            st.download_button("Download PDF", pdf, f"{active.id}_report.pdf", "application/pdf")
        else:
            st.info("Install fpdf2 to enable PDF export.")
    with st.expander("Preview Markdown report"):
        st.markdown(markdown)


def settings_page() -> None:
    page_heading("Settings", "Local application preferences and data-handling information.")
    settings = STORE.settings()
    with st.form("settings_form"):
        analyst = st.text_input("Analyst display name", value=settings.get("analyst_name", "Analyst"))
        engine = st.selectbox("Preferred search engine", SEARCH_ENGINES, index=SEARCH_ENGINES.index(settings.get("default_engine", "Google")))
        if st.form_submit_button("Save preferences"):
            STORE.save_settings({"analyst_name": analyst.strip() or "Analyst", "default_engine": engine})
            st.success("Preferences saved locally.")
    st.markdown(
        '<div class="section-head"><h2>Data handling</h2><p>Local-first project storage</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="surface">'
        '<p><b>Storage location</b><br>'
        f'<span style="color:#68758C">{STORE.root}</span></p>'
        '<p><b>External behavior</b><br>'
        '<span style="color:#68758C">The application generates outbound browser links only. It does not'
        ' scrape search engines, bypass authentication, process credentials, or execute toolkit software.</span></p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-head"><h2>Investigation history</h2><p>Clear local case records only</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="note">This removes all saved investigations from the local JSON store. Bookmarks and'
        ' preferences remain unchanged.</div>',
        unsafe_allow_html=True,
    )
    if st.button("Clear recent investigations", key="clear_investigations"):
        clear_investigations()
        st.success("Recent investigations cleared locally.")
        st.rerun()


def render_sidebar_toggle() -> None:
    """Floating hamburger that reopens a collapsed sidebar.

    The button lives in the parent document, appears only while the sidebar is
    collapsed, and clicks Streamlit's own expand control so the native open/close
    animation is preserved. The component iframe is zero-height.
    """
    components.html(
        """
        <script>
        (function () {
            const doc = window.parent.document;
            if (!doc) return;
            const BTN_ID = "osint-sidebar-toggle";

            const findSidebar = () => doc.querySelector('section[data-testid="stSidebar"]');
            const findExpandButton = () =>
                doc.querySelector('[data-testid="stExpandSidebarButton"] button') ||
                doc.querySelector('[data-testid="stExpandSidebarButton"]') ||
                doc.querySelector('[data-testid="stSidebarCollapsedControl"] button') ||
                doc.querySelector('[data-testid="stSidebarCollapsedControl"]');

            const isCollapsed = () => {
                const sidebar = findSidebar();
                if (!sidebar) return true;
                if (sidebar.getAttribute("aria-expanded") === "false") return true;
                const rect = sidebar.getBoundingClientRect();
                return rect.width < 40 || rect.left + rect.width <= 1;
            };

            let button = doc.getElementById(BTN_ID);
            if (!button) {
                button = doc.createElement("button");
                button.id = BTN_ID;
                button.type = "button";
                button.setAttribute("aria-label", "Open navigation menu");
                button.title = "Open navigation menu";
                button.innerHTML = "\\u2630";
                Object.assign(button.style, {
                    position: "fixed", left: "12px", top: "12px", zIndex: "1000000",
                    width: "44px", height: "44px", display: "none",
                    alignItems: "center", justifyContent: "center",
                    background: "#10213E", color: "#FFFFFF",
                    border: "1px solid rgba(23,105,224,.35)", borderRadius: "12px",
                    fontSize: "20px", lineHeight: "1", cursor: "pointer",
                    boxShadow: "0 6px 18px rgba(16,33,62,.28)",
                    transition: "transform .16s ease, background-color .16s ease, box-shadow .16s ease",
                    fontFamily: "'DM Sans', sans-serif",
                });
                button.addEventListener("mouseenter", () => {
                    button.style.background = "#124BA4";
                    button.style.transform = "translateY(-1px)";
                    button.style.boxShadow = "0 10px 24px rgba(23,105,224,.32)";
                });
                button.addEventListener("mouseleave", () => {
                    button.style.background = "#10213E";
                    button.style.transform = "translateY(0)";
                    button.style.boxShadow = "0 6px 18px rgba(16,33,62,.28)";
                });
                button.addEventListener("mousedown", () => { button.style.transform = "translateY(1px) scale(.97)"; });
                button.addEventListener("mouseup", () => { button.style.transform = "translateY(-1px)"; });
                button.addEventListener("click", () => {
                    const expand = findExpandButton();
                    if (expand) expand.click();
                    setTimeout(sync, 60);
                });
                doc.body.appendChild(button);
            }

            const sync = () => {
                if (!doc.body.contains(button)) doc.body.appendChild(button);
                button.style.display = isCollapsed() ? "flex" : "none";
            };

            // React to Streamlit re-renders and to the collapse/expand transition.
            const sidebar = findSidebar();
            if (sidebar && !sidebar.dataset.osintToggleWatched) {
                sidebar.dataset.osintToggleWatched = "1";
                new MutationObserver(sync).observe(sidebar, {
                    attributes: true, attributeFilter: ["aria-expanded", "style", "class"],
                });
            }
            if (!doc.body.dataset.osintToggleWatched) {
                doc.body.dataset.osintToggleWatched = "1";
                new MutationObserver(sync).observe(doc.body, { childList: true, subtree: false });
            }
            window.parent.addEventListener("resize", sync);
            // Poll briefly as a safety net for late DOM mounts.
            let ticks = 0;
            const poll = setInterval(() => { sync(); if (++ticks > 40) clearInterval(poll); }, 250);
            sync();
        })();
        </script>
        """,
        height=0,
    )


def main() -> None:
    st.set_page_config(page_title="OSINT Investigation Suite", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
    init_state()
    st.markdown(APP_CSS, unsafe_allow_html=True)
    render_sidebar_toggle()

    records = get_investigations()
    if "_go_to" in st.session_state:
        st.session_state["nav"] = st.session_state.pop("_go_to")

    with st.sidebar:
        st.markdown(
            '<div class="suite-brand">'
            '<div class="suite-mark">◈</div>'
            '<div><strong>OSINT Investigation Suite</strong>'
            '<span>DEFENSIVE RESEARCH WORKSPACE</span></div>'
            '</div>',
            unsafe_allow_html=True,
        )
        navigation = st.radio(
            "Navigation",
            ["Home", "Investigation Builder", "Dork Assistant", "OSINT Toolkit", "Bookmarks", "Reports", "Settings"],
            key="nav", label_visibility="collapsed",
        )
        st.markdown("---")
        current = active_investigation(records)
        if current:
            st.caption("ACTIVE INVESTIGATION")
            st.markdown(
                '<div class="activity-item">'
                '<div class="home-kicker">Current case</div>'
                f'<div class="home-value">{escape(current.title)}</div>'
                f'<div class="home-detail">{escape(current.target_value)}</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.caption("NO ACTIVE INVESTIGATION")
            st.markdown(
                '<div class="home-detail">Create a scoped local workspace to begin.</div>',
                unsafe_allow_html=True,
            )
        st.markdown("---")
        st.caption("PUBLIC-SOURCE RESEARCH ONLY")
    pages = {
        "Home": lambda: home_page(records),
        "Investigation Builder": lambda: builder_page(records),
        "Dork Assistant": lambda: dork_page(records),
        "OSINT Toolkit": lambda: toolkit_page(records),
        "Bookmarks": bookmarks_page,
        "Reports": lambda: reports_page(records),
        "Settings": settings_page,
    }
    pages[navigation]()


if __name__ == "__main__":
    main()
