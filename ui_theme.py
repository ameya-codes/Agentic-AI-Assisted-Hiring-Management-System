"""
Visual design system for Streamlit — calm, spacious, product-grade polish.
"""

from __future__ import annotations

import html

import streamlit as st


def inject_css(*, sidebar_visible: bool) -> None:
    hide_sidebar = "" if sidebar_visible else '[data-testid="stSidebar"] { display: none !important; }'
    css = f"""
    <style>
    :root {{
      --tc-bg: #f6f7f9;
      --tc-surface: #ffffff;
      --tc-border: #e8eaed;
      --tc-text: #111418;
      --tc-muted: #5f6368;
      --tc-soft: #80868b;
      --tc-accent: #4338ca;
      --tc-accent-soft: #eef2ff;
      --tc-radius: 14px;
      --tc-radius-sm: 10px;
      --tc-shadow: 0 1px 2px rgba(17, 20, 24, 0.06), 0 4px 16px rgba(17, 20, 24, 0.04);
      --tc-shadow-lg: 0 4px 24px rgba(17, 20, 24, 0.08);
    }}

    html, body, .stApp, [class*="css"] {{
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}

    {hide_sidebar}

    .stApp {{
      background-color: var(--tc-bg);
      background-image:
        radial-gradient(ellipse 120% 80% at 100% -20%, rgba(67, 56, 202, 0.07), transparent 50%),
        radial-gradient(ellipse 80% 60% at 0% 100%, rgba(59, 130, 246, 0.05), transparent 45%);
    }}

    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    div[data-testid="stDecoration"] {{ display: none; }}
    header[data-testid="stHeader"] {{ background: rgba(255,255,255,0.72) !important; backdrop-filter: blur(10px); border-bottom: 1px solid var(--tc-border); }}
    div[data-testid="stToolbar"] {{ visibility: hidden; }}

    .block-container {{
      padding-top: 1.5rem !important;
      padding-bottom: 4rem !important;
      max-width: 1200px !important;
    }}

    /* Bordered panels (st.container(border=True)) */
    [data-testid="stVerticalBlockBorderWrapper"] {{
      background: var(--tc-surface) !important;
      border: 1px solid var(--tc-border) !important;
      border-radius: var(--tc-radius) !important;
      box-shadow: var(--tc-shadow) !important;
      padding: 1.25rem 1.5rem !important;
      margin-bottom: 1.1rem !important;
    }}

    /* Dataframes & charts feel like cards */
    div[data-testid="stDataFrame"],
    div[data-testid="stVegaLiteChart"] {{
      border-radius: var(--tc-radius-sm) !important;
      border: 1px solid var(--tc-border) !important;
      overflow: hidden !important;
      background: var(--tc-surface) !important;
      box-shadow: 0 1px 2px rgba(17,20,24,0.04) !important;
    }}

    /* Alerts softer */
    div[data-baseweb="notification"] {{
      border-radius: var(--tc-radius-sm) !important;
    }}
    [data-testid="stExpander"] {{
      background: var(--tc-surface) !important;
      border: 1px solid var(--tc-border) !important;
      border-radius: var(--tc-radius-sm) !important;
      margin-bottom: 0.5rem !important;
    }}
    [data-testid="stExpander"] summary {{
      font-weight: 600 !important;
      font-size: 0.875rem !important;
    }}
    .stAlert {{
      border-radius: var(--tc-radius-sm) !important;
      border: 1px solid var(--tc-border) !important;
      background: #fafbff !important;
    }}

    /* Form controls */
    .stTextInput input, .stTextArea textarea {{
      border-radius: 10px !important;
      border-color: var(--tc-border) !important;
      font-size: 0.9375rem !important;
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{
      border-color: var(--tc-accent) !important;
      box-shadow: 0 0 0 3px var(--tc-accent-soft) !important;
    }}
    .stNumberInput input {{
      border-radius: 10px !important;
    }}
    .stSelectbox label, .stTextInput label, .stTextArea label, .stNumberInput label, .stSlider label {{
      font-size: 0.8125rem !important;
      font-weight: 600 !important;
      color: var(--tc-text) !important;
      text-transform: none !important;
    }}
    div[data-baseweb="select"] > div {{
      border-radius: 10px !important;
      border-color: var(--tc-border) !important;
    }}

    .stButton > button {{
      border-radius: 10px !important;
      font-weight: 600 !important;
      transition: transform 0.12s ease, box-shadow 0.12s ease !important;
    }}
    .stButton > button[kind="primary"] {{
      background: linear-gradient(180deg, #4f46e5 0%, #4338ca 100%) !important;
      border: none !important;
      box-shadow: 0 1px 2px rgba(67, 56, 202, 0.35) !important;
    }}
    .stButton > button[kind="primary"]:hover {{
      background: linear-gradient(180deg, #5558e3 0%, #4c3fd6 100%) !important;
      box-shadow: 0 2px 8px rgba(67, 56, 202, 0.35) !important;
    }}
    .stButton > button[kind="secondary"] {{
      border: 1px solid var(--tc-border) !important;
      background: #fff !important;
      color: var(--tc-text) !important;
    }}

    /* Captions on login */
    .stCaption {{
      color: var(--tc-soft) !important;
      letter-spacing: 0.02em;
    }}

    /* Page chrome */
    .pro-kicker {{
      font-size: 0.6875rem;
      font-weight: 700;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--tc-accent);
      margin: 0 0 0.35rem 0;
    }}
    .pro-page-title {{
      font-size: 1.875rem;
      font-weight: 700;
      color: var(--tc-text);
      letter-spacing: -0.03em;
      line-height: 1.2;
      margin: 0 0 0.4rem 0;
    }}
    .pro-page-sub {{
      font-size: 1rem;
      color: var(--tc-muted);
      margin: 0 0 1.5rem 0;
      line-height: 1.55;
      max-width: 52rem;
    }}

    .pro-poc {{
      font-size: 0.8125rem;
      color: var(--tc-muted);
      background: linear-gradient(90deg, var(--tc-accent-soft) 0%, #f8fafc 40%, #f8fafc 100%);
      border: 1px solid #e0e7ff;
      border-radius: var(--tc-radius-sm);
      padding: 0.65rem 1rem;
      margin: 0 0 1.5rem 0;
      border-left: 3px solid var(--tc-accent);
    }}

    .pro-section-title {{
      font-size: 0.8125rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--tc-muted);
      margin: 0 0 0.85rem 0;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid var(--tc-border);
    }}

    .pro-metric-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 1rem;
      margin-bottom: 1.25rem;
    }}
    @media (max-width: 1100px) {{
      .pro-metric-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    }}
    @media (max-width: 700px) {{
      .pro-metric-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    .pro-metric {{
      background: var(--tc-surface);
      border: 1px solid var(--tc-border);
      border-radius: var(--tc-radius);
      padding: 1.15rem 1.25rem;
      box-shadow: var(--tc-shadow);
      position: relative;
      overflow: hidden;
    }}
    .pro-metric::before {{
      content: "";
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--tc-accent), #6366f1);
      opacity: 0.85;
    }}
    .pro-metric-label {{
      font-size: 0.6875rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--tc-soft);
      margin: 0.35rem 0 0.4rem 0;
    }}
    .pro-metric-value {{
      font-size: 1.75rem;
      font-weight: 700;
      color: var(--tc-text);
      letter-spacing: -0.02em;
      line-height: 1.1;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
      background: linear-gradient(175deg, #0c1022 0%, #151832 48%, #0f111c 100%) !important;
      border-right: 1px solid rgba(255,255,255,0.06) !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
      background: transparent !important;
    }}
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
      color: #e8eaed !important;
    }}
    [data-testid="stSidebar"] .stRadio label {{
      font-size: 0.875rem !important;
      font-weight: 500 !important;
      padding: 0.5rem 0.65rem !important;
      margin: 0.1rem 0 !important;
      border-radius: 10px !important;
      transition: background 0.15s ease !important;
    }}
    [data-testid="stSidebar"] .stRadio label:hover {{
      background: rgba(255,255,255,0.06) !important;
    }}
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {{
      background: rgba(99, 102, 241, 0.35) !important;
      color: #fff !important;
      font-weight: 600 !important;
    }}
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{
      gap: 0.15rem;
    }}
    [data-testid="stSidebar"] hr {{
      border-color: rgba(255,255,255,0.08);
    }}

    .nav-brand {{
      padding: 0.5rem 0 1.1rem 0;
      border-bottom: 1px solid rgba(255,255,255,0.08);
      margin-bottom: 1rem;
    }}
    .nav-brand-badge {{
      display: inline-block;
      font-size: 0.625rem;
      font-weight: 700;
      letter-spacing: 0.12em;
      color: #a5b4fc;
      background: rgba(99, 102, 241, 0.2);
      padding: 0.25rem 0.5rem;
      border-radius: 6px;
      margin-bottom: 0.5rem;
    }}
    .nav-brand-title {{
      font-size: 1.125rem;
      font-weight: 700;
      color: #fff !important;
      letter-spacing: -0.02em;
      line-height: 1.25;
    }}
    .nav-brand-sub {{
      font-size: 0.75rem;
      color: #9ca3af !important;
      margin-top: 0.35rem;
      line-height: 1.4;
    }}
    .nav-user {{
      font-size: 0.8125rem;
      color: #c7cad1 !important;
      background: rgba(255,255,255,0.05);
      border-radius: 12px;
      padding: 0.75rem 0.85rem;
      margin: 0.75rem 0 1rem 0;
      border: 1px solid rgba(255,255,255,0.08);
      line-height: 1.45;
    }}

    /* Login hero */
    .login-hero {{
      padding: 2rem 1.5rem 2rem 0;
    }}
    .login-hero h2 {{
      font-size: 2rem;
      font-weight: 700;
      color: var(--tc-text);
      letter-spacing: -0.03em;
      line-height: 1.15;
      margin: 0 0 1rem 0;
    }}
    .login-hero p {{
      font-size: 1rem;
      color: var(--tc-muted);
      line-height: 1.6;
      margin: 0 0 1.5rem 0;
    }}
    .login-hero ul {{
      list-style: none;
      padding: 0;
      margin: 0;
    }}
    .login-hero li {{
      font-size: 0.9375rem;
      color: var(--tc-text);
      padding: 0.5rem 0;
      padding-left: 1.5rem;
      position: relative;
    }}
    .login-hero li::before {{
      content: "";
      position: absolute;
      left: 0;
      top: 0.85rem;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--tc-accent);
    }}
    .login-card-title {{
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--tc-text);
      margin: 0 0 0.35rem 0;
    }}
    .login-card-sub {{
      font-size: 0.875rem;
      color: var(--tc-muted);
      margin: 0 0 1.25rem 0;
      line-height: 1.5;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def page_header(title: str, subtitle: str | None = None, *, kicker: str | None = None) -> None:
    esc_title = html.escape(title)
    esc_sub = html.escape(subtitle) if subtitle else ""
    kick = f'<div class="pro-kicker">{html.escape(kicker)}</div>' if kicker else ""
    sub = f'<p class="pro-page-sub">{esc_sub}</p>' if subtitle else ""
    st.markdown(
        f'{kick}<div class="pro-page-title">{esc_title}</div>{sub}',
        unsafe_allow_html=True,
    )


def section_heading(title: str) -> None:
    st.markdown(f'<div class="pro-section-title">{html.escape(title)}</div>', unsafe_allow_html=True)


def poc_note() -> None:
    st.markdown(
        '<div class="pro-poc">Academic proof of concept — not a production HR system. '
        "AI outputs are simulated; approvals, compensation, and compliance remain human-owned.</div>",
        unsafe_allow_html=True,
    )


def metrics_row(stats: dict) -> None:
    items = [
        ("Open roles", stats["open_jobs"]),
        ("Candidates", stats["total_candidates"]),
        ("Shortlisted", stats["shortlisted"]),
        ("Interviews", stats["interviews"]),
        ("Offers", stats["offers"]),
    ]
    parts = []
    for label, val in items:
        parts.append(
            f'<div class="pro-metric"><div class="pro-metric-label">{html.escape(label)}</div>'
            f'<div class="pro-metric-value">{html.escape(str(val))}</div></div>'
        )
    st.markdown(f'<div class="pro-metric-grid">{"".join(parts)}</div>', unsafe_allow_html=True)


def sidebar_brand() -> None:
    st.sidebar.markdown(
        '<div class="nav-brand">'
        '<span class="nav-brand-badge">INTERNAL DEMO</span>'
        '<div class="nav-brand-title">HireFlow AI</div>'
        '<div class="nav-brand-sub">Agent-assisted recruiting & onboarding</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def sidebar_user_block(role: str) -> None:
    st.sidebar.markdown(
        '<div class="nav-user">Active profile<br/>'
        f'<strong style="color:#f9fafb;font-size:0.95rem;">{html.escape(role)}</strong></div>',
        unsafe_allow_html=True,
    )


def login_hero_column() -> None:
    st.markdown(
        """
        <div class="login-hero">
          <h2>Hiring, orchestrated.</h2>
          <p>One workspace for requisitions, screening, interviews, offers, and onboarding — with AI drafts and human approval at every gate.</p>
          <ul>
            <li>Role-scoped navigation like a production HRIS</li>
            <li>Mock agents — no API keys required</li>
            <li>SQLite persistence for class demos</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def login_card_headers() -> None:
    st.markdown(
        '<p class="login-card-title">Sign in</p>'
        '<p class="login-card-sub">Choose your profile. No password in this demo — menus and actions follow typical enterprise boundaries.</p>',
        unsafe_allow_html=True,
    )
