import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import locale

# Forcer la locale française (adaptation selon OS)
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # Linux/macOS
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'French_France.1252')  # Windows
    except locale.Error:
        st.warning("Locale française non disponible sur ce système. Dates en anglais.")

st.set_page_config(page_title="Rythmes du Cycle - Vue Synthétique", layout="centered")

# --- UTILS ---
def get_cycle_phase(day, cycle_length=28):
    phases = [
        ("Menstruation", 0, 4, "🔴"),
        ("Folliculaire", 5, 13, "🌱"),
        ("Ovulation", 14, 16, "💫"),
        ("Lutéale", 17, cycle_length-1, "🌙")
    ]
    for name, start, end, emoji in phases:
        if start <= day % cycle_length <= end:
            return name, start, end
    return "Inconnu", None, None

def phase_activity_profile():
    return {
        "Menstruation": {
            "Réparatrice": 0.6,
            "Créative douce": 0.3,
            "Logistique": 0.1
        },
        "Folliculaire": {
            "Créative": 0.4,
            "Exploration": 0.3,
            "Apprentissage": 0.3
        },
        "Ovulation": {
            "Communicationnelle": 0.4,
            "Relationnelle": 0.3,
            "Leadership": 0.3
        },
        "Lutéale": {
            "Exécutive": 0.4,
            "Analytique": 0.3,
            "Automatisme": 0.3
        }
    }

# --- UI ---
st.title("🌸 Rythmes du Cycle - Vue Synthétique")
st.markdown("""
Indiquez votre cycle, et visualisez les moments les plus propices pour chaque type d'activité selon les phases naturelles.
""")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Date du premier jour des dernières règles", datetime.date.today())
with col2:
    cycle_length = st.slider("Durée moyenne de votre cycle (jours)", 21, 35, 28)

# --- Data regroupée par phase ---
activity_profiles = phase_activity_profile()
phase_days = {}

# Répartir les jours du cycle par phase et mémoriser les dates
for i in range(cycle_length):
    phase, start_idx, end_idx = get_cycle_phase(i, cycle_length)
    if phase not in phase_days:
        phase_days[phase] = {"days": [], "start_idx": start_idx, "end_idx": end_idx}
    phase_days[phase]["days"].append(start_date + datetime.timedelta(days=i))

# Calculer les moyennes de proportion par activité pour chaque phase
data = []
for phase, info in phase_days.items():
    profile = activity_profiles.get(phase, {})
    for activity, proportion in profile.items():
        data.append({
            "Phase": phase,
            "Activité": activity,
            "Proportion moyenne": proportion
        })

df = pd.DataFrame(data)
df_pivot = df.pivot_table(index="Phase", columns="Activité", values="Proportion moyenne", fill_value=0)

# Ordre des phases chronologique
phase_order = ["Menstruation", "Folliculaire", "Ovulation", "Lutéale"]
df_pivot = df_pivot.loc[phase_order]

# Préparer les labels avec nom phase + plage de dates en français
x_labels = []
for phase in phase_order:
    info = phase_days.get(phase)
    if info:
        start_date_phase = info["days"][0].strftime("%d %b")
        end_date_phase = info["days"][-1].strftime("%d %b")
        label = f"{phase}\n{start_date_phase} - {end_date_phase}"
    else:
        label = phase
    x_labels.append(label)

# --- Diagramme de synthèse par phase ---
st.subheader("📊 Activités recommandées regroupées par phase")

fig, ax = plt.subplots(figsize=(9, 6))
df_pivot.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")

ax.set_ylabel("Proportion d'énergie/temps")
ax.set_xlabel("Phase du cycle")
ax.set_title("Répartition idéale des types d'activités par phase du cycle")
ax.legend(title="Type d'activité", bbox_to_anchor=(1.05, 1), loc='upper left')
ax.set_xticklabels(x_labels, rotation=0)

st.pyplot(fig)

# --- Légende explicative ---
st.markdown("---")
st.markdown("### Légende des phases et recommandations")
st.markdown("""
- **Menstruation** : Priorisez les activités réparatrices, créatives douces, et un peu de logistique.  
- **Folliculaire** : Favorisez la créativité, l'exploration et l'apprentissage.  
- **Ovulation** : Mettez l'accent sur la communication, les relations, et le leadership.  
- **Lutéale** : Concentrez-vous sur les tâches exécutives, l'analyse et les routines automatisées.
""")

# --- Footer ---
st.markdown("""
---
💡 *Cet outil propose une base indicative pour mieux s'écouter et organiser ses priorités.*
""")
