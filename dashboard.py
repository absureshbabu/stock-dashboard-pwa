"""dashboard.py — Mobile Streamlit app. Reads from GitHub (raw JSON).

Run locally: streamlit run dashboard.py
Deploy: push to GitHub, connect to Streamlit Community Cloud.
No secrets required — reads from public GitHub raw URL.
Optional secrets (Streamlit Cloud → Settings → Secrets):
  GITHUB_REPO   = "absureshbabu/stock-dashboard-pwa"   # override if needed
  GITHUB_BRANCH = "main"
"""
import json
import urllib.request
import urllib.error
import streamlit as st
from datetime import datetime, timezone

st.set_page_config(
    page_title="Stock Terminal",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── GitHub raw URL config ─────────────────────────────────────────────────────
_repo   = st.secrets.get("GITHUB_REPO",   "absureshbabu/stock-dashboard-pwa") if hasattr(st, "secrets") else "absureshbabu/stock-dashboard-pwa"
_branch = st.secrets.get("GITHUB_BRANCH", "main") if hasattr(st, "secrets") else "main"
_BASE   = f"https://raw.githubusercontent.com/{_repo}/{_branch}/data"

SNAPSHOT_URL     = f"{_BASE}/snapshot.json"
TICKER_LOOKUP_URL = f"{_BASE}/ticker_lookup.json"


# ── Data loaders ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def _load_snapshot() -> dict:
    try:
        with urllib.request.urlopen(SNAPSHOT_URL, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        st.error(f"Could not load snapshot from GitHub: {e}")
        return {}


@st.cache_data(ttl=300)
def _load_ticker_lookup() -> list:
    try:
        with urllib.request.urlopen(TICKER_LOOKUP_URL, timeout=10) as r:
            return json.loads(r.read())
    except Exception:
        return []


def _lookup_ticker(ticker: str) -> list:
    rows = _load_ticker_lookup()
    t = ticker.upper()
    return [r for r in rows if (r.get("ticker") or "").upper() == t]


# ── Formatting helpers ────────────────────────────────────────────────────────

def _signal_icon(sig: str) -> str:
    s = (sig or "").upper()
    if "MUST"     in s: return "🔥"
    if "STRONG B" in s: return "🟢"
    if "BUY"      in s: return "🟢"
    if "HOLD"     in s: return "🟡"
    if "STRONG S" in s: return "🔴"
    return "🔴"


def _p(v) -> str:
    if v is None or v == "": return "—"
    if isinstance(v, (int, float)): return f"₹{v:,.0f}"
    return str(v)


def _pct(v) -> str:
    try:
        f = float(v)
        sign = "▲" if f >= 0 else "▼"
        return f"{sign}{abs(f):.2f}%"
    except (TypeError, ValueError):
        return ""


def _levels(item: dict) -> str:
    parts = []
    for key, label in [("t1", "T1"), ("t2", "T2"), ("r1", "R1"), ("s1", "S1")]:
        v = item.get(key)
        if v:
            parts.append(f"{label} {_p(v)}")
    return " · ".join(parts)


def _llm_levels(item: dict) -> str:
    parts = []
    for key, label in [("llm_support", "S"), ("llm_resistance", "R"), ("llm_target", "T")]:
        v = item.get(key)
        if v:
            try:
                parts.append(f"{label} {_p(float(v))}")
            except (TypeError, ValueError):
                pass
    return " · ".join(parts)


# ── Main app ──────────────────────────────────────────────────────────────────

def main():
    # snapshot.json IS the snap dict (no nested .snapshot key)
    snap = _load_snapshot()
    if not snap:
        return

    synced_at = snap.get("synced_at") or ""
    try:
        dt = datetime.fromisoformat(synced_at.replace("Z", "+00:00"))
        age_m = int((datetime.now(timezone.utc) - dt).total_seconds() // 60)
        age_str = f"{age_m}m ago" if age_m < 60 else f"{age_m // 60}h ago"
    except Exception:
        age_str = synced_at[:16] if synced_at else "—"
    st.caption(f"✓ Last updated {age_str}")

    tabs = st.tabs(["Overview", "Buy Signals", "Results", "In Focus", "Sector", "Lookup", "Screener"])

    # ── Overview ──────────────────────────────────────────────────────────────
    with tabs[0]:
        ov          = snap.get("overview") or {}
        mb          = snap.get("model_bar") or {}
        buy_signals = snap.get("buy_signals") or []

        col1, col2 = st.columns(2)
        nifty  = ov.get("nifty_close")
        sensex = ov.get("sensex_close")
        col1.metric("NIFTY 50",
            _p(nifty) if nifty else "—",
            _pct(ov.get("nifty_pct")) if ov.get("nifty_pct") is not None else None)
        col2.metric("SENSEX",
            _p(sensex) if sensex else "—",
            _pct(ov.get("sensex_pct")) if ov.get("sensex_pct") is not None else None)
        if ov.get("india_vix"):
            try:
                st.caption(f"India VIX: {float(ov['india_vix']):.1f}")
            except (TypeError, ValueError):
                st.caption(f"India VIX: {ov['india_vix']}")

        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Win Rate",  f"{mb.get('current_win_rate', '—')}%")
        m2.metric("Precision", f"{mb.get('precision', '—')}%")
        m3.metric("Samples",   mb.get("n_samples", "—"))

        auc   = mb.get("cv_roc_auc")
        brier = mb.get("brier_score")
        brier_n = mb.get("brier_n")
        if auc or brier:
            a1, a2 = st.columns(2)
            if auc:
                a1.metric("AUC (CV)", f"{auc:.1f}%",
                          help="ROC-AUC from time-series cross-validation. 50%=random, higher=better.")
            if brier is not None:
                a2.metric("Brier Score", f"{brier:.4f}",
                          help=f"Brier score on {brier_n} OOF rows. 0.25=random, lower=better.")

        st.divider()
        must_ct = sum(1 for s in buy_signals if "MUST" in (s.get("signal") or "").upper())
        buy_ct  = len(buy_signals) - must_ct
        c1, c2 = st.columns(2)
        c1.error(f"🔥 {must_ct} MUST BUY")
        c2.success(f"✓ {buy_ct} BUY")

    # ── Buy Signals ───────────────────────────────────────────────────────────
    with tabs[1]:
        signals = snap.get("buy_signals") or []
        if not signals:
            st.info("No buy signals in last snapshot.")
        for s in signals:
            is_must = "MUST" in (s.get("signal") or "").upper()
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    badge  = "🔥 MUST BUY" if is_must else "🟢 BUY"
                    sector = s.get("sector") or s.get("sec") or ""
                    name   = s.get("name") or ""
                    st.markdown(f"**{s.get('ticker','?')}** `{badge}`")
                    st.caption(f"{name[:25]} · {sector}")

                    price = _p(s.get("price"))
                    chg   = _pct(s.get("change_pct")) if s.get("change_pct") is not None else ""
                    st.caption(f"{price} {chg}")

                    entry = s.get("entry") or "—"
                    sl    = s.get("sl") or "—"
                    st.caption(f"Entry {entry} · SL {sl}")

                    lvl = _levels(s)
                    if lvl:
                        st.caption(lvl)

                    llm_lvl = _llm_levels(s)
                    if llm_lvl:
                        st.caption(f"🤖 {llm_lvl}")

                    extras = []
                    if s.get("win"):      extras.append(f"Win {s['win']}%")
                    if s.get("risk"):     extras.append(f"Risk {s['risk']}%")
                    if s.get("pe_ratio"): extras.append(f"PE {s['pe_ratio']}")
                    if s.get("pb_ratio"): extras.append(f"PB {s['pb_ratio']}")
                    if extras:
                        st.caption(" · ".join(extras))

                with col2:
                    display_score = s.get("adjusted_score") or s.get("ml") or "—"
                    st.metric("Score", display_score)
                    if s.get("llm_confidence"):
                        st.caption(f"LLM: {s['llm_confidence']}")

                risk_flags  = s.get("llm_risk_flags") or []
                green_flags = s.get("llm_green_flags") or []
                if risk_flags:
                    st.markdown(" ".join(f"🔴 `{f}`" for f in risk_flags))
                if green_flags:
                    st.markdown(" ".join(f"🟢 `{f}`" for f in green_flags))
                if s.get("llm_doc_narrative"):
                    with st.expander("Analyst view"):
                        st.caption(s["llm_doc_narrative"])

    # ── Results ───────────────────────────────────────────────────────────────
    with tabs[2]:
        results    = snap.get("results") or []
        all_sigs   = sorted({(r.get("signal") or "—") for r in results})
        sig_filter = st.selectbox("Filter", ["All"] + all_sigs, key="rf")
        shown = results if sig_filter == "All" else [
            r for r in results if r.get("signal") == sig_filter
        ]
        st.caption(f"{len(shown)} of {len(results)} results")
        for r in shown:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    icon     = _signal_icon(r.get("signal"))
                    ticker   = r.get("ticker", "?")
                    name     = (r.get("name") or "")[:22]
                    quarter  = r.get("quarter") or ""
                    ann_type = r.get("type") or ""
                    st.markdown(f"{icon} **{ticker}** · {name}")
                    st.caption(f"{quarter}  {ann_type}".strip())

                    sig     = r.get("signal") or "—"
                    verdict = r.get("verdict") or ""
                    st.caption(f"{sig}" + (f" · {verdict[:40]}" if verdict else ""))

                    price = _p(r.get("price")) if r.get("price") else ""
                    chg   = _pct(r.get("change_pct")) if r.get("change_pct") is not None else ""
                    if price:
                        entry = r.get("entry") or "—"
                        sl    = r.get("sl") or "—"
                        st.caption(f"{price} {chg} · Entry {entry} · SL {sl}")

                    lvl = _levels(r)
                    if lvl:
                        st.caption(lvl)

                    llm_lvl = _llm_levels(r)
                    if llm_lvl:
                        st.caption(f"🤖 {llm_lvl}")

                with col2:
                    st.metric("Score", r.get("ml") or r.get("win") or "—")
                    if r.get("llm_confidence"):
                        st.caption(f"LLM: {r['llm_confidence']}")
                    if r.get("result_ml") is not None:
                        st.caption(f"R: {r['result_ml']}")
                    if r.get("risk"):
                        st.caption(f"Risk {r['risk']}%")
                    if r.get("pe_ratio"):
                        st.caption(f"PE {r['pe_ratio']}")
                    if r.get("pb_ratio"):
                        st.caption(f"PB {r['pb_ratio']}")

            risk_flags  = r.get("llm_risk_flags") or []
            green_flags = r.get("llm_green_flags") or []
            if risk_flags or green_flags:
                flags_str = " ".join(f"🔴`{f}`" for f in risk_flags) + " " + " ".join(f"🟢`{f}`" for f in green_flags)
                st.caption(flags_str.strip())
            if r.get("llm_doc_narrative"):
                with st.expander("Analyst view"):
                    st.caption(r["llm_doc_narrative"])

    # ── In Focus ──────────────────────────────────────────────────────────────
    with tabs[3]:
        focus = snap.get("in_focus") or []
        if not focus:
            st.info("No in-focus stocks.")
        for f in focus:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    price  = _p(f.get("price"))
                    chg    = _pct(f.get("change_pct")) if f.get("change_pct") is not None else ""
                    sector = f.get("sector") or ""
                    st.markdown(f"**{f.get('ticker','?')}** · {price} {chg}")
                    st.caption(sector)

                    verdict = f.get("verdict") or f.get("tag") or ""
                    if verdict:
                        st.caption(verdict[:50])

                    entry = f.get("entry") or "—"
                    sl    = f.get("sl") or "—"
                    st.caption(f"Entry {entry} · SL {sl}")

                    lvl = _levels(f)
                    if lvl:
                        st.caption(lvl)

                with col2:
                    st.metric("Score", f.get("score") or "—")
                    if f.get("win"):      st.caption(f"Win {f['win']}%")
                    if f.get("pe_ratio"): st.caption(f"PE {f['pe_ratio']}")
                    if f.get("pb_ratio"): st.caption(f"PB {f['pb_ratio']}")

    # ── Sector ────────────────────────────────────────────────────────────────
    with tabs[4]:
        sf    = snap.get("sector_forecast") or {}
        buys  = sf.get("buys") or []
        sells = sf.get("sells") or []
        st.caption(f"Sector run: {sf.get('run_date', '—')}")
        for b in buys:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    price = _p(b.get("price"))
                    st.markdown(f"**{b.get('ticker','?')}** · {b.get('sector','')}")
                    rec = b.get("rec") or "—"
                    st.caption(f"{rec} · {price}")

                    entry = b.get("entry") or "—"
                    sl    = b.get("sl") or "—"
                    st.caption(f"Entry {entry} · SL {sl}")

                    lvl = _levels(b)
                    if lvl:
                        st.caption(lvl)

                with col2:
                    st.metric("Score", b.get("score") or "—")
        if sells:
            with st.expander(f"Sells ({len(sells)})"):
                for s in sells:
                    price = _p(s.get("price"))
                    entry = s.get("entry") or "—"
                    sl    = s.get("sl") or "—"
                    st.markdown(f"**{s.get('ticker','?')}** · {s.get('sector','')} · {s.get('rec','—')}")
                    st.caption(f"{price} · Entry {entry} · SL {sl}")
                    lvl = _levels(s)
                    if lvl:
                        st.caption(lvl)

    # ── Lookup ────────────────────────────────────────────────────────────────
    with tabs[5]:
        st.caption("Search any ticker from last retrain. Not live.")
        query = st.text_input("Ticker", placeholder="e.g. RELIANCE").strip().upper()
        if query:
            rows = _lookup_ticker(query)
            if rows:
                r = rows[0]
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{r.get('ticker','?')}** · {r.get('name','')}")
                        st.caption(f"Entry: {r.get('entry') or '—'} · SL: {r.get('sl') or '—'}")
                        if r.get("win_context"):
                            st.caption(r["win_context"])
                    with col2:
                        st.metric("Score", r.get("score") or "—")
                        st.caption(r.get("signal") or "—")
            else:
                st.info(f"No data for **{query}** in last retrain.")

    # ── Screener ──────────────────────────────────────────────────────────────
    with tabs[6]:
        screener_snap    = snap.get("screener") or {}
        screener_results = screener_snap.get("results") or []

        mode_filter = st.radio("Mode", ["general", "pre-run"], horizontal=True, key="sc_mode")
        filtered = [r for r in screener_results if r.get("mode") == mode_filter]

        st.caption(f"{len(filtered)} picks · {screener_snap.get('date','—')}")

        if not filtered:
            st.info(f"No screener results for '{mode_filter}' today. Check after 8:30 AM.")
        else:
            for r in filtered:
                conviction = r.get("conviction", "MEDIUM")
                icon = "🔥" if conviction == "HIGH" else "⚡" if conviction == "MEDIUM" else "👁"
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"{icon} **{r.get('ticker','?')}** · {r.get('sector','')}")
                        signals = r.get("signals") or []
                        action  = r.get("action", "WATCH")
                        st.caption(f"{action} · {', '.join(signals[:3])}")
                        if r.get("thesis"):
                            st.caption(r["thesis"])
                    with col2:
                        st.metric("Signals", r.get("signal_count", 0))
                        st.caption(conviction)

                    risks = r.get("risks") or []
                    if risks:
                        with st.expander("Risks"):
                            for risk in risks:
                                st.caption(f"⚠ {risk}")

                    parts = []
                    if r.get("entry_zone"): parts.append(f"Entry {r['entry_zone']}")
                    if r.get("target"):     parts.append(f"T1 {_p(r['target'])}")
                    if r.get("stop_loss"):  parts.append(f"SL {_p(r['stop_loss'])}")
                    if parts:
                        st.caption(" · ".join(parts))


if __name__ == "__main__":
    main()
