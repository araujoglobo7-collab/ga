import warnings
import urllib3
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
from io import StringIO
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore")

st.set_page_config(
    layout="wide",
    page_title="GMAC — Ponto",
    page_icon="📍",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

:root {
    --bg: #F6F5FA;
    --bg2: #FFFFFF;
    --border: #E2E4EA;
    --accent: #DC2626;
    --green: #16A34A;
    --text: #111827;
    --muted: #6B7280;
}

html, body, .stApp { font-family: 'Inter', sans-serif !important; background: var(--bg) !important; }
[data-testid="stHeader"], #MainMenu, footer { display: none !important; }
.block-container { padding: 1.5rem !important; max-width: 100% !important; }

[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .block-container { padding: 1.2rem 1rem !important; }

.stButton > button {
    background: #111827 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
.stButton > button:hover { opacity: .85 !important; }

.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 7px !important;
    padding: 7px 14px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: #111827 !important;
    color: #fff !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────
if "logado" not in st.session_state:
    st.session_state.logado = False
if "df" not in st.session_state:
    st.session_state.df = None

# ── CORES ──────────────────────────────────────────────────────
PALETA = ["#e11d48","#7c3aed","#1d4ed8","#0891b2","#059669",
          "#d97706","#ea580c","#be185d","#4338ca","#0f766e",
          "#b45309","#7e22ce","#1e40af","#047857","#9333ea"]

_cor_cache = {}
_cor_idx   = [0]

def cor_de(nome):
    if nome not in _cor_cache:
        _cor_cache[nome] = PALETA[_cor_idx[0] % len(PALETA)]
        _cor_idx[0] += 1
    return _cor_cache[nome]

def iniciais(nome):
    p = str(nome).strip().split()
    return ((p[0][0] if p else "") + (p[1][0] if len(p) > 1 else "")).upper()

# ── LOGIN ──────────────────────────────────────────────────────
if not st.session_state.logado:
    c1, _, c2 = st.columns([1, 0.05, 1])
    with c1:
        st.markdown("""
        <div style="height:480px;display:flex;align-items:center;justify-content:center;
            background:#fff;border-radius:16px;border:1px solid #e2e4e9;margin-top:40px">
          <div style="text-align:center">
            <div style="font-size:72px;margin-bottom:12px">📍</div>
            <div style="font-family:'Syne',sans-serif;font-size:36px;font-weight:800;color:#DC2626">GMAC</div>
            <div style="font-size:13px;color:#6b7280;margin-top:6px">Sistema de Gestão de Ponto</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div style="padding:60px 0 28px">
          <div style="font-family:'Syne',sans-serif;font-size:38px;font-weight:800;color:#111827;line-height:1">Bem-vindo,</div>
          <div style="font-family:'Syne',sans-serif;font-size:38px;font-weight:800;color:#DC2626;line-height:1;margin-bottom:20px">GMAC.</div>
          <p style="color:#6b7280;font-size:14px;line-height:1.8">Insira a senha para acessar<br>o painel de ponto eletrônico.</p>
        </div>
        """, unsafe_allow_html=True)
        senha = st.text_input("SENHA", type="password", placeholder="••••••••", label_visibility="visible")
        if st.button("🔐  ENTRAR", use_container_width=True):
            if senha == "gs123":
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()

# ── DADOS ──────────────────────────────────────────────────────
SHEET_ID = "1hVObjoII-YqtuFJQMjpFp4GYYNSOeZULrSe-OmxoMXY"
URLS = [
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0",
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=0",
]

# Seed — dados reais do xlsx, sempre disponíveis offline
SEED = pd.DataFrame([
    {"_dt": pd.Timestamp("2026-05-12 16:42:26"), "_nome": "JOYCIELLY ALINE TORRES GALINDO AMORIM", "_foto": "", "_status": "Saída",   "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-12 16:43:49"), "_nome": "PAULO JOSÉ",                             "_foto": "", "_status": "Saída",   "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-12 16:44:06"), "_nome": "ALEXANDRE DA CONCEIÇÃO",                "_foto": "", "_status": "Saída",   "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-12 16:45:44"), "_nome": "WANDERLEY DA SILVA NASCIMENTO",         "_foto": "", "_status": "Saída",   "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-12 16:47:02"), "_nome": "JORGE CORREIA BORGES",                  "_foto": "", "_status": "Saída",   "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-12 16:47:39"), "_nome": "FLAVIO DAS VIRGENS DE CARVALHO QUEIROZ","_foto": "", "_status": "Saída",   "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-12 16:48:33"), "_nome": "MARIO ALVES",                           "_foto": "", "_status": "Saída",   "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-12 16:48:51"), "_nome": "EDOIL BATISTA MARTINS",                 "_foto": "", "_status": "Saída",   "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-12 16:50:05"), "_nome": "THIAGO RAFAEL CARVALHO DE SANTANA",     "_foto": "", "_status": "Saída",   "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-13 06:45:42"), "_nome": "JORGE CORREIA BORGES",                  "_foto": "", "_status": "Entrada", "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-13 06:47:03"), "_nome": "JOYCIELLY ALINE TORRES GALINDO AMORIM", "_foto": "", "_status": "Entrada", "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-13 06:47:18"), "_nome": "THIAGO RAFAEL CARVALHO DE SANTANA",     "_foto": "", "_status": "Entrada", "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-13 06:47:58"), "_nome": "WANDERLEY DA SILVA NASCIMENTO",         "_foto": "", "_status": "Entrada", "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-13 06:50:24"), "_nome": "MARCOS ANTONIO LIMA NASCIMENTO",        "_foto": "", "_status": "Entrada", "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-13 06:51:44"), "_nome": "ED CARLOS SOUZA CARDOSO",               "_foto": "", "_status": "Entrada", "_lat": -8.378224, "_lng": -35.026251},
    {"_dt": pd.Timestamp("2026-05-13 10:03:16"), "_nome": "EDOIL BATISTA MARTINS",                 "_foto": "", "_status": "Entrada", "_lat": -8.377972, "_lng": -35.025940},
    {"_dt": pd.Timestamp("2026-05-13 10:03:41"), "_nome": "ANTONIO JORGE VIEIRA",                  "_foto": "", "_status": "Entrada", "_lat": -8.377981, "_lng": -35.025935},
    {"_dt": pd.Timestamp("2026-05-13 10:04:02"), "_nome": "FLAVIO DAS VIRGENS DE CARVALHO QUEIROZ","_foto": "", "_status": "Entrada", "_lat": -8.377977, "_lng": -35.025937},
    {"_dt": pd.Timestamp("2026-05-13 10:04:28"), "_nome": "FELIPE BOTELHO SANTOS",                 "_foto": "", "_status": "Entrada", "_lat": -8.377961, "_lng": -35.025937},
])

