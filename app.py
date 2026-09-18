import streamlit as st
import pandas as pd
import calendar
from datetime import date, datetime
import io

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(layout="wide", page_title="Gestionale Turni Sondalo-Tirano")

# --- COSTANTI TECNICHE ---
ORE_TURNO = 12.25
ORE_GIORNALIERE_DEBITO = 7.2
PATRONO = (6, 19) # 19 Giugno

# --- FUNZIONI DI SERVIZIO ---
def get_festivita(anno):
    return [date(anno, 1, 1), date(anno, 1, 6), date(anno, 4, 25), date(anno, 5, 1), 
            date(anno, 6, 2), date(anno, 6, 19), date(anno, 8, 15), date(anno, 11, 1), 
            date(anno, 12, 8), date(anno, 12, 25), date(anno, 12, 26)]

def calcola_debito(mese, anno, pt=100, ore_104=0):
    festivi = get_festivita(anno)
    num_giorni = calendar.monthrange(anno, mese)[1]
    giorni_feriali = 0
    for d in range(1, num_giorni + 1):
        dt = date(anno, mese, d)
        if dt.weekday() < 5 and dt not in festivi:
            giorni_feriali += 1
    return round((giorni_feriali * ORE_GIORNALIERE_DEBITO * (pt/100)) - ore_104, 2)

# --- INIZIALIZZAZIONE STATO ---
if 'staff' not in st.session_state:
    st.session_state.staff = pd.DataFrame([
        {"Nome": "MEROLLA MASSIMO", "MSA1": True, "MSA2": True, "Notti": True, "PT": 100, "H104": 0, "Ruolo": "Coordinatore"},
        {"Nome": "BALDO GABRIELE", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Ruolo": "Infermiere"},
        {"Nome": "PES SILVIA", "MSA1": True, "MSA2": False, "Notti": False, "PT": 100, "H104": 0, "Ruolo": "Infermiere"}
    ])

# --- STRUTTURA A SCHEDE (TABS) ---
tab_turni, tab_anagrafica, tab_report = st.tabs(["📅 Gestione Turni", "👥 Anagrafica & Parametri", "📊 Report & Suggeritore"])

# --- TABELLA ANAGRAFICA ---
with tab_anagrafica:
    st.header("Gestione Profili Infermieri")
    st.write("Configura qui le competenze e i vincoli contrattuali.")
    st.session_state.staff = st.data_editor(st.session_state.staff, num_rows="dynamic", use_container_width=True)

# --- TABELLA TURNI (STILE PDF) ---
with tab_turni:
    col_m, col_a = st.columns(2)
    mese_sel = col_m.selectbox("Mese", range(1, 13), index=datetime.now().month - 1)
    anno_sel = col_a.number_input("Anno", value=2026)

    giorni_mese = calendar.monthrange(anno_sel, mese_sel)[1]
    colonne = [f"{d}" for d in range(1, giorni_mese + 1)]
    nomi_staff = st.session_state.staff["Nome"].tolist()

    if 'griglia' not in st.session_state or st.session_state.get('current_m') != mese_sel:
        st.session_state.griglia = pd.DataFrame("", index=nomi_staff, columns=colonne)
        st.session_state.current_m = mese_sel

    st.warning("Codici: G12/N12 (PS), G12B/N12B (OBI), GTI/NTI (Tirano), GSL/NSL (Sondalo), GBO/NBO (Bormio), AO:ore, PEDI, MAL")
    
    # Editor della griglia principale
    grid_edit = st.data_editor(st.session_state.griglia, use_container_width=True)
    st.session_state.griglia = grid_edit

    # --- VALIDAZIONE COPERTURA ---
    st.subheader("✅ Verifica Copertura Giornaliera")
    check_data = []
    for d in colonne:
        col_turni = grid_edit[d].tolist()
        check_data.append({
            "Giorno": d,
            "PS_G (req 3)": col_turni.count("G12"),
            "PS_N (req 3)": col_turni.count("N12"),
            "OBI (req 1+1)": f"{col_turni.count('G12B')}+{col_turni.count('N12B')}",
            "Amb (req 2+2)": col_turni.count("GTI")+col_turni.count("GSL")+col_turni.count("NTI")+col_turni.count("NSL")
        })
    st.dataframe(pd.DataFrame(check_data).T, use_container_width=True)

# --- REPORT & SUGGERITORE ---
with tab_report:
    st.header("Analisi Debito e Sostituzioni")
    
    # Calcolo Ore Reali
    report_list = []
    for _, inf in st.session_state.staff.iterrows():
        ore_lavorate = 0
        pedi_count = 0
        for d in colonne:
            val = str(grid_edit.loc[inf['Nome'], d])
            if any(x in val for x in ["G12", "N12", "GTI", "NTI", "GSL", "NSL", "GBO", "NBO"]):
                ore_lavorate += ORE_TURNO
            if "AO:" in val:
                try: ore_lavorate += float(val.split(":")[1])
                except: pass
            if "PEDI" in val: pedi_count += ORE_TURNO

        debito_inf = calcola_debito(mese_sel, anno_sel, inf['PT'], inf['H104'])
        bilancio = ore_lavorate - debito_inf
        
        report_list.append({
            "Infermiere": inf['Nome'],
            "Debito Target": debito_inf,
            "Ore Totali": ore_lavorate,
            "Bilancio": round(bilancio, 2),
            "PEDI (h)": pedi_count,
            "Note": "⚠️ SOGLIA PEDI SUPERATA" if pedi_count > 30 else "OK"
        })

    st.table(pd.DataFrame(report_list))

    # SUGGERITORE
    st.divider()
    st.subheader("🚑 Trova Sostituto per Malattia/Buco")
    g_sost = st.selectbox("Giorno", colonne)
    tipo_sost = st.selectbox("Tipo Turno", ["PS/OBI", "Ambulanza (MSA1)", "Bormio (MSA2)"])
    
    if st.button("Suggerisci Personale"):
        disp = []
        for _, row in st.session_state.staff.iterrows():
            # Filtri: non deve lavorare quel giorno + competenze
            gia_lavora = grid_edit.loc[row['Nome'], g_sost] != ""
            
            check_msa = True
            if "Ambulanza" in tipo_sost and not row['MSA1']: check_msa = False
            if "Bormio" in tipo_sost and not row['MSA2']: check_msa = False
            
            if not gia_lavora and check_msa:
                b = next(item for item in report_list if item["Infermiere"] == row['Nome'])["Bilancio"]
                disp.append({"Nome": row['Nome'], "Bilancio Ore": b})
        
        if disp:
            st.write("Infermieri disponibili (ordinati per chi deve recuperare ore):")
            st.table(pd.DataFrame(disp).sort_values("Bilancio Ore"))
        else:
            st.error("Nessun sostituto idoneo trovato.")

# --- EXPORT ---
st.sidebar.divider()
if st.sidebar.button("💾 Genera File Excel"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        grid_edit.to_excel(writer, sheet_name='Turni_Mese')
        pd.DataFrame(report_list).to_excel(writer, sheet_name='Bilancio_Ore')
    st.sidebar.download_button(label="📥 Scarica Excel", data=output.getvalue(), file_name="turni_ps.xlsx")
