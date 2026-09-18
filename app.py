import streamlit as st
import pandas as pd
import calendar
from datetime import date, datetime
import io

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(layout="wide", page_title="ShiftMaster PS Sondalo-Tirano", page_icon="🏥")

# --- COSTANTI ---
ORE_TURNO = 12.25
ORE_DEBITO_GG = 7.2
CODICI_TURNO = [
    "", "G12", "N12", "G12B", "N12B", "GTI", "NTI", "GSL", "NSL", 
    "GBO", "NBO", "AO:2", "AO:4", "AO:6", "AO:8", "PEDI", "MAL", "FERIE", "R", "SN"
]

# --- FUNZIONI DI CALCOLO ---
def get_festivita(anno):
    # Calcolo base festività italiane + Patrono Sondrio (19/06)
    return [date(anno, 1, 1), date(anno, 1, 6), date(anno, 4, 25), date(anno, 5, 1), 
            date(anno, 6, 2), date(anno, 6, 19), date(anno, 8, 15), date(anno, 11, 1), 
            date(anno, 12, 8), date(anno, 12, 25), date(anno, 12, 26)]

def calcola_debito_mensile(mese, anno, pt=100, ore_104=0):
    festivi = get_festivita(anno)
    num_giorni = calendar.monthrange(anno, mese)[1]
    giorni_feriali = 0
    for d in range(1, num_giorni + 1):
        dt = date(anno, mese, d)
        if dt.weekday() < 5 and dt not in festivi:
            giorni_feriali += 1
    return round((giorni_feriali * ORE_DEBITO_GG * (pt/100)) - ore_104, 2)