def _processar_csv(texto):
    df = pd.read_csv(StringIO(texto))
    df.columns = [c.strip() for c in df.columns]
    col_dt  = next((c for c in df.columns if "data"  in c.lower()), None)
    col_nm  = next((c for c in df.columns if "colab" in c.lower()), df.columns[1] if len(df.columns) > 1 else None)
    col_ft  = next((c for c in df.columns if "foto"  in c.lower()), None)
    col_st  = next((c for c in df.columns if "status" in c.lower()), None)
    col_lc  = next((c for c in df.columns if "local" in c.lower()), None)
    df["_dt"]     = pd.to_datetime(df[col_dt], errors="coerce") if col_dt else pd.NaT
    df["_nome"]   = df[col_nm].astype(str).str.strip() if col_nm else ""
    df["_foto"]   = df[col_ft].astype(str).str.strip() if col_ft else ""
    df["_status"] = df[col_st].astype(str).str.strip() if col_st else ""
    if col_lc:
        coords = df[col_lc].astype(str).str.split(",", expand=True)
        df["_lat"] = pd.to_numeric(coords[0].str.strip(), errors="coerce")
        df["_lng"] = pd.to_numeric(coords[1].str.strip() if coords.shape[1] > 1 else "", errors="coerce")
    else:
        df["_lat"] = None; df["_lng"] = None
    return df.dropna(subset=["_nome"]).query("_nome != '' and _nome != 'nan'").reset_index(drop=True)

