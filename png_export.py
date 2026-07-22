"""
PNG export for the Day Archive dashboard.

Renders the 5-page pack (transparent PNGs) for the orders held in
st.session_state.processed_orders, and offers them as a zip download.

Key behaviour:
- The rendered zip is cached in st.session_state, so clicking the download
  button (which triggers a Streamlit rerun) never re-renders the packs.
- The zip is built on disk, not in memory, to keep peak RAM low on large
  batches (29 orders = 145 large PNGs).

Drop this file in the repo root next to dashboard_v3.py, then call:
    from png_export import render_png_section
    render_png_section(st.session_state.processed_orders)
"""

import gc
import os
import zipfile
import tempfile

import streamlit as st

from render_pack import render_pack

# Above this many orders, warn that it's a long job.
LARGE_BATCH = 15


def _rerun():
    """st.rerun() on modern Streamlit, experimental_rerun() on older."""
    fn = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if fn:
        fn()


def _orders_signature(processed_orders):
    """Cheap fingerprint so we know if the cached zip matches these orders."""
    return (
        len(processed_orders),
        tuple(
            (o.get("OrderID", ""), o.get("Name", ""))
            for o in processed_orders[:50]
        ),
    )


def render_png_section(processed_orders):
    """Render a 'Print PNGs' section for the processed orders."""
    if not processed_orders:
        return

    total = len(processed_orders)
    sig = _orders_signature(processed_orders)

    st.markdown("---")
    st.subheader("🖼️ Print PNGs")
    st.caption(
        f"Generates 5 transparent A4 @ 300dpi PNGs per pack "
        f"({total} pack(s) = {total * 5} files)."
    )

    if total > LARGE_BATCH:
        st.info(
            f"{total} packs is a large batch ({total * 5} images). "
            "Generating may take a few minutes - leave the tab open. "
            "If it stalls, process fewer orders at a time."
        )

    # ---- Cached result: show the download button without re-rendering ----
    cached = st.session_state.get("png_zip_data")
    cached_sig = st.session_state.get("png_zip_sig")

    if cached is not None and cached_sig == sig:
        size_mb = len(cached) / (1024 * 1024)
        st.success(
            f"{st.session_state.get('png_zip_count', 0)} PNGs ready "
            f"({size_mb:.1f} MB)."
        )
        st.download_button(
            label="📦 Download all PNGs (zip)",
            data=cached,
            file_name="day_archive_packs.zip",
            mime="application/zip",
            key="png_zip_download",
        )
        if st.button("🔄 Clear and regenerate", key="png_zip_clear"):
            for k in ("png_zip_data", "png_zip_sig", "png_zip_count"):
                st.session_state.pop(k, None)
            gc.collect()
            _rerun()
        return

    # ---- Generate ----
    if st.button("🎨 Generate Print PNGs", type="primary", key="png_generate"):
        progress = st.progress(0.0)
        status = st.empty()

        out_dir = tempfile.mkdtemp(prefix="dayarchive_png_")
        zip_path = os.path.join(out_dir, "day_archive_packs.zip")
        count = 0

        try:
            # Stream each pack straight into the zip on disk, then delete the
            # PNGs, so we never hold 145 large images (or an 80MB buffer)
            # in memory at once.
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
                for i, order in enumerate(processed_orders, start=1):
                    name = order.get("Name", "")
                    status.markdown(f"**Rendering {i} of {total}** - {name}")

                    paths = render_pack(order, out_dir)
                    for p in paths:
                        z.write(p, os.path.basename(p))
                        os.remove(p)          # free disk immediately
                        count += 1

                    progress.progress(i / total)
                    if i % 5 == 0:
                        gc.collect()          # keep peak memory down

            with open(zip_path, "rb") as f:
                zip_bytes = f.read()

            # cache so the download click doesn't re-render everything
            st.session_state["png_zip_data"] = zip_bytes
            st.session_state["png_zip_sig"] = sig
            st.session_state["png_zip_count"] = count

            status.markdown("**All PNGs rendered**")
            progress.progress(1.0)

        except Exception as e:
            st.error(f"Error rendering PNGs: {e}")
            st.exception(e)
            return
        finally:
            try:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                os.rmdir(out_dir)
            except OSError:
                pass
            gc.collect()

        _rerun()   # show the cached download button