# --- INIZIALIZZAZIONE STAFF (LISTA COMPLETA DAL PDF) ---
if 'staff' not in st.session_state:
    data_staff = [
        # Coordinatore
        {"Nome": "MEROLLA MASSIMO", "MSA1": True, "MSA2": True, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Coordinatore"},
        # Infermieri PS
        {"Nome": "BALDO GABRIELE", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "BROGGINI CHARLOTTE", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "CANCLINI FEDERICA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "FRANZINI MARTINO", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "GHILOTTI PAOLO", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "PIETROGIOVANNA CHIARA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "POLETTI RIZZI ALESSIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "RODIGARI GIULIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "SPINI NADIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "BARBARO GALANTINO SILVIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "CRUPI CARMEN", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "GAMBARRI CRISTINA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "GERALI ALESSIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "INNOCENTI DANIELA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "MIOTTI SOFIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "PANIZZA CATERINA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "PESARO DAVIDE", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "SCARAMUZZI JACOPO", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "STEDILE PATRIZIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        # Turni Bormio
        {"Nome": "BELTRACCHI VITTORIA", "MSA1": True, "MSA2": True, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Bormio"},
        {"Nome": "BORSERINI FRANCESCA", "MSA1": True, "MSA2": True, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Bormio"},
        {"Nome": "CAPELLI GIOVANNA", "MSA1": True, "MSA2": True, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Bormio"},
        {"Nome": "GALASSO DONATELLA", "MSA1": True, "MSA2": True, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Bormio"},
        {"Nome": "PES SILVIA", "MSA1": True, "MSA2": True, "Notti": False, "PT": 100, "H104": 0, "Gruppo": "Bormio"}
    ]
    st.session_state.staff = pd.DataFrame(data_staff)

# --- INTERFACCIA TABS ---
tab_turni, tab_anagrafica, tab_analisi = st.tabs(["🗓️ Turni Mensili", "👥 Anagrafica Personale", "📊 Calcolo Debito & Ore"])

# --- TAB ANAGRAFICA ---
with tab_anagrafica:
    st.header("Configurazione Personale")
    st.info("Qui puoi modificare le competenze, i part-time o aggiungere nuovi colleghi.")
    updated_staff = st.data_editor(st.session_state.staff, num_rows="dynamic", use_container_width=True)
    st.session_state.staff = updated_staff

# --- TAB TURNI ---
with tab_turni:
    col_m, col_a = st.columns(2)
    mese = col_m.selectbox("Mese", range(1, 13), index=datetime.now().month - 1, key="sel_mese")
    anno = col_a.number_input("Anno", value=2026, key="sel_anno")
    
    num_gg = calendar.monthrange(anno, mese)[1]
    colonne_gg = [f"{d}" for d in range(1, num_gg + 1)]
    elenco_nomi = st.session_state.staff["Nome"].tolist()
    
    # Inizializzazione sicura della griglia
    if 'griglia' not in st.session_state or st.session_state.get('last_m') != mese:
        st.session_state.griglia = pd.DataFrame("", index=elenco_nomi, columns=colonne_gg)
        st.session_state.last_m = mese
    
    # Sincronizzazione righe (se aggiungo/tolgo in anagrafica)
    st.session_state.griglia = st.session_state.griglia.reindex(elenco_nomi).fillna("")
    
    st.subheader("Inserimento Turni")
    st.caption("Fai doppio clic su una cella per selezionare il turno dal menu a tendina.")
    
    # Configurazione colonne per menu a tendina
    config_colonne = {
        c: st.column_config.SelectboxColumn(c, options=CODICI_TURNO, width="small") 
        for d, c in enumerate(colonne_gg)
    }
    
    grid_final = st.data_editor(
        st.session_state.griglia,
        column_config=config_colonne,
        use_container_width=True,
        key="main_grid"
    )
    st.session_state.griglia = grid_final

# --- TAB ANALISI ---
with tab_analisi:
    st.header("Bilancio Orario Real-Time")
    
    report = []
    for _, inf in st.session_state.staff.iterrows():
        nome = inf['Nome']
        h_lavorate = 0
        h_pedi = 0
        
        # Calcolo sicuro delle ore
        if nome in grid_final.index:
            riga = grid_final.loc[nome]
            for val in riga:
                if any(x in str(val) for x in ["G12", "N12", "GTI", "NTI", "GSL", "NSL", "GBO", "NBO"]):
                    h_lavorate += ORE_TURNO
                elif "AO:" in str(val):
                    try: h_lavorate += float(val.split(":")[1])
                    except: pass
                elif "PEDI" in str(val):
                    h_pedi += ORE_TURNO
        
        debito = calcola_debito_mensile(mese, anno, inf['PT'], inf['H104'])
        bilancio = h_lavorate - debito
        
        report.append({
            "Nome": nome,
            "Debito Mensile": debito,
            "Ore Effettive": h_lavorate,
            "Bilancio (+/-)": round(bilancio, 2),
            "PEDI Totali": h_pedi,
            "Stato": "PREMIANTE (P)" if bilancio > 0 else "DEBITO"
        })
    
    df_report = pd.DataFrame(report)
    
    # Formattazione colori
    def color_bilancio(val):
        color = 'red' if val < 0 else 'green'
        return f'color: {color}; font-weight: bold'

    st.dataframe(df_report.style.applymap(color_bilancio, subset=['Bilancio (+/-)']), use_container_width=True)

    # Suggeritore Sostituzioni
    st.divider()
    st.subheader("🚑 Suggeritore per Sostituzioni")
    col_s1, col_s2 = st.columns(2)
    g_buco = col_s1.selectbox("Giorno del buco", colonne_gg)
    p_buco = col_s2.selectbox("Tipo di postazione", ["PS/OBI", "Ambulanza (MSA1)", "Bormio (MSA2)"])
    
    if st.button("Trova chi può coprire il turno"):
        candidati = []
        for _, r in st.session_state.staff.iterrows():
            nome = r['Nome']
            # Non deve già lavorare quel giorno
            if grid_final.loc[nome, g_buco] == "":
                # Controllo MSA
                idoneo = True
                if "Ambulanza" in p_buco and not r['MSA1']: idoneo = False
                if "Bormio" in p_buco and not r['MSA2']: idoneo = False
                
                if idoneo:
                    bil = df_report.loc[df_report['Nome'] == nome, 'Bilancio (+/-)'].values[0]
                    candidati.append({"Infermiere": nome, "Bilancio Ore": bil})
        
        if candidati:
            st.table(pd.DataFrame(candidati).sort_values("Bilancio Ore"))
        else:
            st.error("Nessun sostituto disponibile per i criteri selezionati.")

# --- SIDEBAR EXPORT ---
st.sidebar.header("💾 Salvataggio")
if st.sidebar.button("Genera Excel Professionale"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        grid_final.to_excel(writer, sheet_name='Turni')
        df_report.to_excel(writer, sheet_name='Conteggio_Ore')
    st.sidebar.download_button(
        label="📥 Scarica File",
        data=buffer.getvalue(),
        file_name=f"Turni_PS_{mese}_{anno}.xlsx",
        mime="application/vnd.ms-excel"
    )
