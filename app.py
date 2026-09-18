import streamlit as st
import pandas as pd
import calendar
from datetime import date, datetime
import io

# --- CONFIGURAZIONE ESTETICA ---
st.set_page_config(layout="wide", page_title="Gestionale Turni PS")

st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stDataEditor { border: 2px solid #000; }
    </style>
    """, unsafe_allow_html=True)

# --- COSTANTI ---
ORE_TURNO = 12.25  # 12h 15min
ORE_GIORNALIERE_DEBITO = 7.2

# --- FUNZIONI DI CALCOLO ---
def calcola_debito_mensile(mese, anno, pt=100, ore_104=0):
    festivi = [date(anno, 1, 1), date(anno, 1, 6), date(anno, 4, 25), date(anno, 5, 1), 
                date(anno, 6, 2), date(anno, 6, 19), date(anno, 8, 15), date(anno, 11, 1), 
                date(anno, 12, 8), date(anno, 12, 25), date(anno, 12, 26)]
    num_giorni = calendar.monthrange(anno, mese)[1]
    giorni_feriali = 0
    for d in range(1, num_giorni + 1):
        dt = date(anno, mese, d)
        if dt.weekday() < 5 and dt not in festivi:
            giorni_feriali += 1
    return round((giorni_feriali * ORE_GIORNALIERE_DEBITO * (pt/100)) - ore_104, 2)

# --- STATO DELL'APPLICAZIONE (Memory) ---
if 'staff' not in st.session_state:
    st.session_state.staff = pd.DataFrame([
        {"Nome": "Merolla Massimo", "MSA": "MSA1+2", "Notti": True, "PT%": 100, "104_h": 0, "PEDI_Res": 30},
        {"Nome": "Esempio Inf MSA1", "MSA": "MSA1", "Notti": True, "PT%": 100, "104_h": 0, "PEDI_Res": 30},
        {"Nome": "Esempio Inf NoNotti", "MSA": "MSA1", "Notti": False, "PT%": 100, "104_h": 0, "PEDI_Res": 30}
    ])

# --- INTERFACCIA SIDEBAR ---
with st.sidebar:
    st.header("👥 Anagrafica Personale")
    st.session_state.staff = st.data_editor(st.session_state.staff, num_rows="dynamic")
    
    st.header("📅 Selezione Periodo")
    mese_sel = st.selectbox("Mese", range(1, 13), index=datetime.now().month - 1)
    anno_sel = st.number_input("Anno", value=2026)
    
    debito_base = calcola_debito_mensile(mese_sel, anno_sel)
    st.metric("Debito Base Mese (Full Time)", f"{debito_base} h")

# --- GRIGLIA TURNI ---
st.title(f"Turni Pronto Soccorso - {calendar.month_name[mese_sel]} {anno_sel}")

num_giorni = calendar.monthrange(anno_sel, mese_sel)[1]
colonne_giorni = [f"{d}" for d in range(1, num_giorni + 1)]
postazioni = [
    "PS_G1", "PS_G2", "PS_G3", "PS_N1", "PS_N2", "PS_N3", 
    "OBI_G", "OBI_N", 
    "AMB_SL_G", "AMB_SL_N", "AMB_TI_G", "AMB_TI_N",
    "BORMIO_G", "BORMIO_N", "PREMIANTI_EXT"
]

if 'griglia' not in st.session_state or st.session_state.get('last_mese') != mese_sel:
    st.session_state.griglia = pd.DataFrame("", index=postazioni, columns=colonne_giorni)
    st.session_state.last_mese = mese_sel

# Editor della Griglia
st.write("👉 Inserisci i nomi degli infermieri nelle celle. Usa 'AO:5' per 5 ore di aggiornamento.")
grid_edit = st.data_editor(st.session_state.griglia, use_container_width=True)
st.session_state.griglia = grid_edit

# --- LOGICA DI CALCOLO ORE REAL-TIME ---
st.divider()
st.subheader("📈 Monitoraggio Ore e Debito")

calcolo_ore = []
for _, inf in st.session_state.staff.iterrows():
    nome = inf['Nome']
    ore_fatte = 0
    # Conta quante volte appare il nome nella griglia
    for col in colonne_giorni:
        for row in postazioni:
            cella = str(grid_edit.loc[row, col])
            if nome in cella:
                if "AO:" in cella: # Gestione AO con ore manuali
                    try: ore_fatte += float(cella.split(":")[1])
                    except: pass
                elif "PEDI" in cella or "MAL" in cella:
                    pass # La malattia non somma ore lavorate
                else:
                    ore_fatte += ORE_TURNO
    
    debito_personale = calcola_debito_mensile(mese_sel, anno_sel, inf['PT%'], inf['104_h'])
    differenza = ore_fatte - debito_personale
    
    calcolo_ore.append({
        "Infermiere": nome,
        "Debito Target": debito_personale,
        "Ore Totali": ore_fatte,
        "Bilancio": round(differenza, 2),
        "Stato": "ECCEDENZA (P)" if differenza > 0 else "DA COPRIRE"
    })

df_status = pd.DataFrame(calcolo_ore)
st.dataframe(df_status.style.applymap(lambda x: 'color: red' if isinstance(x, float) and x < 0 else 'color: green', subset=['Bilancio']))

# --- IL SUGGERITORE (MALATTIA / SOSTITUZIONI) ---
st.divider()
col_sx, col_dx = st.columns(2)

with col_sx:
    st.subheader("🚑 Suggeritore Sostituzioni")
    giorno_sost = st.selectbox("Giorno del buco", colonne_giorni)
    post_sost = st.selectbox("Postazione da coprire", postazioni)
    
    if st.button("Chi può lavorare?"):
        # Logica Suggeritore
        necessita_msa = "AMB" in post_sost or "BORMIO" in post_sost
        necessita_notti = "_N" in post_sost
        
        possibili = []
        for _, inf in st.session_state.staff.iterrows():
            # 1. Controllo se già lavora quel giorno
            lavora_gia = False
            for p in postazioni:
                if inf['Nome'] in str(grid_edit.loc[p, giorno_sost]):
                    lavora_gia = True
            
            # 2. Controllo MSA
            ha_msa = True
            if necessita_msa and "MSA1" not in inf['MSA']:
                ha_msa = False
                
            # 3. Controllo Notti
            puo_notti = True
            if necessita_notti and not inf['Notti']:
                puo_notti = False
                
            if not lavora_gia and ha_msa and puo_notti:
                # Recupero il bilancio ore
                bilancio = next(item for item in calcolo_ore if item["Infermiere"] == inf['Nome'])["Bilancio"]
                possibili.append({"Nome": inf['Nome'], "Bilancio Ore": bilancio})
        
        if possibili:
            # Ordina per chi ha più debito (Bilancio più basso)
            possibili_df = pd.DataFrame(possibili).sort_values(by="Bilancio Ore")
            st.write("✅ Infermieri disponibili (ordinati per chi deve recuperare ore):")
            st.table(possibili_df)
        else:
            st.error("Nessun sostituto trovato con i requisiti necessari!")

with col_dx:
    st.subheader("📥 Esporta Turno")
    # Funzione semplice per export Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        grid_edit.to_excel(writer, sheet_name='Turni')
        df_status.to_excel(writer, sheet_name='Conto_Ore')
    st.download_button(
        label="Scarica Excel per Stampa",
        data=output.getvalue(),
        file_name=f"turni_{mese_sel}_{anno_sel}.xlsx",
        mime="application/vnd.ms-excel"
    )
