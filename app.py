import streamlit as st
import pandas as pd
import calendar
from datetime import date, datetime
import io

# --- CONFIGURAZIONE UI PROFESSIONALE ---
st.set_page_config(layout="wide", page_title="PRO-Shift v3.0 | Pronto Soccorso", page_icon="🚑")

# Custom CSS per UX/UI di alto livello
st.markdown("""
    <style>
    /* Main container */
    .main { background-color: #f8f9fa; }
    
    /* Header e Titoli */
    .main-title { font-size: 32px; font-weight: 800; color: #1e3a8a; margin-bottom: 20px; text-align: center; }
    
    /* Pannello Suggeritore */
    .suggeritore-panel { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    
    /* Bottone Genera - Stile Premium */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white; border: none; padding: 15px 40px; font-size: 20px; font-weight: bold;
        border-radius: 10px; width: 100%; box-shadow: 0 4px 15px rgba(217, 119, 6, 0.4);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(217, 119, 6, 0.6); }

    /* Badge Turni */
    .t-badge { padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- REGOLE E COSTANTI ---
ORE_TURNO = 12.25
DEBITO_GG = 7.2
CODICI_TURNO = ["", "G", "G12", "N12", "G12B", "N12B", "GTI", "NTI", "GSL", "NSL", "GBO", "NBO", "AO:6", "PEDI", "MAL", "FERIE", "R", "SN"]

def get_festivi(anno):
    # Calcolo festività nazionali + Patrono 19 Giugno
    return [date(anno, 1, 1), date(anno, 1, 6), date(anno, 4, 25), date(anno, 5, 1), 
            date(anno, 6, 2), date(anno, 6, 19), date(anno, 8, 15), date(anno, 11, 1), 
            date(anno, 12, 8), date(anno, 12, 25), date(anno, 12, 26)]

# --- INIZIALIZZAZIONE DATI ---
if 'staff' not in st.session_state:
    st.session_state.staff = pd.DataFrame([
        {"Nome": "MEROLLA MASSIMO", "Ruolo": "Coordinatore", "MSA1": True, "MSA2": True, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "BALDO GABRIELE", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "BROGGINI CHARLOTTE", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "CANCLINI FEDERICA", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "FRANZINI MARTINO", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "GHILOTTI PAOLO", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "PIETROGIOVANNA CHIARA", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "POLETTI RIZZI ALESSIA", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "RODIGARI GIULIA", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "SPINI NADIA", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "BARBARO GALANTINO SILVIA", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "CRUPI CARMEN", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "GAMBARRI CRISTINA", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "GERALI ALESSIA", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "INNOCENTI DANIELA", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "MIOTTI SOFIA", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "PANIZZA CATERINA", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "PESARO DAVIDE", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "SCARAMUZZI JACOPO", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0},
        {"Nome": "STEDILE PATRIZIA", "Ruolo": "Infermiere", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0}
    ])

# --- DASHBOARD ---
st.markdown('<div class="main-title">🏥 ShiftMaster PRO v3.0</div>', unsafe_allow_html=True)

tab_turni, tab_staff = st.tabs(["🗓️ GESTIONE TURNI E CALCOLO", "👥 ANAGRAFICA PERSONALE"])

with tab_staff:
    st.info("💡 Aggiungi qui i colleghi. Se il ruolo è 'Coordinatore', riceverà turni G (7.2h) in automatico.")
    st.session_state.staff = st.data_editor(st.session_state.staff, num_rows="dynamic", use_container_width=True)

with tab_turni:
    # Sidebar selectors spostati in colonna per pulizia
    c1, c2, c3 = st.columns([1, 1, 2])
    mese_sel = c1.selectbox("Mese", range(1, 13), index=datetime.now().month-1)
    anno_sel = c2.number_input("Anno", value=2026)
    
    num_gg = calendar.monthrange(anno_sel, mese_sel)[1]
    giorni = [f"{d}" for d in range(1, num_gg + 1)]
    nomi_staff = st.session_state.staff["Nome"].tolist()
    
    if 'griglia' not in st.session_state or st.session_state.get('last_m') != mese_sel:
        st.session_state.griglia = pd.DataFrame("", index=nomi_staff, columns=giorni)
        st.session_state.last_m = mese_sel
    
    st.session_state.griglia = st.session_state.griglia.reindex(nomi_staff).fillna("")

    # --- TASTO GENERA PREMIUM ---
    if st.button("✨ GENERA TURNI AUTOMATICI"):
        with st.spinner("Bilanciamento orario e sequenze in corso..."):
            # Reset dei turni generati precedentemente per evitare sovrapposizioni sporche
            for d_idx, d in enumerate(giorni):
                dt = date(anno_sel, mese_sel, int(d))
                festivi = get_festivi(anno_sel)
                is_festivo = dt.weekday() >= 5 or dt in festivi
                
                # Fabbisogno
                reqs = ["G12"]*3 + ["N12"]*3 + ["G12B"] + ["N12B"] + ["GTI", "GSL", "NTI", "NSL"]
                
                for turno in reqs:
                    # 1. Chi è il più scarico?
                    cur_h = {n: sum([ORE_TURNO for t in st.session_state.griglia.loc[n] if any(x in str(t) for x in ["12", "GT", "GS", "NT", "NS"])]) for n in nomi_staff}
                    sorted_names = sorted(cur_h.items(), key=lambda x: x[1])
                    
                    for nome, ore in sorted_names:
                        r = st.session_state.staff[st.session_state.staff["Nome"] == nome].iloc[0]
                        
                        # --- LOGICA COORDINATORE ---
                        if r["Ruolo"] == "Coordinatore":
                            if not is_festivo: st.session_state.griglia.at[nome, d] = "G"
                            continue # Non prende turni di PS
                        
                        # --- FILTRI IDONEITÀ ---
                        if st.session_state.griglia.at[nome, d] != "": continue
                        if "N" in turno and not r["Notti"]: continue
                        if any(x in turno for x in ["GT", "GS", "NT", "NS"]) and not r["MSA1"]: continue
                        
                        # Sequenza N -> SN -> R
                        if d_idx > 0:
                            ieri = giorni[d_idx-1]
                            if "N" in str(st.session_state.griglia.at[nome, ieri]): continue
                        
                        st.session_state.griglia.at[nome, d] = turno
                        if "N" in turno:
                            if d_idx+1 < num_gg: st.session_state.griglia.at[nome, giorni[d_idx+1]] = "SN"
                            if d_idx+2 < num_gg: st.session_state.griglia.at[nome, giorni[d_idx+2]] = "R"
                        break
        st.success("Tabellone generato con successo!")

    # GRIGLIA EDITABILE
    config_c = {d: st.column_config.SelectboxColumn(d, options=CODICI_TURNO, width="small") for d in giorni}
    grid_res = st.data_editor(st.session_state.griglia, column_config=config_c, use_container_width=True, height=600)
    st.session_state.griglia = grid_res

    # --- PANNELLO ANALISI ---
    st.divider()
    col_rep, col_sug = st.columns([3, 2])
    
    with col_rep:
        st.subheader("⚖️ Bilancio Ore Mensili")
        rep_data = []
        for _, inf in st.session_state.staff.iterrows():
            fatte = sum([ORE_TURNO for t in grid_res.loc[inf["Nome"]] if any(x in str(t) for x in ["12", "GT", "GS", "NT", "NS"])])
            fatte += sum([DEBITO_GG for t in grid_res.loc[inf["Nome"]] if t == "G"])
            fatte += sum([float(str(t).split(":")[1]) for t in grid_res.loc[inf["Nome"]] if "AO:" in str(t)])
            
            festivi = get_festivi(anno_sel)
            gg_l = len([d for d in range(1, num_gg+1) if date(anno_sel, mese_sel, d).weekday() < 5 and date(anno_sel, mese_sel, d) not in festivi])
            debito = (gg_l * DEBITO_GG) * (inf["PT"]/100) - inf["H104"]
            
            rep_data.append({"Infermiere": inf["Nome"], "Contratto": f"{inf['PT']}%", "Debito": round(debito, 1), "Fatte": round(fatte, 1), "Saldo": round(fatte-debito,
