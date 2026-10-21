"""
Streamlit UI for the Memorial pack ("The Day You Passed").

Manual-entry first: enter a name, date of birth and date of passing, generate the
5-page pack (research + render), preview it, and download a zip. Shopify
auto-detection can be wired in later via the same build_pack_data/render calls.

Wire into dashboard_v3.py with:
    from memorial_section import render_memorial_section
    with memorial_tab:
        render_memorial_section()
"""

import os
import io
import gc
import zipfile
import datetime
import tempfile

import streamlit as st

from memorial_research import build_pack_data
from memorial_render import render_memorial_pack, find_chrome


def _get_api_key():
    """Best-effort fetch of the Claude API key already used elsewhere in the app."""
    ss = st.session_state
    for src in ((ss.get("api_credentials") or {}).get("claude_api_key"),
                ss.get("claude_api_key"),
                (ss.get("settings") or {}).get("claude_api_key"),
                (ss.get("settings") or {}).get("api_key"),
                os.environ.get("CLAUDE_API_KEY"), os.environ.get("ANTHROPIC_API_KEY")):
        if src:
            return src
    return ""


def render_memorial_section():
    st.header("🕊️ Memorial Pack — On the Day You Passed")
    st.caption("A 5-page memorial keepsake. Enter a name and two dates; everything else "
               "is researched and rendered automatically.")

    # chromium availability check (needs packages.txt 'chromium' on Streamlit Cloud)
    try:
        find_chrome()
    except Exception as e:
        st.error(f"Rendering engine unavailable: {e}")
        st.info("Add a file named **packages.txt** to the repo root containing a single "
                "line: `chromium` — then redeploy.")
        return

    today = datetime.date.today()
    with st.form("memorial_form"):
        name = st.text_input("Full name of the person", placeholder="Margaret Rose Whelan")
        c1, c2 = st.columns(2)
        dob = c1.date_input("Date of birth", value=datetime.date(1940, 1, 1),
                            min_value=datetime.date(1900, 1, 1), max_value=today, format="DD/MM/YYYY")
        dop = c2.date_input("Date of passing", value=today,
                            min_value=datetime.date(1900, 1, 1), max_value=today, format="DD/MM/YYYY")
        api_key = st.text_input("Claude API key", value=_get_api_key(), type="password",
                                help="Used to research the day of passing.")
        order_id = st.text_input("Order number (optional)", placeholder="#1234",
                                 help="Added to the PNG filenames, like the birthday pack.")
        submitted = st.form_submit_button("🎨 Generate memorial pack", type="primary")

    if not submitted:
        return

    # ---- validate ----
    if not name.strip():
        st.error("Please enter a name."); return
    if not api_key.strip():
        st.error("A Claude API key is required to research the pack."); return
    if dop <= dob:
        st.error("Date of passing must be after the date of birth."); return

    status = st.empty()
    try:
        status.info("🔍 Researching the day of passing…")
        tokens, warnings = build_pack_data(name, dob, dop, api_key,
                                           progress=lambda m: status.info(m))
        for w in warnings:
            st.warning(w)
        status.info("🖼️ Rendering 5 pages…")
        out_dir = tempfile.mkdtemp(prefix="memorial_")
        paths = render_memorial_pack(tokens, out_dir, order_id=order_id.strip(), name=name)
    except Exception as e:
        status.empty()
        st.error(f"Could not generate the pack: {e}")
        st.exception(e)
        return

    status.success("✅ Memorial pack ready.")

    # ---- zip for download ----
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    buf.seek(0)
    zip_name = f"memorial_{name.strip().replace(' ', '_')}.zip"
    st.download_button("📦 Download pack (zip)", data=buf.getvalue(), file_name=zip_name,
                       mime="application/zip", key="memorial_zip")

    # ---- preview ----
    st.markdown("**Preview**")
    cols = st.columns(5)
    for i, p in enumerate(paths):
        with cols[i]:
            st.image(p, caption=f"Page {i + 1}", use_container_width=True)

    gc.collect()
