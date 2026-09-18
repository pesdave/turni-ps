import streamlit as st
import pandas as pd
import calendar
from datetime import date, datetime
import io

# --- CONFIGURAZIONE UI ---
st.set_page_config(layout="wide", page_title="Gestionale Turni PS Sondalo", page_icon="🏥")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #ffffff; border-radius: 5px 5px 0px 0px; gap: 1px; }
    .stTabs [aria-selected="true"] { background-color: #e1f5fe; border-bottom: 2px solid #0288d1; }
    </style>
    """, unsafe_allow_html=True)

# --- REGOLE E COSTANTI ---
ORE_TURNO = 12.25
DEBITO_GG = 7.2
CODICI_TURNO = ["", "G12", "N12", "G12B", "N12B", "GTI", "NTI", "GSL", "NSL", "GBO", "NBO", "AO:6", "PEDI", "MAL", "FERIE", "R", "SN"]

# --- FUNZIONI CORE ---
def get_festivi(anno):
    return [date(anno, 1, 1), date(anno, 1, 6), date(anno, 4, 25), date(anno, 5, 1), 
            date(anno, 6, 2), date(anno, 6, 19), date(anno, 8, 15), date(anno, 11, 1), 
            date(anno, 12, 8), date(anno, 12, 25), date(anno, 12, 26)]

def calcola_debito_mensile(mese, anno, pt=100, ore_104=0):
    festivi = get_festivi(anno)
    num_gg = calendar.monthrange(anno, mese)[1]
    gg_lav = len([d for d in range(1, num_gg+1) if date(anno, mese, d).weekday() < 5 and date(anno, mese, d) not in festivi])
    return round((gg_lav * DEBITO_GG * (pt/100)) - ore_104, 2)

# --- INITIAL DATA ---
if 'staff' not in st.session_state:
    st.session_state.staff = pd.DataFrame([
        {"Nome": "MEROLLA MASSIMO", "MSA1": True, "MSA2": True, "Notti": True, "PT": 100, "H104": 0, "Role": "Coordinatore"},
        {"Nome": "BALDO GABRIELE", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "BROGGINI CHARLOTTE", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "CANCLINI FEDERICA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "FRANZINI MARTINO", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "GHILOTTI PAOLO", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "PIETROGIOVANNA CHIARA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "POLETTI RIZZI ALESSIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "RODIGARI GIULIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "SPINI NADIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "BARBARO GALANTINO SILVIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "CRUPI CARMEN", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "GAMBARRI CRISTINA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "GERALI ALESSIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "INNOCENTI DANIELA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "MIOTTI SOFIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "PANIZZA CATERINA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "PESARO DAVIDE", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "SCARAMUZZI JACOPO", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"},
        {"Nome": "STEDILE PATRIZIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Role": "Inf"}
    ])

# --- TABS ---
t_grid, t_staff, t_analytics = st.tabs(["🗓️ Griglia Turni", "👥 Personale", "📊 Analisi & Copertura"])

with t_staff:
    st.header("Gestione Anagrafica")
    st.session_state.staff = st.data_editor(st.session_state.staff, num_rows="dynamic", use_container_width=True)

with t_grid:
    c1, c2 = st.columns([1, 4])
    m = c1.selectbox("Mese", range(1, 13), index=datetime.now().month-1)
    y = c1.number_input("Anno", value=2026)
    
    num_gg = calendar.monthrange(y, m)[1]
    days = [f"{d}" for d in range(1, num_gg+1)]
    staff_names = st.session_state.staff["Nome"].tolist()
    
    if 'griglia' not in st.session_state or st.session_state.get('cur_m') != m:
        st.session_state.griglia = pd.DataFrame("", index=staff_names, columns=days)
        st.session_state.cur_m = m
    
    st.session_state.griglia = st.session_state.griglia.reindex(staff_names).fillna("")

    # --- ALGORITMO DI GENERAZIONE SEQUENZIALE ---
    if st.button("🚀 GENERA TURNI (PS 3+3, OBI 1+1, AMB 2+2)"):
        with st.spinner("Generazione in corso rispettando sequenza G-N-SN-R..."):
            for d_idx, d in enumerate(days):
                # Fabbisogno giornaliero
                necessari = ["G12"]*3 + ["N12"]*3 + ["G12B"] + ["N12B"] + ["GTI", "GSL", "NTI", "NSL"]
                
                for turno in necessari:
                    # Se il turno è già stato assegnato manualmente, saltalo
                    if (st.session_state.griglia[d] == turno).any(): continue
                    
                    # Filtra candidati validi
                    candidati = st.session_state.staff.copy()
                    
                    for _, inf in candidati.iterrows():
                        nome = inf["Nome"]
                        
                        # 1. Non deve avere altri turni oggi
                        if st.session_state.griglia.at[nome, d] != "": continue
                        
                        # 2. Controllo sequenza: se ieri ha fatto Notte, oggi deve fare SN
                        if d_idx > 0:
                            ieri = days[d_idx-1]
                            turno_ieri = st.session_state.griglia.at[nome, ieri]
                            if "N" in str(turno_ieri) and turno != "SN": continue
                        
                        # 3. Competenze
                        if turno in ["GTI", "GSL", "NTI", "NSL"] and not inf["MSA1"]: continue
                        if "N" in turno and not inf["Notti"]: continue
                        
                        # Assegnazione
                        st.session_state.griglia.at[nome, d] = turno
                        # Se è Notte, prenota SN e R per i giorni successivi
                        if "N" in turno:
                            if d_idx + 1 < num_gg: st.session_state.griglia.at[nome, days[d_idx+1]] = "SN"
                            if d_idx + 2 < num_gg: st.session_state.griglia.at[nome, days[d_idx+2]] = "R"
                        break
        st.success("Turni generati con successo!")

    config = {d: st.column_config.SelectboxColumn(d, options=CODICI_TURNO, width="small") for d in days}
    grid_edit = st.data_editor(st.session_state.griglia, column_config=config, use_container_width=True, height=700)
    st.session_state.griglia = grid_edit

with t_analytics:
    st.header("Verifica Copertura")
    check_list = []
    for d in days:
        c = grid_edit[d].tolist()
        check_list.append({
            "Giorno": d,
            "PS G12 (req 3)": c.count("G12"),
            "PS N12 (req 3)": c.count("N12"),
            "OBI (1+1)": f"{c.count('G12B')}/{c.count('N12B')}",
            "Ambulanze (req 4)": c.count("GTI")+c.count("GSL")+c.count("NTI")+c.count("NSL")
        })
    st.dataframe(pd.DataFrame(check_list).set_index("Giorno").T, use_container_width=True)

    st.header("Bilancio Ore Mensili")
    report = []
    for _, inf in st.session_state.staff.iterrows():
        fatte = sum([ORE_TURNO for t in grid_edit.loc[inf["Nome"]] if any(x in str(t) for x in ["12", "GTI", "GSL", "NTI", "NSL", "BO"])])
        debito = calcola_debito_mensile(m, y, inf["PT"], inf["H104"])
        report.append({"Nome": inf["Nome"], "Debito": debito, "Ore Fatte": fatte, "Saldo": round(fatte-debito, 2)})
    st.table(pd.DataFrame(report))

if st.sidebar.button("📥 Esporta Excel"):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
        grid_edit.to_excel(wr, sheet_name='Turni')
    st.sidebar.download_button("Scarica", buf.getvalue(), f"Turni_{m}_{y}.xlsx")
