import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
            return name
    return "Inconnu"

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

# Répartir les jours du cycle par phase
for i in range(cycle_length):
    phase = get_cycle_phase(i, cycle_length)
    if phase not in phase_days:
        phase_days[phase] = []
    phase_days[phase].append(i + 1)

# Calculer les moyennes de proportion par activité pour chaque phase
data = []
for phase, days in phase_days.items():
    profile = activity_profiles.get(phase, {})
    for activity, proportion in profile.items():
        data.append({
            "Phase": phase,
            "Activité": activity,
            "Proportion moyenne": proportion,
            "Jours": f"{min(days)}-{max(days)}"
        })

summary_df = pd.DataFrame(data)
df_pivot = summary_df.pivot_table(index=["Phase", "Jours"], columns="Activité", values="Proportion moyenne", fill_value=0)

# Ordre des phases chronologique
phase_order = ["Menstruation", "Folliculaire", "Ovulation", "Lutéale"]
df_pivot = df_pivot.reindex([(p, summary_df[summary_df["Phase"] == p]["Jours"].iloc[0]) for p in phase_order])

# --- Diagramme de synthèse par phase ---
st.subheader("📊 Activités recommandées regroupées par phase")
fig, ax = plt.subplots(figsize=(9, 6))
df_pivot.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
ax.set_ylabel("Proportion d'énergie/temps")
ax.set_xlabel("Phase du cycle (jours correspondants)")
ax.set_title("Répartition idéale des types d'activités par phase du cycle")
ax.set_xticklabels([f"{phase}\n({jours})" for phase, jours in df_pivot.index], rotation=0)
ax.legend(title="Type d'activité", bbox_to_anchor=(1.05, 1), loc='upper left')
st.pyplot(fig)

# --- Légende explicative ---
st.markdown("""
### 🧾 Légende des phases
- **🔴 Menstruation** *(Jours 1-5)* : période de repos, recentrage, ressourcement
- **🌱 Folliculaire** *(Jours 6-13)* : montée en énergie, exploration et créativité
- **💫 Ovulation** *(Jours 14-16)* : élan relationnel, communication et visibilité
- **🌙 Lutéale** *(Jours 17-fin)* : recentrage, tri, tâches concrètes et automatisées
""")

# --- Footer ---
st.markdown("""
---
💡 *Cet outil propose une base indicative pour mieux s'écouter et organiser ses priorités.*
""")
