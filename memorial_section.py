"""
Streamlit UI for the Memorial pack ("The Day You Passed").

Two modes:
  • Manual entry   — type a name + two dates, generate one pack.
  • From Shopify    — auto-detect unfulfilled "The Day You Passed Archive" orders
                      (reads Full Name / Date of Birth / Date of Passing) and
                      batch-generate them.

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
from memorial_shopify import fetch_unfulfilled_orders, extract_memorial_orders


def _get_api_key():
    ss = st.session_state
    for src in ((ss.get("api_credentials") or {}).get("claude_api_key"),
                ss.get("claude_api_key"),
                (ss.get("settings") or {}).get("claude_api_key"),
                os.environ.get("CLAUDE_API_KEY"), os.environ.get("ANTHROPIC_API_KEY")):
        if src:
            return src
    return ""


def _render_one(name, dob, dop, api_key, out_dir, order_id="", express=False,
                item_index=0, item_count=1, progress=None):
    """Research + render one pack into out_dir; returns (paths, warnings)."""
    tokens, warnings = build_pack_data(name, dob, dop, api_key, progress=progress)
    oid = order_id
    if item_count > 1:
        oid = f"{order_id} (Item {item_index + 1} of {item_count})"
    disp_name = f"{name} (EXPRESS)" if express else name
    paths = render_memorial_pack(tokens, out_dir, order_id=oid.strip(), name=disp_name)
    return paths, warnings


def _zip_bytes(paths):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))
    buf.seek(0)
    return buf.getvalue()


def render_memorial_section():
    st.header("🕊️ Memorial Pack — On the Day You Passed")

    # rendering engine must be present (packages.txt 'chromium' on Streamlit Cloud)
    try:
        find_chrome()
    except Exception as e:
        st.error(f"Rendering engine unavailable: {e}")
        st.info("Add a repo-root **packages.txt** containing a single line `chromium`, then redeploy.")
        return

    api_key = _get_api_key()
    mode = st.radio("Source", ["From Shopify orders", "Manual entry"], horizontal=True)

    # =====================================================================
    # SHOPIFY MODE
    # =====================================================================
    if mode == "From Shopify orders":
        creds = st.session_state.get("api_credentials") or {}
        store, token = creds.get("shopify_store", ""), creds.get("shopify_token", "")
        if not (store and token):
            st.warning("Add your Shopify store + token in the sidebar (⚙️ Controls) first.")
            return

        if st.button("🔄 Load unfulfilled memorial orders", type="primary"):
            try:
                with st.spinner("Fetching from Shopify…"):
                    orders = fetch_unfulfilled_orders(token, store)
                    st.session_state.memorial_items = extract_memorial_orders(orders)
            except Exception as e:
                st.error(f"Could not fetch orders: {e}")
                return

        items = st.session_state.get("memorial_items")
        if items is None:
            st.caption('Click "Load" to find "The Day You Passed Archive" orders awaiting fulfilment.')
            return
        if not items:
            st.info("No unfulfilled memorial orders found.")
            return

        st.success(f"{len(items)} memorial order(s) ready.")
        st.dataframe(
            [{"Order": it["order_name"], "Name": it["name"], "Born": it["dob"],
              "Passed": it["dop"], "Express": "✓" if it["express"] else ""}
             for it in items],
            use_container_width=True, hide_index=True,
        )

        if not api_key:
            st.error("A Claude API key is required (set it in the sidebar).")
            return

        if st.button(f"🎨 Generate all {len(items)} pack(s)", type="primary"):
            out_dir = tempfile.mkdtemp(prefix="memorial_batch_")
            all_paths, errors = [], []
            prog = st.progress(0.0)
            status = st.empty()
            for n, it in enumerate(items, start=1):
                status.markdown(f"**{n}/{len(items)}** — {it['name'] or it['order_name']}")
                try:
                    paths, warns = _render_one(
                        it["name"], it["dob"], it["dop"], api_key, out_dir,
                        order_id=it["order_name"], express=it["express"],
                        item_index=it["item_index"], item_count=it["item_count"],
                        progress=lambda m: status.caption(m))
                    all_paths.extend(paths)
                    for w in warns:
                        st.warning(f"{it['order_name']}: {w}")
                except Exception as e:
                    errors.append(f"{it['order_name']} ({it['name']}): {e}")
                prog.progress(n / len(items))
                if n % 3 == 0:
                    gc.collect()
            status.empty()
            if all_paths:
                st.success(f"Rendered {len(all_paths)} PNG(s) for {len(items) - len(errors)} order(s).")
                st.download_button("📦 Download all packs (zip)", data=_zip_bytes(all_paths),
                                   file_name="memorial_packs.zip", mime="application/zip",
                                   key="memorial_batch_zip")
            for err in errors:
                st.error(err)
            gc.collect()
        return

    # =====================================================================
    # MANUAL MODE
    # =====================================================================
    today = datetime.date.today()
    with st.form("memorial_manual"):
        name = st.text_input("Full name of the person", placeholder="Margaret Rose Whelan")
        c1, c2 = st.columns(2)
        dob = c1.date_input("Date of birth", value=datetime.date(1940, 1, 1),
                            min_value=datetime.date(1900, 1, 1), max_value=today, format="DD/MM/YYYY")
        dop = c2.date_input("Date of passing", value=today,
                            min_value=datetime.date(1900, 1, 1), max_value=today, format="DD/MM/YYYY")
        key_in = st.text_input("Claude API key", value=api_key, type="password")
        order_id = st.text_input("Order number (optional)", placeholder="#1234")
        submitted = st.form_submit_button("🎨 Generate memorial pack", type="primary")

    if not submitted:
        return
    if not name.strip():
        st.error("Please enter a name."); return
    if not key_in.strip():
        st.error("A Claude API key is required."); return
    if dop <= dob:
        st.error("Date of passing must be after the date of birth."); return

    status = st.empty()
    try:
        out_dir = tempfile.mkdtemp(prefix="memorial_")
        paths, warnings = _render_one(name, dob, dop, key_in, out_dir,
                                      order_id=order_id.strip(),
                                      progress=lambda m: status.info(m))
    except Exception as e:
        status.empty()
        st.error(f"Could not generate the pack: {e}")
        return
    status.success("✅ Memorial pack ready.")
    for w in warnings:
        st.warning(w)
    st.download_button("📦 Download pack (zip)", data=_zip_bytes(paths),
                       file_name=f"memorial_{name.strip().replace(' ', '_')}.zip",
                       mime="application/zip", key="memorial_manual_zip")
    cols = st.columns(5)
    for i, p in enumerate(paths):
        with cols[i]:
            st.image(p, caption=f"Page {i + 1}", use_container_width=True)
    gc.collect()
