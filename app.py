import streamlit as st
import pandas as pd
import calendar
from datetime import date, datetime
import io
import numpy as np

# --- CONFIGURAZIONE UI AVANZATA ---
st.set_page_config(layout="wide", page_title="PRO-Shift | Pronto Soccorso", page_icon="🏥")

st.markdown("""
    <style>
    /* Global Style */
    .main { background-color: #f0f2f6; }
    .stTable { font-size: 12px !important; }
    
    /* Badge Styles per i Turni */
    .badge { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; color: white; }
    .badge-g12 { background-color: #FF9800; } /* Arancio */
    .badge-n12 { background-color: #2c3e50; } /* Blu notte */
    .badge-amb { background-color: #27ae60; } /* Verde */
    .badge-obi { background-color: #2980b9; } /* Azzurro */
    .badge-off { background-color: #bdc3c7; color: #34495e; } /* Grigio */

    /* Card Style per statistiche */
    .stat-card { background: white; padding: 20px; border-radius: 10px; border-left: 5px solid #0288d1; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- REGOLE E COSTANTI ---
ORE_TURNO = 12.25
DEBITO_GG = 7.2
CODICI_TURNO = ["", "G12", "N12", "G12B", "N12B", "GTI", "NTI", "GSL", "NSL", "GBO", "NBO", "AO:6", "PEDI", "MAL", "FERIE", "R", "SN"]

def get_festivi(anno):
    return [date(anno, 1, 1), date(anno, 1, 6), date(anno, 4, 25), date(anno, 5, 1), 
            date(anno, 6, 2), date(anno, 6, 19), date(anno, 8, 15), date(anno, 11, 1), 
            date(anno, 12, 8), date(anno, 12, 25), date(anno, 12, 26)]

# --- DATA INITIALIZATION ---
if 'staff' not in st.session_state:
    st.session_state.staff = pd.DataFrame([
        {"Nome": "MEROLLA MASSIMO", "MSA1": True, "MSA2": True, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "BALDO GABRIELE", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "BROGGINI CHARLOTTE", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "CANCLINI FEDERICA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "FRANZINI MARTINO", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "GHILOTTI PAOLO", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "PIETROGIOVANNA CHIARA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "POLETTI RIZZI ALESSIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "RODIGARI GIULIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "SPINI NADIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "BARBARO GALANTINO SILVIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "CRUPI CARMEN", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "GAMBARRI CRISTINA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "GERALI ALESSIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "INNOCENTI DANIELA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "MIOTTI SOFIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "PANIZZA CATERINA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "PESARO DAVIDE", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "SCARAMUZZI JACOPO", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "STEDILE PATRIZIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0}
    ])

# --- APP LAYOUT ---
st.title("🏥 PRO-Shift v2.0 | Sondalo-Tirano")
t1, t2 = st.tabs(["📊 Dashboard Turni", "👥 Setup Personale"])

with t2:
    st.subheader("Configurazione Anagrafica")
    st.session_state.staff = st.data_editor(st.session_state.staff, num_rows="dynamic", use_container_width=True)

with t1:
    # Sidebar selectors
    c_m, c_a = st.sidebar.columns(2)
    m = c_m.selectbox("Mese", range(1, 13), index=datetime.now().month-1)
    y = c_a.number_input("Anno", value=2026)
    
    num_gg = calendar.monthrange(y, m)[1]
    days = [f"{d}" for d in range(1, num_gg+1)]
    
    if 'griglia' not in st.session_state or st.session_state.get('last_m') != m:
        st.session_state.griglia = pd.DataFrame("", index=st.session_state.staff["Nome"].tolist(), columns=days)
        st.session_state.last_m = m

    # Sincronizzazione
    st.session_state.griglia = st.session_state.griglia.reindex(st.session_state.staff["Nome"].tolist()).fillna("")

    # --- ENGINE DI GENERAZIONE EQUA ---
    if st.sidebar.button("🪄 GENERA TURNI EQUILIBRATI"):
        # Reset turni non bloccati (G12, N12, OBI, AMB)
        for d in days:
            # Requisiti giornalieri
            reqs = ["G12"]*3 + ["N12"]*3 + ["G12B"] + ["N12B"] + ["GTI", "GSL", "NTI", "NSL"]
            
            for turno in reqs:
                # 1. Calcoliamo le ore attuali di tutti per scegliere il più scarico
                current_hours = {}
                for n in st.session_state.staff["Nome"]:
                    row = st.session_state.griglia.loc[n]
                    current_hours[n] = sum([ORE_TURNO for t in row if any(x in str(t) for x in ["12", "GT", "GS", "NT", "NS"])])
                
                # 2. Ordiniamo lo staff dal più scarico al più carico
                sorted_staff = sorted(current_hours.items(), key=lambda x: x[1])
                
                success = False
                for nome, ore in sorted_staff:
                    inf_info = st.session_state.staff[st.session_state.staff["Nome"] == nome].iloc[0]
                    
                    # Vincoli di idoneità
                    if st.session_state.griglia.at[nome, d] != "": continue
                    if "N" in turno and not inf_info["Notti"]: continue
                    if any(x in turno for x in ["GT", "GS", "NT", "NS"]) and not inf_info["MSA1"]: continue
                    
                    # Vincolo Sequenza: N -> SN -> R
                    if int(d) > 1:
                        ieri = str(int(d)-1)
                        if "N" in str(st.session_state.griglia.at[nome, ieri]): continue
                    
                    # Assegnazione
                    st.session_state.griglia.at[nome, d] = turno
                    if "N" in turno: # Automatizzazione smonto
                        if int(d) + 1 <= num_gg: st.session_state.griglia.at[nome, str(int(d)+1)] = "SN"
                        if int(d) + 2 <= num_gg: st.session_state.griglia.at[nome, str(int(d)+2)] = "R"
                    success = True
                    break
        st.success("Bilanciamento completato.")

    # Visualizzazione Tabella Principale
    config = {d: st.column_config.SelectboxColumn(d, options=CODICI_TURNO, width="small") for d in days}
    grid_edit = st.data_editor(st.session_state.griglia, column_config=config, use_container_width=True, height=600)
    st.session_state.griglia = grid_edit

    # --- AREA ANALISI E COPERTURA ---
    st.divider()
    col_a, col_b = st.columns([2, 3])

    with col_a:
        st.subheader("🏁 Verifica Copertura")
        check = []
        for d in days:
            c = grid_edit[d].tolist()
            check.append({
                "G": d,
                "PS G/N": f"{c.count('G12')}/{c.count('N12')}",
                "OBI G/N": f"{c.count('G12B')}/{c.count('N12B')}",
                "AMB": c.count('GTI')+c.count('GSL')+c.count('NTI')+c.count('NSL')
            })
        st.table(pd.DataFrame(check).set_index("G").T)

    with col_b:
        st.subheader("⚖️ Bilancio Ore Mensili")
        rep = []
        for _, inf in st.session_state.staff.iterrows():
            fatte = sum([ORE_TURNO for t in grid_edit.loc[inf["Nome"]] if any(x in str(t) for x in ["12", "GT", "GS", "NT", "NS"])])
            debito = (len([d for d in range(1, num_gg+1) if date(y, m, d).weekday() < 5 and date(y, m, d) not in get_festivi(y)]) * DEBITO_GG) * (inf["PT"]/100)
            rep.append({"Nome": inf["Nome"], "Target": round(debito,1), "Fatte": fatte, "Saldo": round(fatte-debito, 1)})
        
        df_rep = pd.DataFrame(rep)
        # Colorazione per saldo
        def highlight_saldo(s):
            return 'background-color: #ffcdd2' if s < 0 else 'background-color: #c8e6c9'
        
        st.dataframe(df_rep.style.apply(lambda x: [highlight_saldo(v) for v in x], subset=['Saldo']), use_container_width=True)

# --- EXPORT ---
if st.sidebar.button("💾 Esporta per Stampa"):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
        grid_edit.to_excel(wr, sheet_name='Turni')
    st.sidebar.download_button("Scarica Excel", buf.getvalue(), f"Turni_{m}_{y}.xlsx")
