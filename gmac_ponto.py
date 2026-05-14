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
html, body, .stApp { font-family: 'Inter', sans-serif !important; background: #f4f5f7 !important; }
[data-testid="stHeader"], #MainMenu, footer { display: none !important; }
.block-container { padding: 1.5rem !important; max-width: 100% !important; }
[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e2e4e9 !important; }
[data-testid="stSidebar"] .block-container { padding: 1.2rem 1rem !important; }
.stButton > button { background: #111827 !important; color: #fff !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; font-size: 13px !important; }
.stButton > button:hover { opacity: .85 !important; }
.stTabs [data-baseweb="tab-list"] { background: #fff !important; border: 1px solid #e2e4e9 !important; border-radius: 10px !important; padding: 4px !important; gap: 2px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #6b7280 !important; border-radius: 7px !important; padding: 7px 14px !important; font-size: 13px !important; font-weight: 500 !important; border: none !important; }
.stTabs [aria-selected="true"] { background: #111827 !important; color: #fff !important; }
::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ───────────────────────────────────────────────
if "logado"   not in st.session_state: st.session_state.logado   = False
if "df"       not in st.session_state: st.session_state.df       = None
if "sync_ok"  not in st.session_state: st.session_state.sync_ok  = False
if "chat_hist" not in st.session_state: st.session_state.chat_hist = []

# ── CORES ───────────────────────────────────────────────────────
PAL = ["#e11d48","#7c3aed","#1d4ed8","#0891b2","#059669","#d97706",
       "#ea580c","#be185d","#4338ca","#0f766e","#b45309","#7e22ce",
       "#1e40af","#047857","#9333ea"]
_cc, _ci = {}, [0]
def cor(n):
    if n not in _cc: _cc[n] = PAL[_ci[0] % len(PAL)]; _ci[0] += 1
    return _cc[n]
def ini(n):
    p = str(n).strip().split()
    return ((p[0][0] if p else "") + (p[1][0] if len(p)>1 else "")).upper()

# ── DADOS ───────────────────────────────────────────────────────
SHEET_ID = "1hVObjoII-YqtuFJQMjpFp4GYYNSOeZULrSe-OmxoMXY"
URLS = [
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0",
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=0",
]

SEED = pd.DataFrame([
    {"_dt":pd.Timestamp("2026-05-12 16:42:26"),"_nome":"JOYCIELLY ALINE TORRES GALINDO AMORIM","_foto":"","_status":"Saída","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-12 16:43:49"),"_nome":"PAULO JOSÉ","_foto":"","_status":"Saída","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-12 16:44:06"),"_nome":"ALEXANDRE DA CONCEIÇÃO","_foto":"","_status":"Saída","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-12 16:45:44"),"_nome":"WANDERLEY DA SILVA NASCIMENTO","_foto":"","_status":"Saída","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-12 16:47:02"),"_nome":"JORGE CORREIA BORGES","_foto":"","_status":"Saída","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-12 16:47:39"),"_nome":"FLAVIO DAS VIRGENS DE CARVALHO QUEIROZ","_foto":"","_status":"Saída","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-12 16:48:33"),"_nome":"MARIO ALVES","_foto":"","_status":"Saída","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-12 16:48:51"),"_nome":"EDOIL BATISTA MARTINS","_foto":"","_status":"Saída","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-12 16:50:05"),"_nome":"THIAGO RAFAEL CARVALHO DE SANTANA","_foto":"","_status":"Saída","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-13 06:45:42"),"_nome":"JORGE CORREIA BORGES","_foto":"","_status":"Entrada","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-13 06:47:03"),"_nome":"JOYCIELLY ALINE TORRES GALINDO AMORIM","_foto":"","_status":"Entrada","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-13 06:47:18"),"_nome":"THIAGO RAFAEL CARVALHO DE SANTANA","_foto":"","_status":"Entrada","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-13 06:47:58"),"_nome":"WANDERLEY DA SILVA NASCIMENTO","_foto":"","_status":"Entrada","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-13 06:50:24"),"_nome":"MARCOS ANTONIO LIMA NASCIMENTO","_foto":"","_status":"Entrada","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-13 06:51:44"),"_nome":"ED CARLOS SOUZA CARDOSO","_foto":"","_status":"Entrada","_lat":-8.378224,"_lng":-35.026251},
    {"_dt":pd.Timestamp("2026-05-13 10:03:16"),"_nome":"EDOIL BATISTA MARTINS","_foto":"","_status":"Entrada","_lat":-8.377972,"_lng":-35.025940},
    {"_dt":pd.Timestamp("2026-05-13 10:03:41"),"_nome":"ANTONIO JORGE VIEIRA","_foto":"","_status":"Entrada","_lat":-8.377981,"_lng":-35.025935},
    {"_dt":pd.Timestamp("2026-05-13 10:04:02"),"_nome":"FLAVIO DAS VIRGENS DE CARVALHO QUEIROZ","_foto":"","_status":"Entrada","_lat":-8.377977,"_lng":-35.025937},
    {"_dt":pd.Timestamp("2026-05-13 10:04:28"),"_nome":"FELIPE BOTELHO SANTOS","_foto":"","_status":"Entrada","_lat":-8.377961,"_lng":-35.025937},
])

