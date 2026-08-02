"""Application-wide presentation rules for the custom Streamlit experience."""

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root {
	--ink:#10233E;
	--muted:#66758E;
	--soft-muted:#7D8BA3;
	--line:#DDE5F0;
	--line-strong:#C9D5E6;
	--blue:#1769E0;
	--blue-dark:#124BA4;
	--blue-soft:#EAF2FF;
	--canvas:#F3F6FB;
	--card:#FFFFFF;
	--card-soft:#FBFCFE;
	--green:#12845A;
	--amber:#A15A00;
	--shadow:0 14px 36px rgba(20,43,77,.08);
}

html, body, [class*="css"] {
	font-family:'DM Sans', sans-serif;
	color:var(--ink);
}

.stApp {
	background:
		radial-gradient(circle at top right, rgba(23,105,224,.08), transparent 25%),
		radial-gradient(circle at top left, rgba(18,132,90,.06), transparent 24%),
		var(--canvas);
}

#MainMenu, footer { visibility:hidden; }

/* Keep the header element (it hosts the native sidebar-expand control)
   but strip its chrome so it stays invisible. */
header[data-testid="stHeader"] {
	background:transparent !important;
	box-shadow:none !important;
	height:0 !important;
}

header[data-testid="stHeader"] [data-testid="stToolbar"],
header[data-testid="stHeader"] [data-testid="stDecoration"],
header[data-testid="stHeader"] [data-testid="stStatusWidget"] {
	display:none !important;
}

/* Zero-height toggle component should not add a vertical gap. */
.stApp iframe[title="st.iframe"][height="0"],
.stApp [data-testid="stCustomComponentV1"][height="0"] {
	height:0 !important;
	min-height:0 !important;
	display:block;
	margin:0 !important;
}

/* The floating hamburger is the primary reopen control, so hide Streamlit's
   native collapsed sidebar button (still clicked programmatically). */
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapsedControl"] {
	opacity:0 !important;
	pointer-events:none !important;
	width:0 !important;
	height:0 !important;
	overflow:hidden !important;
}

/* Smooth open/close animation for the sidebar panel. */
section[data-testid="stSidebar"] {
	transition:transform .28s cubic-bezier(.4,0,.2,1),
	           width .28s cubic-bezier(.4,0,.2,1),
	           margin .28s cubic-bezier(.4,0,.2,1) !important;
}

section[data-testid="stSidebar"] {
	background:linear-gradient(180deg,#10213E 0%,#0B1930 100%);
	border-right:0;
}

section[data-testid="stSidebar"] > div {
	padding:1.25rem .95rem 1.1rem;
}

section[data-testid="stSidebar"] * { color:#D9E5F7; }

section[data-testid="stSidebar"] .stRadio > div {
	gap:.35rem;
}

section[data-testid="stSidebar"] .stRadio label {
	border-radius:12px;
	padding:10px 11px;
	margin:2px 0;
	transition:background-color .16s ease, transform .16s ease, box-shadow .16s ease;
	position:relative;
	overflow:hidden;
}

section[data-testid="stSidebar"] .stRadio label:hover {
	background:rgba(255,255,255,.08);
	transform:translateX(1px);
}

section[data-testid="stSidebar"] .stRadio label:before {
	content:'';
	position:absolute;
	inset:0 auto 0 0;
	width:3px;
	border-radius:999px;
	background:transparent;
	transition:background-color .16s ease;
}

section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
	background:rgba(23,105,224,.18);
	color:#fff;
	font-weight:800;
	box-shadow:inset 0 0 0 1px rgba(110,171,255,.26);
}

section[data-testid="stSidebar"] .stRadio label:has(input:checked):before {
	background:#6FB3FF;
}

section[data-testid="stSidebar"] .stRadio input { display:none; }

section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
	color:#91A4C4 !important;
}

.block-container {
	max-width:1480px;
	padding:1.7rem 2.35rem 3rem;
}

.suite-brand {
	display:flex;
	gap:10px;
	align-items:center;
	margin:0 4px 1.35rem;
	color:#FFF;
}