def carregar_dados():
    for url in URLS:
        try:
            r = requests.get(url, timeout=5, verify=False, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200 and len(r.text) > 100:
                return _processar_csv(r.text)
        except Exception:
            continue
    return SEED.copy()


if st.session_state.df is None:
    st.session_state.df = carregar_dados()

df = st.session_state.df

# Pré-registrar cores
for n in df["_nome"].unique():
    cor_de(n)

# ── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0 0 16px">
      <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:#DC2626">GMAC</div>
      <div style="font-size:11px;color:#9ca3af;margin-top:2px">Gestão de Ponto</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("🔄 Sincronizar", use_container_width=True):
        st.cache_data.clear()
        with st.spinner("Buscando dados..."):
            novo_df = carregar_dados()
        st.session_state.df = novo_df
        df = st.session_state.df
        online = len(df) > 0 and any(df["_foto"].astype(str).str.startswith("Pág", na=False))
        st.success(f"✅ {len(df)} registros carregados!")
        st.rerun()

    st.link_button("📊 Abrir Planilha", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit", use_container_width=True)

    st.divider()

    if not df.empty:
        total  = len(df)
        ent    = len(df[df["_status"] == "Entrada"])
        sai    = len(df[df["_status"] == "Saída"])
        colabs = df["_nome"].nunique()

        for lbl, val, cor in [
            ("REGISTROS",      total,  "#111827"),
            ("ENTRADAS",       ent,    "#16a34a"),
            ("SAÍDAS",         sai,    "#dc2626"),
            ("COLABORADORES",  colabs, "#1d4ed8"),
        ]:
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #e2e4e9;border-radius:10px;
                padding:12px 14px;margin-bottom:8px">
              <div style="font-size:9px;letter-spacing:2px;color:#9ca3af;margin-bottom:4px">{lbl}</div>
              <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:{cor}">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    if st.button("Sair", use_container_width=True):
        st.session_state.logado = False
        st.session_state.df = None
        st.rerun()

# ── HEADER ─────────────────────────────────────────────────────
now = datetime.now()
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
    padding:16px 24px;border:1px solid #e2e4e9;border-radius:14px;
    background:#fff;margin-bottom:24px">
  <div>
    <div style="font-size:10px;letter-spacing:3px;color:#DC2626;margin-bottom:4px">● SISTEMA ATIVO</div>
    <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:#111827">GMAC — PONTO ELETRÔNICO</div>
  </div>
  <div style="text-align:right;font-size:11px;color:#9ca3af">
    <div style="color:#16a34a;margin-bottom:4px">● ONLINE</div>
    <div>{now.strftime('%d/%m/%Y  %H:%M')}</div>
  </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📋 Registro Diário", "📍 Localização"])

# ── TAB 1 — REGISTRO ───────────────────────────────────────────
with tab1:
    if df.empty:
        st.warning("Nenhum dado. Clique em Sincronizar.")
    else:
        f1, f2, f3 = st.columns(3)
        nomes = ["Todos"] + sorted(df["_nome"].unique().tolist())

        with f1:
            f_nome = st.selectbox("Colaborador", nomes, key="reg_nome")
        with f2:
            datas_disp = ["Todas"] + sorted(
                df["_dt"].dropna().dt.date.unique().astype(str).tolist(), reverse=True
            )
            f_data = st.selectbox("Data", datas_disp, key="reg_data")
        with f3:
            f_status = st.selectbox("Status", ["Entrada e Saída", "Entrada", "Saída"], key="reg_status")

        # Filtrar
        dff = df.copy()
        if f_nome != "Todos":
            dff = dff[dff["_nome"] == f_nome]
        if f_data != "Todas":
            dff = dff[dff["_dt"].dt.date.astype(str) == f_data]
        if f_status != "Entrada e Saída":
            dff = dff[dff["_status"] == f_status]
        dff = dff.sort_values("_dt", ascending=False)

        # Card colaborador
        if f_nome != "Todos":
            dc = df[df["_nome"] == f_nome]
            e  = len(dc[dc["_status"] == "Entrada"])
            s  = len(dc[dc["_status"] == "Saída"])
            c  = cor_de(f_nome)
            ini_str = iniciais(f_nome)
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #e2e4e9;border-radius:12px;
                padding:16px 20px;margin-bottom:16px;display:flex;align-items:center;gap:18px">
              <div style="width:72px;height:72px;border-radius:50%;background:{c};
                  display:flex;align-items:center;justify-content:center;
                  font-size:22px;font-weight:700;color:#fff;flex-shrink:0">{ini_str}</div>
              <div>
                <div style="font-size:16px;font-weight:700;color:#111827;margin-bottom:8px">{f_nome}</div>
                <div style="display:flex;gap:8px;flex-wrap:wrap">
                  <span style="background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">✅ {e} Entrada{"s" if e!=1 else ""}</span>
                  <span style="background:#fef2f2;color:#dc2626;border:1px solid #fecaca;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">🔴 {s} Saída{"s" if s!=1 else ""}</span>
                  <span style="background:#f4f5f7;color:#6b7280;border:1px solid #e2e4e9;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">📊 {len(dc)} total</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Stats
        s1, s2, s3, s4 = st.columns(4)
        for col, lbl, val, cor in [
            (s1, "Registros",     len(dff),                                           "#111827"),
            (s2, "Entradas",      len(dff[dff["_status"]=="Entrada"]),                "#16a34a"),
            (s3, "Saídas",        len(dff[dff["_status"]=="Saída"]),                  "#dc2626"),
            (s4, "Colaboradores", dff["_nome"].nunique(),                              "#1d4ed8"),
        ]:
            col.markdown(f"""
            <div style="background:#fff;border:1px solid #e2e4e9;border-radius:10px;padding:14px 18px">
              <div style="font-size:11px;color:#6b7280;margin-bottom:4px">{lbl}</div>
              <div style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:{cor}">{val}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabela
        if dff.empty:
            st.info("Nenhum registro encontrado.")
        else:
            st.markdown("""
            <div style="display:grid;grid-template-columns:60px 1fr 130px 90px 110px;gap:12px;
                padding:10px 16px;background:#f4f5f7;border-radius:8px;margin-bottom:4px">
              <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.5px">Foto</div>
              <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.5px">Colaborador</div>
              <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.5px">Data</div>
              <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.5px">Horário</div>
              <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.5px">Status</div>
            </div>
            """, unsafe_allow_html=True)

            rows_html = ""
            for _, row in dff.iterrows():
                nome   = row["_nome"]
                c      = cor_de(nome)
                ini_s  = iniciais(nome)
                dt_val = row["_dt"]
                data_s = dt_val.strftime("%d/%m/%Y") if pd.notna(dt_val) else "—"
                hora_s = dt_val.strftime("%H:%M")    if pd.notna(dt_val) else "—"
                status = row["_status"]
                isE    = status == "Entrada"
                bbg    = "#f0fdf4" if isE else "#fef2f2"
                btc    = "#16a34a" if isE else "#dc2626"
                bbd    = "#bbf7d0" if isE else "#fecaca"

                # Foto: URL pública ou iniciais
                foto_val = str(row.get("_foto", "")).strip()
                if foto_val and foto_val.startswith("http"):
                    av = f'<img src="{foto_val}" style="width:44px;height:44px;border-radius:50%;object-fit:cover;border:2px solid #e2e4e9">'
                else:
                    av = f'<div style="width:44px;height:44px;border-radius:50%;background:{c};display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:#fff">{ini_s}</div>'

                rows_html += f"""
                <div style="display:grid;grid-template-columns:60px 1fr 130px 90px 110px;gap:12px;
                    align-items:center;padding:12px 16px;background:#fff;border:1px solid #e2e4e9;
                    border-radius:8px;margin-bottom:4px">
                  <div>{av}</div>
                  <div style="font-weight:500;font-size:13px">{nome}</div>
                  <div style="font-size:13px;color:#6b7280">{data_s}</div>
                  <div style="font-size:13px;color:#6b7280">{hora_s}</div>
                  <div><span style="background:{bbg};color:{btc};border:1px solid {bbd};
                      padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600;
                      display:inline-flex;align-items:center;gap:5px">
                    <span style="width:5px;height:5px;border-radius:50%;background:{btc}"></span>
                    {status}
                  </span></div>
                </div>"""

            st.markdown(rows_html, unsafe_allow_html=True)

# ── TAB 2 — LOCALIZAÇÃO ────────────────────────────────────────
with tab2:
    if df.empty:
        st.warning("Nenhum dado. Clique em Sincronizar.")
    else:
        m1, m2 = st.columns(2)
        nomes_m = ["Todos"] + sorted(df["_nome"].unique().tolist())

        with m1:
            f_mnome = st.selectbox("Colaborador", nomes_m, key="loc_nome")
        with m2:
            datas_m = ["Todas"] + sorted(
                df["_dt"].dropna().dt.date.unique().astype(str).tolist(), reverse=True
            )
            f_mdata = st.selectbox("Data", datas_m, key="loc_data")

        dfm = df.copy()
        if f_mnome != "Todos":
            dfm = dfm[dfm["_nome"] == f_mnome]
        if f_mdata != "Todas":
            dfm = dfm[dfm["_dt"].dt.date.astype(str) == f_mdata]
        dfm = dfm.dropna(subset=["_lat","_lng"]).sort_values("_dt", ascending=False)

        # Card colaborador
        if f_mnome != "Todos":
            dc  = df[df["_nome"] == f_mnome]
            e   = len(dc[dc["_status"] == "Entrada"])
            s   = len(dc[dc["_status"] == "Saída"])
            c   = cor_de(f_mnome)
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #e2e4e9;border-radius:12px;
                padding:16px 20px;margin-bottom:16px;display:flex;align-items:center;gap:18px">
              <div style="width:72px;height:72px;border-radius:50%;background:{c};
                  display:flex;align-items:center;justify-content:center;
                  font-size:22px;font-weight:700;color:#fff;flex-shrink:0">{iniciais(f_mnome)}</div>
              <div>
                <div style="font-size:16px;font-weight:700;color:#111827;margin-bottom:8px">{f_mnome}</div>
                <div style="display:flex;gap:8px">
                  <span style="background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">✅ {e} Entrada{"s" if e!=1 else ""}</span>
                  <span style="background:#fef2f2;color:#dc2626;border:1px solid #fecaca;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">🔴 {s} Saída{"s" if s!=1 else ""}</span>
                  <span style="background:#f4f5f7;color:#6b7280;border:1px solid #e2e4e9;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">📍 {len(dfm)} no mapa</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Mapa Leaflet — igual ao Gabriel usa no mapeamento GS
        if dfm.empty:
            st.info("Nenhum registro com localização para os filtros selecionados.")
        else:
            clat = float(dfm["_lat"].mean())
            clng = float(dfm["_lng"].mean())

            # Montar marcadores
            markers_js = ""
            for _, row in dfm.iterrows():
                nome   = str(row["_nome"])
                status = str(row["_status"])
                isE    = status == "Entrada"
                cor    = "#16a34a" if isE else "#dc2626"
                dt_val = row["_dt"]
                data_s = dt_val.strftime("%d/%m/%Y") if pd.notna(dt_val) else ""
                hora_s = dt_val.strftime("%H:%M")    if pd.notna(dt_val) else ""
                lat    = float(row["_lat"])
                lng    = float(row["_lng"])
                ini_s  = iniciais(nome)

                # Nome abreviado: primeiro + último
                partes = nome.split()
                abrev  = (partes[0] + " " + partes[-1]) if len(partes) > 1 else nome

                # Escapar para JS — substituir aspas e caracteres problemáticos
                abrev_js = abrev.replace("'", "\\'").replace('"', '\\"')
                hora_js  = hora_s.replace("'", "\\'")
                status_js = status.replace("'", "\\'")
                bg    = "#f0fdf4" if isE else "#fef2f2"
                bbd   = "#bbf7d0" if isE else "#fecaca"

                markers_js += (
                    "L.marker([" + str(lat) + "," + str(lng) + "],{"
                    "icon:L.divIcon({"
                    "html:'<div style=\"width:36px;height:46px\">"
                    "<div style=\"width:36px;height:36px;border-radius:50%;background:" + cor + ";border:3px solid #fff;"
                    "box-shadow:0 2px 8px rgba(0,0,0,.3);display:flex;align-items:center;justify-content:center;"
                    "font-size:11px;font-weight:700;color:#fff;font-family:Inter,sans-serif\">" + ini_s + "</div>"
                    "<div style=\"width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;"
                    "border-top:10px solid " + cor + ";margin:0 auto\"></div>"
                    "</div>',"
                    "className:'',iconSize:[36,46],iconAnchor:[18,46],popupAnchor:[0,-48]"
                    "})}).addTo(map)"
                    ".bindPopup('<div style=\"font-family:Inter,sans-serif;min-width:180px\">"
                    "<div style=\"font-weight:700;font-size:13px;color:#111;margin-bottom:8px\">" + abrev_js + "</div>"
                    "<div style=\"font-size:12px;color:#6b7280;margin-bottom:8px\">📅 " + data_s + " &middot; " + hora_js + "</div>"
                    "<span style=\"background:" + bg + ";color:" + cor + ";border:1px solid " + bbd + ";"
                    "padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600\">" + status_js + "</span>"
                    "</div>',{maxWidth:260});\n"
                )

            mapa_html = (
                "<!DOCTYPE html><html><head><meta charset='utf-8'>"
                "<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'/>"
                "<script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>"
                "<style>body{margin:0}#map{width:100%;height:520px;border-radius:12px}</style>"
                "</head><body>"
                "<div id='map'></div>"
                "<script>"
                "var map=L.map('map').setView([" + str(clat) + "," + str(clng) + "],17);"
                "L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',"
                "{attribution:'&copy; OpenStreetMap',maxZoom:20}).addTo(map);"
                + markers_js +
                "var layers=[];map.eachLayer(function(l){if(l instanceof L.Marker)layers.push(l)});"
                "if(layers.length){map.fitBounds(L.featureGroup(layers).getBounds().pad(0.35));}"
                "</script></body></html>"
            )

            components.html(mapa_html, height=540)

            # Legenda
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #e2e4e9;border-radius:10px;
                padding:12px 18px;margin-top:10px;display:flex;gap:20px;align-items:center">
              <strong style="font-size:12px;color:#6b7280">Legenda:</strong>
              <div style="display:flex;align-items:center;gap:7px;font-size:13px;color:#6b7280">
                <div style="width:10px;height:10px;border-radius:50%;background:#16a34a"></div> Entrada
              </div>
              <div style="display:flex;align-items:center;gap:7px;font-size:13px;color:#6b7280">
                <div style="width:10px;height:10px;border-radius:50%;background:#dc2626"></div> Saída
              </div>
              <div style="margin-left:auto;font-size:12px;color:#9ca3af">{len(dfm)} registro(s) no mapa</div>
            </div>
            """, unsafe_allow_html=True)

        # Lista
        st.markdown("<br>", unsafe_allow_html=True)
        lista_html = ""
        for _, row in dfm.iterrows():
            nome   = row["_nome"]
            c      = cor_de(nome)
            status = row["_status"]
            isE    = status == "Entrada"
            bbg    = "#f0fdf4" if isE else "#fef2f2"
            btc    = "#16a34a" if isE else "#dc2626"
            bbd    = "#bbf7d0" if isE else "#fecaca"
            dt_val = row["_dt"]
            lista_html += f"""
            <div style="display:flex;align-items:center;gap:12px;padding:11px 16px;
                background:#fff;border:1px solid #e2e4e9;border-radius:8px;margin-bottom:4px">
              <div style="width:36px;height:36px;border-radius:50%;background:{c};display:flex;
                  align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#fff;flex-shrink:0">
                {iniciais(nome)}
              </div>
              <div style="flex:1;font-weight:500;font-size:13px">{nome}</div>
              <div style="font-size:12px;color:#6b7280">{dt_val.strftime('%d/%m/%Y · %H:%M') if pd.notna(dt_val) else '—'}</div>
              <span style="background:{bbg};color:{btc};border:1px solid {bbd};
                  padding:3px 9px;border-radius:20px;font-size:11px;font-weight:600">{status}</span>
            </div>"""

        if lista_html:
            st.markdown(lista_html, unsafe_allow_html=True)
