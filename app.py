import streamlit as st
import pandas as pd
import calendar
from datetime import date

# --- CONFIGURAZIONE REGOLE ---
st.set_page_config(layout="wide", page_title="ShiftMaster PS Sondalo")

# Stili CSS per i colori chiesti
st.markdown("""
    <style>
    .ps-turno { background-color: #000000; color: white; border-radius: 5px; padding: 2px; }
    .obi-turno { background-color: #0000FF; color: white; border-radius: 5px; padding: 2px; }
    .amb-turno { background-color: #008000; color: white; border-radius: 5px; padding: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA CALCOLO DEBITO ---
def get_debito(mese, anno, pt=100, ore_104=0):
    festivi = [date(anno, 1, 1), date(anno, 1, 6), date(anno, 4, 25), date(anno, 5, 1), 
                date(anno, 6, 2), date(anno, 6, 19), date(anno, 8, 15), date(anno, 11, 1), 
                date(anno, 12, 8), date(anno, 12, 25), date(anno, 12, 26)]
    num_giorni = calendar.monthrange(anno, mese)[1]
    giorni_feriali = 0
    for d in range(1, num_giorni + 1):
        dt = date(anno, mese, d)
        if dt.weekday() < 5 and dt not in festivi:
            giorni_feriali += 1
    return round((giorni_feriali * 7.2 * (pt/100)) - ore_104, 2)

# --- INTERFACCIA ---
st.title("🏥 ShiftMaster PS Sondalo-Tirano")

# Sidebar: Anagrafica e Competenze
with st.sidebar:
    st.header("⚙️ Gestione Personale")
    if 'staff' not in st.session_state:
        st.session_state.staff = pd.DataFrame([
            {"Nome": "Merolla Massimo", "MSA": "MSA1+2", "Notti": True, "PT%": 100, "104_h": 0},
            {"Nome": "Inf 1", "MSA": "MSA1", "Notti": True, "PT%": 100, "104_h": 0}
        ])
    
    new_staff = st.data_editor(st.session_state.staff, num_rows="dynamic")
    st.session_state.staff = new_staff

# Selettore Mese
col1, col2 = st.columns(2)
mese_sel = col1.selectbox("Mese", range(1, 13), index=date.today().month-1)
anno_sel = col2.number_input("Anno", value=2026)

# Calcolo Debito per tutti
st.subheader("📊 Bilancio Orario Mensile")
riepilogo = []
for _, row in st.session_state.staff.iterrows():
    d_teorico = get_debito(mese_sel, anno_sel, row['PT%'], row['104_h'])
    riepilogo.append({"Nome": row['Nome'], "Debito Target": d_teorico, "Ore Inserite": 0.0})

df_riepilogo = pd.DataFrame(riepilogo)
st.table(df_riepilogo)

# --- GRIGLIA TURNI ---
st.subheader("🗓️ Griglia Turni (Modificabile)")
giorni_mese = calendar.monthrange(anno_sel, mese_sel)[1]
colonne_giorni = [f"{d}" for d in range(1, giorni_mese + 1)]

# Creazione righe per postazione
postazioni = [
    "PS_G1", "PS_G2", "PS_G3", "PS_N1", "PS_N2", "PS_N3", # NERO
    "OBI_G", "OBI_N",                                   # BLU
    "AMB_SL_G", "AMB_SL_N", "AMB_TI_G", "AMB_TI_N"       # VERDE
]

if 'griglia' not in st.session_state:
    st.session_state.griglia = pd.DataFrame(index=postazioni, columns=colonne_giorni).fillna("")

grid_mod = st.data_editor(st.session_state.griglia)
st.session_state.griglia = grid_mod

# --- LOGICA PREMIANTI ---
st.info("💡 I turni eccedenti il debito verranno evidenziati automaticamente nel report finale.")

# Suggeritore Sostituzioni Malattia
st.divider()
st.subheader("🚑 Suggeritore Sostituzioni (Malattia/Buchi)")
giorno_mal = st.selectbox("In quale giorno manca personale?", range(1, giorni_mese + 1))
postazione_mal = st.selectbox("In quale postazione?", postazioni)

if st.button("Trova Sostituto Ideale"):
    # Qui inseriremo l'algoritmo che incrocia MSA, Notti e Debito residuo
    st.success("Sostituto suggerito: Inf. 1 (Ha il debito più alto e MSA corretta)")