def _processar(texto):
    df = pd.read_csv(StringIO(texto))
    df.columns = [c.strip() for c in df.columns]
    col_dt = next((c for c in df.columns if "data"   in c.lower()), None)
    col_nm = next((c for c in df.columns if "colab"  in c.lower()), df.columns[1] if len(df.columns)>1 else None)
    col_ft = next((c for c in df.columns if "foto"   in c.lower()), None)
    col_st = next((c for c in df.columns if "status" in c.lower()), None)
    col_lc = next((c for c in df.columns if "local"  in c.lower()), None)
    df["_dt"]     = pd.to_datetime(df[col_dt], dayfirst=True, errors="coerce") if col_dt else pd.NaT
    df["_nome"]   = df[col_nm].astype(str).str.strip() if col_nm else ""
    df["_foto"]   = df[col_ft].astype(str).str.strip() if col_ft else ""
    df["_status"] = df[col_st].astype(str).str.strip() if col_st else ""
    if col_lc:
        coords = df[col_lc].astype(str).str.split(",", expand=True)
        df["_lat"] = pd.to_numeric(coords[0].str.strip(), errors="coerce")
        df["_lng"] = pd.to_numeric(coords[1].str.strip() if coords.shape[1]>1 else "", errors="coerce")
    else:
        df["_lat"] = None; df["_lng"] = None
    return df.dropna(subset=["_nome"]).query("_nome!='' and _nome!='nan'").reset_index(drop=True)

def carregar_dados():
    for url in URLS:
        try:
            r = requests.get(url, timeout=8, verify=False, headers={"User-Agent":"Mozilla/5.0"})
            if r.status_code == 200 and len(r.text) > 100:
                df = _processar(r.text)
                if len(df) > 0:
                    st.session_state.sync_ok = True
                    return df
        except Exception:
            continue
    st.session_state.sync_ok = False
    return SEED.copy()

if st.session_state.df is None:
    st.session_state.df = carregar_dados()

df = st.session_state.df
for n in df["_nome"].unique(): cor(n)

# ── LOGIN ───────────────────────────────────────────────────────
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

