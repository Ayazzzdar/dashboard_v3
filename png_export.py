"""
PNG export for the Day Archive dashboard.

Renders the 5-page pack (transparent PNGs) for the orders held in
st.session_state.processed_orders, and offers them as a zip download.

Drop this file in the repo root next to dashboard_v3.py, then in
dashboard_v3.py (right after the CSV download button) add:

    from png_export import render_png_section
    render_png_section(st.session_state.processed_orders)
"""

import io
import os
import zipfile
import tempfile

import streamlit as st

from render_pack import render_pack, build_filename


def render_png_section(processed_orders):
    """Render a 'Generate Print PNGs' section for the processed orders."""
    if not processed_orders:
        return

    st.markdown("---")
    st.subheader("🖼️ Print PNGs (transparent, ready for Officeworks)")
    st.caption(
        f"Generates 5 transparent A4 @ 300dpi PNGs per pack "
        f"({len(processed_orders)} pack(s) = {len(processed_orders) * 5} files)."
    )

    if st.button("🎨 Generate Print PNGs", type="primary"):
        progress = st.progress(0.0)
        status = st.empty()
        total = len(processed_orders)

        # render everything into a fresh temp dir
        out_dir = tempfile.mkdtemp(prefix="dayarchive_png_")
        all_paths = []
        try:
            for i, order in enumerate(processed_orders, start=1):
                name = order.get("Name", "")
                status.markdown(f"**Rendering {i} of {total}** — {name}")
                paths = render_pack(order, out_dir)
                all_paths.extend(paths)
                progress.progress(i / total)

            status.markdown("**✅ All PNGs rendered**")

            # bundle into a single zip for download
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                for p in all_paths:
                    z.write(p, os.path.basename(p))
            buf.seek(0)

            st.success(f"Generated {len(all_paths)} PNGs across {total} pack(s).")
            st.download_button(
                label="📦 Download all PNGs (zip)",
                data=buf.getvalue(),
                file_name="day_archive_packs.zip",
                mime="application/zip",
            )

            # also show a preview of page 1 of the first order
            with st.expander("👁️ Preview (page 1 of first pack)"):
                first_p1 = all_paths[0]
                st.image(first_p1, caption=os.path.basename(first_p1), width=350)

        except Exception as e:
            st.error(f"Error rendering PNGs: {e}")
            st.exception(e)