.suite-mark {
	width:36px;
	height:36px;
	border-radius:11px;
	display:grid;
	place-items:center;
	background:linear-gradient(135deg,#68B2FF,#1D5FD2);
	font-weight:800;
	box-shadow:0 10px 22px rgba(0,0,0,.22);
}

.suite-brand strong {
	display:block;
	font-family:Manrope,sans-serif;
	font-size:.92rem;
	letter-spacing:-.02em;
}

.suite-brand span {
	font-size:.67rem;
	color:#91A4C4;
	letter-spacing:.08em;
}

.eyebrow {
	text-transform:uppercase;
	letter-spacing:.12em;
	color:var(--blue);
	font-size:.68rem;
	font-weight:800;
	margin-bottom:.45rem;
}

h1,h2,h3 {
	font-family:Manrope,sans-serif !important;
	letter-spacing:-.035em;
	color:var(--ink);
}

.page-title {
	font-size:2rem;
	margin:0 0 .35rem;
	font-weight:800;
}

.page-subtitle {
	color:var(--muted);
	margin:0 0 1.4rem;
	font-size:.96rem;
	line-height:1.55;
}

.hero {
	background:linear-gradient(120deg,#10213E 0%,#183869 55%,#1D69D8 100%);
	border-radius:24px;
	padding:1.95rem 2rem;
	color:#fff;
	position:relative;
	overflow:hidden;
	margin-bottom:1.3rem;
	box-shadow:var(--shadow);
}

.hero:before,
.home-workspace:before {
	content:'';
	position:absolute;
	inset:auto -70px -120px auto;
	width:270px;
	height:270px;
	border-radius:50%;
	background:rgba(129,194,255,.12);
	pointer-events:none;
}

.hero h1 {
	color:#fff;
	font-size:2rem;
	max-width:720px;
	margin:0 0 .55rem;
}

.hero p {
	color:#D7E6FB;
	max-width:700px;
	margin:0;
	line-height:1.6;
}

.hero-badge {
	display:inline-flex;
	align-items:center;
	gap:8px;
	background:rgba(255,255,255,.12);
	border:1px solid rgba(255,255,255,.18);
	border-radius:999px;
	padding:6px 11px;
	font-weight:700;
	font-size:.72rem;
	margin-bottom:1rem;
	letter-spacing:.04em;
}

.surface,
.stForm,
.home-workspace,
.activity-panel,
.filter-panel {
	background:var(--card);
	border:1px solid var(--line);
	border-radius:18px;
	padding:1.1rem 1.15rem;
	box-shadow:0 2px 8px rgba(21,42,77,.03);
}

.stForm {
	padding:1.35rem;
}

.home-workspace {
	position:relative;
	overflow:hidden;
	margin-bottom:1.1rem;
}

.home-workspace h2 {
	margin:0;
	font-size:1.1rem;
}

.home-workspace p,
.activity-panel p,
.filter-panel p {
	color:var(--muted);
	margin:.25rem 0 0;
	line-height:1.5;
}

.home-workspace .home-meta-grid {
	display:grid;
	grid-template-columns:repeat(2, minmax(0, 1fr));
	gap:.8rem;
	margin-top:1rem;
}

.home-workspace .home-meta-card,
.activity-item {
	background:var(--card-soft);
	border:1px solid #E7EDF6;
	border-radius:15px;
	padding:.9rem .95rem;
}

.home-workspace .home-meta-card .home-kicker,
.activity-item .home-kicker {
	text-transform:uppercase;
	letter-spacing:.08em;
	font-size:.68rem;
	font-weight:800;
	color:var(--soft-muted);
	margin-bottom:.35rem;
}

.home-workspace .home-meta-card .home-value,
.activity-item .home-value {
	font-family:Manrope,sans-serif;
	font-weight:800;
	font-size:.98rem;
	color:var(--ink);
	line-height:1.3;
	word-break:break-word;
}

.home-workspace .home-meta-card .home-detail,
.activity-item .home-detail {
	color:var(--muted);
	font-size:.8rem;
	line-height:1.45;
	margin-top:.25rem;
}

.workspace-hero-actions {
	display:grid;
	gap:.55rem;
}

.workspace-hero-actions .stButton button,
.workspace-hero-actions .stLinkButton a {
	min-height:2.45rem;
}

.workspace-track {
	display:grid;
	gap:.72rem;
	margin-top:1rem;
}

.home-section {
	margin-top:1rem;
}

.section-head {
	display:flex;
	justify-content:space-between;
	align-items:flex-end;
	margin:1.6rem 0 .75rem;
	gap:12px;
}

.section-head h2 {
	font-size:1.1rem;
	margin:0;
}

.section-head p {
	color:var(--muted);
	font-size:.82rem;
	margin:0;
}

.stat-line {
	background:#fff;
	border:1px solid var(--line);
	border-radius:15px;
	padding:.95rem 1rem;
	min-height:92px;
	box-shadow:0 1px 2px rgba(16,35,62,.02);
}

.stat-line .label {
	color:var(--muted);
	font-size:.75rem;
	font-weight:800;
	text-transform:uppercase;
	letter-spacing:.07em;
}

.stat-line .value {
	font-family:Manrope,sans-serif;
	font-weight:800;
	font-size:1.5rem;
	margin-top:.12rem;
}

.stat-line .detail {
	color:var(--muted);
	font-size:.75rem;
	margin-top:.1rem;
}

.info-card {
	background:#fff;
	border:1px solid var(--line);
	border-radius:16px;
	padding:1rem 1rem .95rem;
	margin-bottom:.75rem;
	transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease,background-color .18s ease;
}

.info-card:hover {
	transform:translateY(-2px);
	border-color:var(--line-strong);
	box-shadow:var(--shadow);
}

.info-card h3 {
	font-size:1rem;
	margin:.15rem 0 .35rem;
}

.info-card p {
	color:var(--muted);
	font-size:.84rem;
	line-height:1.45;
	margin:.25rem 0;
}

.dork-card,
.tool-card {
	min-height:0;
}

.tool-footer {
	border-top:1px solid #EEF2F7;
	margin-top:.78rem;
	padding-top:.72rem;
	color:#738197;
	font-size:.72rem;
	font-weight:700;
	line-height:1.35;
}

.card-top {
	display:flex;
	align-items:flex-start;
	justify-content:space-between;
	gap:10px;
}

.card-top-stack {
	display:flex;
	flex-direction:column;
	gap:4px;
}

.card-top-stack h3 {
	margin:0;
}

.chip {
	display:inline-flex;
	align-items:center;
	gap:4px;
	border-radius:999px;
	padding:4px 8px;
	font-size:.69rem;
	font-weight:800;
	line-height:1;
	white-space:nowrap;
}

.chip-blue { color:#145AC0;background:#EAF2FF; }
.chip-green { color:#0C704C;background:#E8F7F0; }
.chip-amber { color:#935000;background:#FFF2DB; }
.chip-slate { color:#55637A;background:#F0F3F8; }
.chip-purple { color:#6840A7;background:#F1EAFF; }

.query {
	background:#F7F9FD;
	border:1px solid #E3EAF4;
	border-radius:12px;
	padding:10px 11px;
	font-family:ui-monospace, SFMono-Regular, Menlo, monospace;
	color:#24354F;
	font-size:.8rem;
	line-height:1.5;
	word-break:break-word;
	margin:.72rem 0 .6rem;
}

.rationale {
	font-size:.79rem;
	color:var(--muted);
	min-height:34px;
	line-height:1.5;
}

.tool-mark {
	width:38px;
	height:38px;
	border-radius:11px;
	background:linear-gradient(135deg,#EAF2FF 0%, #F4F8FF 100%);
	color:#1769E0;
	font-size:.78rem;
	font-weight:800;
	display:grid;
	place-items:center;
	flex:0 0 auto;
	box-shadow:inset 0 0 0 1px rgba(23,105,224,.08);
}

.tool-title {
	font-family:Manrope,sans-serif;
	font-size:.98rem;
	font-weight:800;
	line-height:1.25;
}

.tool-meta {
	font-size:.74rem;
	color:var(--muted);
	margin-top:2px;
	line-height:1.35;
}

.tool-chip-row {
	display:flex;
	flex-wrap:wrap;
	gap:6px;
	margin-top:.75rem;
}

.tool-chip-row .chip {
	font-weight:700;
}

.empty {
	border:1px dashed #CAD4E3;
	border-radius:16px;
	padding:2.15rem;
	text-align:center;
	color:var(--muted);
	background:#FAFBFD;
}

.note {
	border-left:3px solid var(--blue);
	background:#F0F6FF;
	border-radius:0 12px 12px 0;
	padding:.8rem .95rem;
	color:#46607F;
	font-size:.83rem;
	margin:.8rem 0;
	line-height:1.55;
}

.filter-panel {
	margin-bottom:1rem;
}

.filter-panel .filter-summary {
	display:flex;
	flex-wrap:wrap;
	gap:8px;
	margin-top:.9rem;
}

.filter-panel .filter-summary .chip {
	background:#F4F7FB;
	border:1px solid #E2EAF4;
	color:#4E607B;
}

.activity-panel {
	padding:1rem 1.05rem;
}

.activity-list {
	display:grid;
	gap:.6rem;
	margin-top:.85rem;
}

.activity-item .home-value {
	font-size:.94rem;
}

.activity-item .activity-row {
	display:flex;
	justify-content:space-between;
	gap:10px;
	align-items:flex-start;
}

.stButton button,
.stDownloadButton button,
.stLinkButton a {
	width:100%;
	border-radius:13px !important;
	border:1px solid #D7E0EE !important;
	background:#fff !important;
	color:#24415F !important;
	font-size:.8rem !important;
	font-weight:700 !important;
	min-height:2.35rem !important;
	transition:transform .16s ease,box-shadow .16s ease,border-color .16s ease,background-color .16s ease,color .16s ease !important;
}

.stButton button:hover,
.stDownloadButton button:hover,
.stLinkButton a:hover {
	border-color:#1769E0 !important;
	color:#1769E0 !important;
	background:#F5F9FF !important;
	transform:translateY(-1px);
	box-shadow:0 8px 18px rgba(23,105,224,.08);
}

.stFormSubmitButton button {
	background:linear-gradient(180deg,#1C6DE4 0%, #1253B5 100%) !important;
	color:#fff !important;
	border-color:#1769E0 !important;
	box-shadow:0 7px 18px rgba(23,105,224,.2);
}

.stFormSubmitButton button:hover {
	background:linear-gradient(180deg,#145ECC 0%, #0F469A 100%) !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
	background:#fff;
	border-color:#D8E1EE;
	border-radius:13px;
	box-shadow:0 1px 2px rgba(16,35,62,.02);
}

[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
	background:#fff;
	border-color:#D8E1EE;
	border-radius:13px;
	box-shadow:0 1px 2px rgba(16,35,62,.02);
}

[data-testid="stMultiSelect"] [data-baseweb="tag"] {
	background:#EEF4FC;
	border:1px solid #D7E2F1;
	border-radius:999px;
	color:#355174;
}

.stSlider [data-baseweb="slider"] {
	padding-top:.55rem;
}

.stSlider [role="slider"] {
	box-shadow:0 0 0 5px rgba(23,105,224,.08);
}

.stSlider [data-baseweb="slider"] [class*="track"] {
	background:#DDE7F5;
}

.stSlider [data-baseweb="slider"] [class*="innerThumb"] {
	background:linear-gradient(180deg,#1C6DE4 0%, #1253B5 100%);
	border:2px solid #fff;
	box-shadow:0 8px 16px rgba(23,105,224,.22);
}

.stTabs [data-baseweb="tab-list"] {
	gap:10px;
	border-bottom:1px solid var(--line);
	padding-bottom:3px;
}

.stTabs [data-baseweb="tab"] {
	font-weight:700;
	color:#6A778C;
	padding:8px 12px;
	border-radius:999px 999px 0 0;
	border:1px solid transparent;
	background:transparent;
}

.stTabs [aria-selected="true"] {
	color:#1769E0;
	border-color:#D9E6F7 #D9E6F7 var(--canvas);
	background:#F4F8FE;
	box-shadow:0 -1px 0 rgba(23,105,224,.08) inset;
}

[data-testid="stExpander"] {
	border:1px solid #DCE5F0 !important;
	border-radius:16px !important;
	overflow:hidden;
	background:#fff;
	box-shadow:0 2px 8px rgba(21,42,77,.03);
}

[data-testid="stExpander"] summary {
	padding:.85rem 1rem !important;
	font-weight:700 !important;
	color:var(--ink) !important;
}

[data-testid="stExpander"] details > div {
	padding:0 1rem 1rem;
}

[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
	background:#fff;
	border-color:#D8E1EE;
	border-radius:13px;
}

button:focus-visible,
a:focus-visible,
input:focus-visible,
textarea:focus-visible {
	outline:3px solid rgba(23,105,224,.26) !important;
	outline-offset:2px !important;
}

[data-testid="stAlert"] {
	border-radius:12px;
}

.stProgress>div>div>div>div {
	background:#1769E0;
}

.page-status {
	display:flex;
	align-items:center;
	justify-content:center;
	height:2.35rem;
	font-size:.78rem;
	font-weight:700;
	color:var(--muted);
	background:var(--card-soft);
	border:1px solid var(--line);
	border-radius:13px;
	text-align:center;
	white-space:nowrap;
}

@media(max-width:1100px) {
	.block-container { padding:1.35rem 1.35rem 2.4rem; }
	.home-workspace .home-meta-grid { grid-template-columns:1fr; }
}

@media(max-width:1100px) {
	.suite-brand { margin-bottom:1rem; }
	section[data-testid="stSidebar"] > div { padding:1rem .85rem; }
	.workspace-track { gap:.55rem; }
}

@media(max-width:800px) {
	.block-container { padding:1rem .95rem 2rem; margin-left:0; }
	.hero { padding:1.45rem 1.2rem; border-radius:18px; }
	.hero h1 { font-size:1.55rem; margin:0 0 .4rem; }
	.page-title { font-size:1.55rem; margin-bottom:.3rem; }
	.page-subtitle { font-size:.9rem; }
	.section-head { align-items:flex-start; flex-direction:column; margin:1.35rem 0 .65rem; }
	.section-head h2 { font-size:1rem; }
	.section-head p { font-size:.75rem; }
	.info-card:hover { transform:none; border-color:var(--line); }
	.info-card { padding:.85rem .9rem; margin-bottom:.65rem; border-radius:14px; }
	.info-card h3 { font-size:.95rem; }
	.info-card p { font-size:.8rem; }
	.dork-card, .tool-card { min-height:0; }
	.stat-line { min-height:80px; padding:.85rem .9rem; }
	.stat-line .label { font-size:.7rem; }
	.stat-line .value { font-size:1.4rem; }
	.chip { padding:3px 7px; font-size:.66rem; }
	.query { padding:8px 9px; font-size:.75rem; }
	.rationale { font-size:.76rem; }
	.card-top { gap:8px; }
	.tool-chip-row { gap:5px; margin-top:.6rem; }
	.empty { padding:1.5rem 1rem; border-radius:14px; font-size:.85rem; }
	.note { padding:.7rem .85rem; font-size:.8rem; border-left-width:2px; margin:.65rem 0; }
	.hero-badge { font-size:.68rem; padding:5px 10px; margin-bottom:.85rem; }
	.suite-mark { width:32px; height:32px; }
	.suite-brand strong { font-size:.88rem; }
	.suite-brand span { font-size:.64rem; }
	.stButton button,
	.stDownloadButton button,
	.stLinkButton a { font-size:.75rem !important; min-height:2.2rem !important; }
	.stFormSubmitButton button { min-height:2.3rem !important; font-size:.8rem !important; }
	.home-workspace .home-meta-grid { grid-template-columns:1fr; gap:.7rem; }
	.home-kicker { font-size:.65rem; margin-bottom:.3rem; }
	.home-value { font-size:.92rem; }
	.home-detail { font-size:.76rem; }
	.activity-item { padding:.8rem .85rem; border-radius:12px; }
	.filter-panel { margin-bottom:.85rem; padding:1rem; }
	.filter-summary { gap:6px; margin-top:.75rem; }
	[data-testid="stExpander"] { border-radius:14px !important; }
	[data-testid="stExpander"] summary { padding:.75rem .9rem !important; font-size:.85rem !important; }
	[data-testid="stExpander"] details > div { padding:0 .9rem .9rem; }
	[data-testid="stTextInput"] input,
	[data-testid="stTextArea"] textarea,
	[data-testid="stSelectbox"] div[data-baseweb="select"] > div { border-radius:11px; font-size:.85rem; }
	[data-testid="stMultiSelect"] div[data-baseweb="select"] > div { border-radius:11px; }
	.stTabs [data-baseweb="tab"] { padding:7px 10px; font-size:.75rem; }
	.tool-mark { width:34px; height:34px; font-size:.72rem; }
	.tool-title { font-size:.92rem; }
	.tool-meta { font-size:.7rem; }
	.tool-footer { font-size:.68rem; margin-top:.65rem; padding-top:.6rem; }
}

@media(max-width:600px) {
	.block-container { padding:.8rem .75rem 1.5rem; }
	.hero { padding:1.2rem 1rem; }
	.hero h1 { font-size:1.3rem; }
	.page-title { font-size:1.3rem; }
	.page-subtitle { font-size:.85rem; margin-bottom:1rem; }
	.info-card { padding:.75rem .8rem; border-radius:12px; }
	.stat-line { min-height:70px; padding:.8rem .85rem; }
	.stButton button,
	.stDownloadButton button,
	.stLinkButton a { font-size:.72rem !important; min-height:2.1rem !important; border-radius:11px !important; }
	.section-head { margin:1.2rem 0 .6rem; gap:8px; }
	.section-head h2 { font-size:.95rem; }
	.home-workspace { margin-bottom:.9rem; padding:.95rem 1rem; }
	.home-workspace h2 { font-size:1rem; }
	.activity-list { gap:.5rem; }
	.card-top-stack { gap:3px; }
	.hero-badge { font-size:.63rem; padding:4px 9px; }
}

.copy-query {
	width:100%;
	height:38px;
	border-radius:12px;
	border:1px solid #D7E0EE;
	background:#fff;
	color:#24415F;
	font-size:12px;
	font-weight:700;
	cursor:pointer;
	transition:all .16s ease;
	box-shadow:0 1px 2px rgba(16,35,62,.02);
	position:relative;
	outline:none;
	touch-action:manipulation;
}

.copy-query:hover {
	border-color:#1769E0;
	color:#1769E0;
	background:#F5F9FF;
	transform:translateY(-1px);
	box-shadow:0 8px 16px rgba(23,105,224,.08);
}

.copy-query:active {
	transform:translateY(0);
}

.copy-query:focus-visible {
	outline:3px solid rgba(23,105,224,.26);
	outline-offset:2px;
}

.copy-success {
	border-color:#12845A !important;
	color:#12845A !important;
	background:#E8F7F0 !important;
}

.copy-error {
	border-color:#C84141 !important;
	color:#C84141 !important;
	background:#FFE8E8 !important;
}

.info-card { animation:fadeIn .35s ease-out; }

@keyframes fadeIn {
	from { opacity:0; transform:translateY(8px); }
	to { opacity:1; transform:translateY(0); }
}

@media(prefers-reduced-motion:reduce) {
	*,*:before,*:after {
		scroll-behavior:auto !important;
		transition-duration:.01ms !important;
		animation-duration:.01ms !important;
		animation-iteration-count:1 !important;
	}
}
</style>
"""