# ── SIDEBAR ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0 0 16px">
      <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:#DC2626">GMAC</div>
      <div style="font-size:11px;color:#9ca3af;margin-top:2px">Gestão de Ponto</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    if st.button("🔄 Sincronizar", use_container_width=True):
        with st.spinner("Buscando dados do Sheets..."):
            st.session_state.df = carregar_dados()
            df = st.session_state.df
        if st.session_state.sync_ok:
            st.success(f"✅ {len(df)} registros do Sheets!")
        else:
            st.warning("⚠️ Sem acesso — usando dados locais.")
        st.rerun()

    st.link_button("📊 Abrir Planilha", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit", use_container_width=True)
    st.divider()

    # Status sync
    status_cor  = "#16a34a" if st.session_state.sync_ok else "#f59e0b"
    status_txt  = "Online — Sheets" if st.session_state.sync_ok else "Dados locais"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
      <div style="width:8px;height:8px;border-radius:50%;background:{status_cor}"></div>
      <span style="font-size:12px;color:#6b7280">{status_txt}</span>
    </div>
    """, unsafe_allow_html=True)

    df = st.session_state.df
    if not df.empty:
        total  = len(df)
        ent    = len(df[df["_status"]=="Entrada"])
        sai    = len(df[df["_status"]=="Saída"])
        colabs = df["_nome"].nunique()
        for lbl, val, c in [("REGISTROS",total,"#111827"),("ENTRADAS",ent,"#16a34a"),("SAÍDAS",sai,"#dc2626"),("COLABORADORES",colabs,"#1d4ed8")]:
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #e2e4e9;border-radius:10px;padding:12px 14px;margin-bottom:8px">
              <div style="font-size:9px;letter-spacing:2px;color:#9ca3af;margin-bottom:4px">{lbl}</div>
              <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:{c}">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    if st.button("Sair", use_container_width=True):
        st.session_state.logado = False
        st.session_state.df = None
        st.rerun()

# ── HEADER ──────────────────────────────────────────────────────
now = datetime.now()
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
    padding:16px 24px;border:1px solid #e2e4e9;border-radius:14px;background:#fff;margin-bottom:20px">
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

df = st.session_state.df
tab3, tab1, tab2 = st.tabs(["🤖 Chat IA", "📋 Registro Diário", "📍 Localização"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — REGISTRO DIÁRIO
# ══════════════════════════════════════════════════════════════
with tab1:
    if df.empty:
        st.warning("Nenhum dado. Clique em Sincronizar.")
    else:
        f1, f2, f3 = st.columns(3)

        nomes = ["Todos"] + sorted(df["_nome"].dropna().unique().tolist())
        with f1:
            f_nome = st.selectbox("Colaborador", nomes, key="reg_nome")

        # Datas — todas as datas únicas da base, ordenadas do mais recente
        datas_unicas = sorted(
            df["_dt"].dropna().dt.date.unique().tolist(), reverse=True
        )
        opcoes_data = ["Todas"] + [d.strftime("%d/%m/%Y") for d in datas_unicas]
        with f2:
            f_data_str = st.selectbox("Data", opcoes_data, key="reg_data")

        with f3:
            f_status = st.selectbox("Status", ["Entrada e Saída","Entrada","Saída"], key="reg_status")

        # Filtrar
        dff = df.copy().sort_values("_dt", ascending=False)
        if f_nome != "Todos":
            dff = dff[dff["_nome"] == f_nome]
        if f_data_str != "Todas":
            dff = dff[dff["_dt"].dt.strftime("%d/%m/%Y") == f_data_str]
        if f_status != "Entrada e Saída":
            dff = dff[dff["_status"] == f_status]

        # Card colaborador
        if f_nome != "Todos":
            dc  = df[df["_nome"] == f_nome]
            e   = len(dc[dc["_status"]=="Entrada"])
            s   = len(dc[dc["_status"]=="Saída"])
            c   = cor(f_nome)
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #e2e4e9;border-radius:12px;
                padding:16px 20px;margin-bottom:16px;display:flex;align-items:center;gap:18px">
              <div style="width:64px;height:64px;border-radius:50%;background:{c};
                  display:flex;align-items:center;justify-content:center;
                  font-size:20px;font-weight:700;color:#fff;flex-shrink:0">{ini(f_nome)}</div>
              <div>
                <div style="font-size:15px;font-weight:700;color:#111827;margin-bottom:8px">{f_nome}</div>
                <div style="display:flex;gap:8px;flex-wrap:wrap">
                  <span style="background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">✅ {e} Entrada{"s" if e!=1 else ""}</span>
                  <span style="background:#fef2f2;color:#dc2626;border:1px solid #fecaca;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">🔴 {s} Saída{"s" if s!=1 else ""}</span>
                  <span style="background:#f4f5f7;color:#6b7280;border:1px solid #e2e4e9;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">📊 {len(dc)} total</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Stats
        s1,s2,s3,s4 = st.columns(4)
        for col,lbl,val,c in [
            (s1,"Registros",    len(dff),                                "#111827"),
            (s2,"Entradas",     len(dff[dff["_status"]=="Entrada"]),     "#16a34a"),
            (s3,"Saídas",       len(dff[dff["_status"]=="Saída"]),       "#dc2626"),
            (s4,"Colaboradores",dff["_nome"].nunique(),                   "#1d4ed8"),
        ]:
            col.markdown(f"""
            <div style="background:#fff;border:1px solid #e2e4e9;border-radius:10px;padding:14px 18px">
              <div style="font-size:11px;color:#6b7280;margin-bottom:4px">{lbl}</div>
              <div style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:{c}">{val}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabela com localização
        if dff.empty:
            st.info("Nenhum registro encontrado.")
        else:
            st.markdown("""
            <div style="display:grid;grid-template-columns:56px 1fr 110px 80px 100px 140px;gap:10px;
                padding:10px 14px;background:#f4f5f7;border-radius:8px;margin-bottom:4px">
              <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.5px">Foto</div>
              <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.5px">Colaborador</div>
              <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.5px">Data</div>
              <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.5px">Horário</div>
              <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.5px">Status</div>
              <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.5px">Localização</div>
            </div>
            """, unsafe_allow_html=True)

            rows = ""
            for _, row in dff.iterrows():
                nome   = row["_nome"]
                c      = cor(nome)
                ini_s  = ini(nome)
                dt_val = row["_dt"]
                data_s = dt_val.strftime("%d/%m/%Y") if pd.notna(dt_val) else "—"
                hora_s = dt_val.strftime("%H:%M")    if pd.notna(dt_val) else "—"
                status = row["_status"]
                isE    = status == "Entrada"
                bbg    = "#f0fdf4" if isE else "#fef2f2"
                btc    = "#16a34a" if isE else "#dc2626"
                bbd    = "#bbf7d0" if isE else "#fecaca"

                # Foto ou iniciais
                foto_val = str(row.get("_foto","")).strip()
                if foto_val and foto_val.startswith("http"):
                    av = f'<img src="{foto_val}" style="width:44px;height:44px;border-radius:50%;object-fit:cover;border:2px solid #e2e4e9">'
                else:
                    av = f'<div style="width:44px;height:44px;border-radius:50%;background:{c};display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:#fff">{ini_s}</div>'

                # Localização
                lat = row.get("_lat"); lng = row.get("_lng")
                if pd.notna(lat) and pd.notna(lng):
                    maps_url = f"https://maps.google.com/?q={lat},{lng}"
                    loc_html = f'<a href="{maps_url}" target="_blank" style="font-size:11px;color:#1d4ed8;text-decoration:none;display:flex;align-items:center;gap:4px">📍 {float(lat):.4f}, {float(lng):.4f}</a>'
                else:
                    loc_html = '<span style="font-size:11px;color:#9ca3af">—</span>'

                rows += f"""
                <div style="display:grid;grid-template-columns:56px 1fr 110px 80px 100px 140px;gap:10px;
                    align-items:center;padding:11px 14px;background:#fff;border:1px solid #e2e4e9;
                    border-radius:8px;margin-bottom:4px">
                  <div>{av}</div>
                  <div style="font-weight:500;font-size:13px;color:#111827">{nome}</div>
                  <div style="font-size:13px;color:#6b7280">{data_s}</div>
                  <div style="font-size:13px;color:#6b7280">{hora_s}</div>
                  <div><span style="background:{bbg};color:{btc};border:1px solid {bbd};
                      padding:3px 9px;border-radius:20px;font-size:12px;font-weight:600;
                      display:inline-flex;align-items:center;gap:4px">
                    <span style="width:5px;height:5px;border-radius:50%;background:{btc}"></span>{status}
                  </span></div>
                  <div>{loc_html}</div>
                </div>"""

            st.markdown(rows, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — LOCALIZAÇÃO
# ══════════════════════════════════════════════════════════════
with tab2:
    if df.empty:
        st.warning("Nenhum dado. Clique em Sincronizar.")
    else:
        m1, m2 = st.columns(2)
        nomes_m = ["Todos"] + sorted(df["_nome"].dropna().unique().tolist())
        with m1:
            f_mnome = st.selectbox("Colaborador", nomes_m, key="loc_nome")
        with m2:
            datas_m = sorted(df["_dt"].dropna().dt.date.unique().tolist(), reverse=True)
            opcoes_m = ["Todas"] + [d.strftime("%d/%m/%Y") for d in datas_m]
            f_mdata = st.selectbox("Data", opcoes_m, key="loc_data")

        dfm = df.copy()
        if f_mnome != "Todos":
            dfm = dfm[dfm["_nome"] == f_mnome]
        if f_mdata != "Todas":
            dfm = dfm[dfm["_dt"].dt.strftime("%d/%m/%Y") == f_mdata]
        dfm = dfm.dropna(subset=["_lat","_lng"]).sort_values("_dt", ascending=False)

        # Card colaborador
        if f_mnome != "Todos":
            dc = df[df["_nome"]==f_mnome]
            e  = len(dc[dc["_status"]=="Entrada"])
            s  = len(dc[dc["_status"]=="Saída"])
            c  = cor(f_mnome)
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #e2e4e9;border-radius:12px;
                padding:14px 18px;margin-bottom:14px;display:flex;align-items:center;gap:16px">
              <div style="width:56px;height:56px;border-radius:50%;background:{c};
                  display:flex;align-items:center;justify-content:center;
                  font-size:18px;font-weight:700;color:#fff;flex-shrink:0">{ini(f_mnome)}</div>
              <div>
                <div style="font-size:14px;font-weight:700;color:#111827;margin-bottom:6px">{f_mnome}</div>
                <div style="display:flex;gap:8px">
                  <span style="background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0;padding:2px 9px;border-radius:20px;font-size:12px;font-weight:600">✅ {e} Entrada{"s" if e!=1 else ""}</span>
                  <span style="background:#fef2f2;color:#dc2626;border:1px solid #fecaca;padding:2px 9px;border-radius:20px;font-size:12px;font-weight:600">🔴 {s} Saída{"s" if s!=1 else ""}</span>
                  <span style="background:#f4f5f7;color:#6b7280;border:1px solid #e2e4e9;padding:2px 9px;border-radius:20px;font-size:12px;font-weight:600">📍 {len(dfm)} no mapa</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        if dfm.empty:
            st.info("Nenhum registro com localização para os filtros selecionados.")
        else:
            # Mapa esquerda (55%) | Tabela direita (45%)
            col_mapa, col_lista = st.columns([1.2, 1])

            with col_mapa:
                clat = float(dfm["_lat"].mean())
                clng = float(dfm["_lng"].mean())

                markers_js = ""
                for _, row in dfm.iterrows():
                    nome   = str(row["_nome"])
                    status = str(row["_status"])
                    isE    = status == "Entrada"
                    mc     = "#16a34a" if isE else "#dc2626"
                    bg     = "#f0fdf4" if isE else "#fef2f2"
                    bbd    = "#bbf7d0" if isE else "#fecaca"
                    lat    = float(row["_lat"])
                    lng    = float(row["_lng"])
                    ini_s  = ini(nome)
                    dt_val = row["_dt"]
                    data_s = dt_val.strftime("%d/%m/%Y") if pd.notna(dt_val) else ""
                    hora_s = dt_val.strftime("%H:%M")    if pd.notna(dt_val) else ""
                    partes = nome.split()
                    abrev  = (partes[0]+" "+partes[-1]) if len(partes)>1 else nome
                    abrev_js  = abrev.replace("'","\\'")
                    status_js = status.replace("'","\\'")

                    markers_js += (
                        "L.marker(["+str(lat)+","+str(lng)+"],{"
                        "icon:L.divIcon({"
                        "html:'<div style=\"width:36px;height:46px\">"
                        "<div style=\"width:36px;height:36px;border-radius:50%;background:"+mc+";border:3px solid #fff;"
                        "box-shadow:0 2px 12px rgba(0,0,0,.3);display:flex;align-items:center;justify-content:center;"
                        "font-size:11px;font-weight:700;color:#fff;font-family:Inter,sans-serif\">"+ini_s+"</div>"
                        "<div style=\"width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;"
                        "border-top:10px solid "+mc+";margin:0 auto\"></div>"
                        "</div>',"
                        "className:'',iconSize:[36,46],iconAnchor:[18,46],popupAnchor:[0,-48]"
                        "})"
                        "}).addTo(map)"
                        ".bindPopup("
                        "'<div style=\"font-family:Inter,sans-serif;min-width:190px;padding:4px\">"
                        "<div style=\"font-weight:700;font-size:13px;color:#111;margin-bottom:8px\">"+abrev_js+"</div>"
                        "<div style=\"font-size:12px;color:#6b7280;margin-bottom:8px\">📅 "+data_s+" &middot; "+hora_s+"</div>"
                        "<span style=\"background:"+bg+";color:"+mc+";border:1px solid "+bbd+";"
                        "padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600\">"+status_js+"</span>"
                        "<div style=\"margin-top:8px;font-size:10px;color:#9ca3af\">"+str(round(lat,6))+"&deg;, "+str(round(lng,6))+"&deg;</div>"
                        "</div>',"
                        "{maxWidth:260});\n"
                    )

                mapa_html = (
                    "<!DOCTYPE html><html><head><meta charset='utf-8'>"
                    "<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'/>"
                    "<script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>"
                    "<style>body{margin:0}#map{width:100%;height:420px;border-radius:12px}</style>"
                    "</head><body><div id='map'></div><script>"
                    "var map=L.map('map').setView(["+str(clat)+","+str(clng)+"],17);"
                    "L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',"
                    "{attribution:'&copy; <a href=\"https://www.openstreetmap.org\">OpenStreetMap</a>',"
                    "maxZoom:20}).addTo(map);"
                    +markers_js+
                    "var layers=[];map.eachLayer(function(l){if(l instanceof L.Marker)layers.push(l)});"
                    "if(layers.length>1){map.fitBounds(L.featureGroup(layers).getBounds().pad(0.35));}"
                    "</script></body></html>"
                )

                components.html(mapa_html, height=440)

                st.markdown(f"""
                <div style="background:#fff;border:1px solid #e2e4e9;border-radius:8px;
                    padding:8px 14px;margin-top:6px;display:flex;gap:16px;align-items:center">
                  <strong style="font-size:11px;color:#6b7280">Legenda:</strong>
                  <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:#6b7280">
                    <div style="width:9px;height:9px;border-radius:50%;background:#16a34a"></div> Entrada
                  </div>
                  <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:#6b7280">
                    <div style="width:9px;height:9px;border-radius:50%;background:#dc2626"></div> Saída
                  </div>
                  <div style="margin-left:auto;font-size:12px;color:#9ca3af">{len(dfm)} registro(s)</div>
                </div>
                """, unsafe_allow_html=True)

            with col_lista:
                st.markdown("""
                <div style="background:#f4f5f7;border-radius:8px;padding:9px 12px;margin-bottom:4px">
                  <div style="display:grid;grid-template-columns:36px 1fr 95px 75px;gap:8px">
                    <div></div>
                    <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.5px">Colaborador</div>
                    <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.5px">Data</div>
                    <div style="font-size:10px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.5px">Status</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                lista_html = ""
                for _, row in dfm.iterrows():
                    nome   = row["_nome"]
                    c      = cor(nome)
                    status = row["_status"]
                    isE    = status == "Entrada"
                    bbg    = "#f0fdf4" if isE else "#fef2f2"
                    btc    = "#16a34a" if isE else "#dc2626"
                    bbd    = "#bbf7d0" if isE else "#fecaca"
                    dt_val = row["_dt"]
                    data_s = dt_val.strftime("%d/%m/%Y") if pd.notna(dt_val) else "—"
                    hora_s = dt_val.strftime("%H:%M")    if pd.notna(dt_val) else "—"

                    lista_html += f"""
                    <div style="display:grid;grid-template-columns:36px 1fr 95px 75px;gap:8px;
                        align-items:center;padding:9px 12px;background:#fff;border:1px solid #e2e4e9;
                        border-radius:8px;margin-bottom:4px">
                      <div style="width:32px;height:32px;border-radius:50%;background:{c};display:flex;
                          align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#fff;flex-shrink:0">
                        {ini(nome)}
                      </div>
                      <div style="min-width:0">
                        <div style="font-weight:500;font-size:12px;color:#111827;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{nome}</div>
                        <div style="font-size:11px;color:#9ca3af">{hora_s}</div>
                      </div>
                      <div style="font-size:12px;color:#6b7280">{data_s}</div>
                      <div><span style="background:{bbg};color:{btc};border:1px solid {bbd};
                          padding:2px 7px;border-radius:20px;font-size:11px;font-weight:600;white-space:nowrap">{status}</span></div>
                    </div>"""

                st.markdown(f'<div style="max-height:440px;overflow-y:auto">{lista_html}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 3 — CHAT IA
# ══════════════════════════════════════════════════════════════
with tab3:
    df = st.session_state.df

    SUGESTOES = [
        ("👥", "Quem bateu ponto hoje?"),
        ("📊", "Quantas entradas e saídas registradas?"),
        ("🔴", "Quem só registrou saída sem entrada?"),
        ("📅", "Qual foi o último registro de cada colaborador?"),
        ("⏰", "Quem chegou mais cedo hoje?"),
        ("🕐", "Quem chegou mais tarde hoje?"),
        ("📍", "Quais colaboradores têm localização registrada?"),
        ("📈", "Resumo geral do ponto hoje"),
    ]

    pergunta_rapida = None

    col_chat, col_sugest = st.columns([2.2, 1])

    with col_sugest:
        st.markdown("""
        <div style="background:#fff;border:1px solid #e2e4e9;border-radius:14px;padding:18px;">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid #e2e4e9;">
            <div style="width:44px;height:44px;background:#111827;border-radius:50%;
                display:flex;align-items:center;justify-content:center;font-size:22px;">🤖</div>
            <div>
              <div style="font-weight:700;font-size:14px;color:#111827;">Assistente GMAC</div>
              <div style="font-size:11px;color:#16a34a;font-family:monospace;">● ONLINE</div>
            </div>
          </div>
          <div style="font-size:10px;font-weight:600;color:#9ca3af;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;">
            PERGUNTAS RÁPIDAS
          </div>
        </div>
        """, unsafe_allow_html=True)

        for i, (emoji, s) in enumerate(SUGESTOES):
            if st.button(f"{emoji}  {s}", key=f"sug_{i}", use_container_width=True):
                pergunta_rapida = s

    with col_chat:
        st.markdown("""
        <div style="background:#111827;border-radius:14px;padding:18px 22px;margin-bottom:18px;
            display:flex;align-items:center;gap:14px;">
          <div style="font-size:32px;">🤖</div>
          <div>
            <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;color:#fff;">Assistente GMAC</div>
            <div style="font-size:12px;color:rgba(255,255,255,.6)">Análise inteligente do ponto eletrônico</div>
          </div>
          <div style="margin-left:auto;background:rgba(255,255,255,.15);border-radius:20px;padding:4px 12px;">
            <span style="font-size:11px;color:#fff;font-family:monospace;">● ATIVO</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Área do chat com scroll fixo
        msgs_html = ""

        # Mensagem inicial
        msgs_html += """
        <div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:14px;">
          <div style="width:40px;height:40px;background:#111827;border-radius:50%;
              display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;">🤖</div>
          <div style="background:#fff;border:1px solid #e2e4e9;border-radius:4px 14px 14px 14px;
              padding:14px 18px;max-width:90%;font-size:14px;color:#111827;line-height:1.6;">
            <strong>Olá! Sou o assistente do GMAC.</strong> 👋<br><br>
            Tenho acesso completo aos registros de ponto — entradas, saídas, colaboradores e localizações.<br><br>
            Use os botões ao lado ou me faça uma pergunta! 🔥
          </div>
        </div>"""

        # Histórico de mensagens
        for msg in st.session_state.chat_hist:
            if msg["role"] == "user":
                msgs_html += f"""
                <div style="display:flex;justify-content:flex-end;margin:10px 0;gap:8px;">
                  <div style="background:#111827;color:#fff;border-radius:14px 14px 4px 14px;
                      padding:11px 16px;max-width:78%;font-size:14px;line-height:1.5;">
                    {msg['content']}
                  </div>
                  <div style="width:34px;height:34px;background:#e2e4e9;border-radius:50%;
                      display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">👤</div>
                </div>"""
            else:
                content = msg['content'].replace('\n', '<br>')
                msgs_html += f"""
                <div style="display:flex;align-items:flex-start;gap:10px;margin:10px 0;">
                  <div style="width:40px;height:40px;background:#111827;border-radius:50%;
                      display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;">🤖</div>
                  <div style="background:#fff;border:1px solid #e2e4e9;border-radius:4px 14px 14px 14px;
                      padding:14px 18px;max-width:85%;font-size:14px;color:#111827;line-height:1.7;">
                    {content}
                  </div>
                </div>"""

        # Container com scroll fixo — ancora no fundo automaticamente
        st.markdown(f"""
        <div id="chat-box" style="height:440px;overflow-y:auto;padding:16px;
            background:#f4f5f7;border-radius:12px;border:1px solid #e2e4e9;margin-bottom:12px;">
          {msgs_html}
          <div id="chat-end"></div>
        </div>
        <script>
          var box = document.getElementById('chat-box');
          if(box) box.scrollTop = box.scrollHeight;
        </script>
        """, unsafe_allow_html=True)

        # Input + botões na parte de baixo
        col_inp, col_btn, col_clr = st.columns([5, 1, 1])
        with col_inp:
            user_input = st.text_input(
                "msg", value=pergunta_rapida or "",
                placeholder="Faça uma pergunta sobre o ponto...",
                label_visibility="collapsed", key="chat_input"
            )
        with col_btn:
            enviar = st.button("Enviar", use_container_width=True, key="btn_enviar")
        with col_clr:
            if st.button("🗑️", use_container_width=True, key="btn_limpar"):
                st.session_state.chat_hist = []
                st.rerun()

    # ── LÓGICA DO CHAT ──────────────────────────────────────────
    query = user_input if (enviar or pergunta_rapida) and user_input else (pergunta_rapida if pergunta_rapida else None)

    if query:
        st.session_state.chat_hist.append({"role": "user", "content": query})
        q = query.lower()
        now_d = datetime.now().date()

        if df.empty:
            resp = "⚠️ Nenhum dado carregado. Clique em **Sincronizar** primeiro!"
        else:
            # Usa a data mais recente da base como referência de "hoje"
            data_mais_recente = df["_dt"].dropna().dt.date.max()
            df_hoje = df[df["_dt"].dt.date == data_mais_recente]
            hoje_str = data_mais_recente.strftime("%d/%m/%Y") if data_mais_recente else "—"

            total   = len(df)
            ent_tot = len(df[df["_status"] == "Entrada"])
            sai_tot = len(df[df["_status"] == "Saída"])
            colabs  = df["_nome"].nunique()
            ent_hoje = len(df_hoje[df_hoje["_status"] == "Entrada"]) if not df_hoje.empty else 0
            sai_hoje = len(df_hoje[df_hoje["_status"] == "Saída"])   if not df_hoje.empty else 0

            if any(w in q for w in ["hoje", "bateu ponto hoje", "registrou hoje"]):
                if df_hoje.empty:
                    resp = f"📅 Nenhum registro encontrado para o dia mais recente.\n\nVerifique se a planilha foi sincronizada!"
                else:
                    nomes_hoje = df_hoje["_nome"].unique().tolist()
                    lista = "\n".join([f"• {n}" for n in nomes_hoje])
                    resp = f"📅 **Registros mais recentes ({hoje_str}):**\n\n{lista}\n\n✅ {ent_hoje} entradas · 🔴 {sai_hoje} saídas"

            elif any(w in q for w in ["quantas", "total", "entradas", "saídas", "resumo geral"]):
                datas_unicas = df["_dt"].dt.date.nunique()
                resp = f"""📊 **Resumo Geral do Ponto:**

🔢 Total de registros: **{total}**
✅ Entradas: **{ent_tot}**
🔴 Saídas: **{sai_tot}**
👥 Colaboradores únicos: **{colabs}**
📅 Dias com registro: **{datas_unicas}**

📍 Registros com localização: **{df[['_lat']].dropna().shape[0]}**"""

            elif any(w in q for w in ["só saída", "só registrou saída", "sem entrada"]):
                df_sai = df[df["_status"] == "Saída"]["_nome"].unique()
                df_ent = df[df["_status"] == "Entrada"]["_nome"].unique()
                so_saida = [n for n in df_sai if n not in df_ent]
                if so_saida:
                    lista = "\n".join([f"⚠️ {n}" for n in so_saida])
                    resp = f"🔴 **Colaboradores com saída mas sem entrada registrada:**\n\n{lista}"
                else:
                    resp = "✅ Todos os colaboradores com saída também têm entrada registrada!"

            elif any(w in q for w in ["último registro", "último", "mais recente"]):
                ultimo = df.sort_values("_dt", ascending=False).groupby("_nome").first().reset_index()
                linhas = ""
                for _, r in ultimo.iterrows():
                    dt_s = r["_dt"].strftime("%d/%m/%Y %H:%M") if pd.notna(r["_dt"]) else "—"
                    isE  = r["_status"] == "Entrada"
                    icon = "✅" if isE else "🔴"
                    linhas += f"\n{icon} **{r['_nome']}** — {dt_s} ({r['_status']})"
                resp = f"📅 **Último registro de cada colaborador:**\n{linhas}"

            elif any(w in q for w in ["mais cedo", "chegou cedo", "primeiro"]):
                df_ent = df[df["_status"] == "Entrada"].copy()
                if df_ent.empty:
                    resp = "Nenhuma entrada registrada."
                else:
                    mais_cedo = df_ent.sort_values("_dt").iloc[0]
                    resp = f"⏰ **Chegou mais cedo:**\n\n👤 **{mais_cedo['_nome']}**\n📅 {mais_cedo['_dt'].strftime('%d/%m/%Y às %H:%M')}"

            elif any(w in q for w in ["mais tarde", "chegou tarde", "último a chegar"]):
                df_ent = df[df["_status"] == "Entrada"].copy()
                if df_ent.empty:
                    resp = "Nenhuma entrada registrada."
                else:
                    mais_tarde = df_ent.sort_values("_dt", ascending=False).iloc[0]
                    resp = f"🕐 **Chegou mais tarde:**\n\n👤 **{mais_tarde['_nome']}**\n📅 {mais_tarde['_dt'].strftime('%d/%m/%Y às %H:%M')}"

            elif any(w in q for w in ["localização", "localiza", "coordenada", "mapa"]):
                df_loc = df.dropna(subset=["_lat","_lng"])
                nomes_loc = df_loc["_nome"].unique().tolist()
                sem_loc   = [n for n in df["_nome"].unique() if n not in nomes_loc]
                lista_com = "\n".join([f"📍 {n}" for n in nomes_loc])
                lista_sem = "\n".join([f"❌ {n}" for n in sem_loc]) if sem_loc else "Nenhum"
                resp = f"**Com localização registrada ({len(nomes_loc)}):**\n{lista_com}\n\n**Sem localização ({len(sem_loc)}):**\n{lista_sem}"

            elif any(w in q for w in ["resumo", "geral", "análise", "visão"]):
                data_max = df["_dt"].max().strftime("%d/%m/%Y") if pd.notna(df["_dt"].max()) else "—"
                data_min = df["_dt"].min().strftime("%d/%m/%Y") if pd.notna(df["_dt"].min()) else "—"
                resp = f"""📈 **Visão Geral — GMAC Ponto:**

👥 **{colabs} colaboradores** com registro
📋 **{total} registros** no total
✅ **{ent_tot} entradas** · 🔴 **{sai_tot} saídas**

📅 Período: {data_min} até {data_max}
📅 Último dia com registro: **{hoje_str}** ({ent_hoje} entradas · {sai_hoje} saídas)
📍 {df[['_lat']].dropna().shape[0]} registros com localização GPS

{"🟢 Tudo OK — entradas e saídas balanceadas!" if abs(ent_tot - sai_tot) <= 2 else "⚠️ Atenção — diferença entre entradas e saídas detectada!"}"""

            else:
                resp = f"""🤖 Entendi sua pergunta! Aqui um resumo rápido:

📋 **{total} registros** · 👥 **{colabs} colaboradores**
✅ **{ent_tot} entradas** · 🔴 **{sai_tot} saídas**

Use os botões ao lado para análises específicas! 💡"""

        st.session_state.chat_hist.append({"role": "assistant", "content": resp})
        st.rerun()
