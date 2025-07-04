import streamlit as st

def check_inclusion(patient, trial):
    age_condition = False
    for inc in trial['inclusion']:
        if "age" in inc:
            try:
                expression = inc.replace("age", str(patient['age']))
                age_condition |= eval(expression)
            except:
                pass
        elif inc in patient['conditions']:
            age_condition |= True
    return age_condition

def check_exclusion(patient, trial):
    return any(exc in patient['conditions'] for exc in trial['exclusion'])

def location_match(patient, trial):
    return patient['location'].lower() == trial['location'].lower()

def score_match(patient, trial):
    score = 0
    for inc in trial['inclusion']:
        if "age" in inc:
            try:
                if eval(inc.replace("age", str(patient['age']))):
                    score += 1
            except:
                pass
        elif inc in patient['conditions']:
            score += 1
    for exc in trial['exclusion']:
        if exc in patient['conditions']:
            score -= 1
    if location_match(patient, trial):
        score += 1
    return score

def match_trials(patient, trials):
    results = []
    for trial in trials:
        if check_inclusion(patient, trial) and not check_exclusion(patient, trial):
            score = score_match(patient, trial)
            results.append({
                "trial": trial["trial_name"],
                "score": score,
                "reason": f"Matched inclusion criteria and location with score {score}"
            })
    return sorted(results, key=lambda x: x['score'], reverse=True)

st.set_page_config(page_title="Clinical Trial Matcher", layout="centered")
st.title("Clinical Trial Patient Matching System")

default_trials = [
    {
        "trial_name": "Diabetes Drug Trial",
        "inclusion": ["age > 45", "diabetes"],
        "exclusion": ["heart disease"],
        "location": "Hyderabad"
    },
    {
        "trial_name": "Hypertension Study",
        "inclusion": ["age > 30", "hypertension"],
        "exclusion": ["kidney failure"],
        "location": "Bengaluru"
    },
    {
        "trial_name": "Wellness Trial",
        "inclusion": ["age > 20"],
        "exclusion": [],
        "location": "Hyderabad"
    }
]

with st.form("patient_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=120, value=40)
    location = st.text_input("Location")
    conditions_input = st.text_area("Medical Conditions (comma-separated)", value="diabetes")
    submitted = st.form_submit_button("Match Trials")

if submitted:
    conditions = [c.strip().lower() for c in conditions_input.split(",") if c.strip()]
    patient = {
        "name": name,
        "age": age,
        "location": location,
        "conditions": conditions
    }
    st.subheader(f"Matches for {patient['name']}")
    recommendations = match_trials(patient, default_trials)
    if recommendations:
        for r in recommendations:
            st.success(f"{r['trial']} — {r['reason']}")
    else:
        st.warning("No suitable trials found.")

