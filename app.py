#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 29 07:44:24 2025

@author: hcp2
"""

#!/usr/bin/env python3
import math
import streamlit as st

# ---------- Core ASCVD risk function ----------

def ascvd_10y_risk_pce(age, sex, race, tc, hdl, sbp,
                       on_treatment, smoker, diabetes):
    """
    10-year ASCVD risk using ACC/AHA 2013 Pooled Cohort Equations (Goff et al.).

    Parameters
    ----------
    age : float
        Age in years (validated 40–79 in original model).
    sex : str
        'male' or 'female'.
    race : str
        'white', 'black', or 'other' (other -> uses white coefficients).
    tc : float
        Total cholesterol in mg/dL.
    hdl : float
        HDL cholesterol in mg/dL.
    sbp : float
        Systolic blood pressure in mmHg.
    on_treatment : bool
        True if on BP-lowering medication (treated SBP).
    smoker : bool
        True if current smoker.
    diabetes : bool
        True if has diabetes.

    Returns
    -------
    float
        10-year ASCVD risk in percent (0–100).
    """

    sex = sex.lower().strip()
    race = race.lower().strip()
    if race not in ("white", "black", "other"):
        raise ValueError("race must be 'white', 'black', or 'other'")
    if race == "other":
        race = "white"

    # Coefficient sets for the original 2013 Pooled Cohort Equations
    if sex == "female" and race == "white":
        c = dict(
            CAge=-29.799, CSqAge=4.884,
            CTotalChol=13.54, CAgeTotalChol=-3.114,
            CHDLChol=-13.578, CAgeHDLChol=3.149,
            COnHypertensionMeds=2.019, CAgeOnHypertensionMeds=0.0,
            COffHypertensionMeds=1.957, CAgeOffHypertensionMeds=0.0,
            CSmoker=7.574, CAgeSmoker=-1.665,
            CDiabetes=0.661,
            S10=0.9665, MeanTerms=-29.18,
        )
    elif sex == "female" and race == "black":
        c = dict(
            CAge=17.114, CSqAge=0.0,
            CTotalChol=0.94, CAgeTotalChol=0.0,
            CHDLChol=-18.92, CAgeHDLChol=4.475,
            COnHypertensionMeds=29.291, CAgeOnHypertensionMeds=-6.432,
            COffHypertensionMeds=27.82, CAgeOffHypertensionMeds=-6.087,
            CSmoker=0.691, CAgeSmoker=0.0,
            CDiabetes=0.874,
            S10=0.9533, MeanTerms=86.61,
        )
    elif sex == "male" and race == "white":
        c = dict(
            CAge=12.344, CSqAge=0.0,
            CTotalChol=11.853, CAgeTotalChol=-2.664,
            CHDLChol=-7.99, CAgeHDLChol=1.769,
            COnHypertensionMeds=1.797, CAgeOnHypertensionMeds=0.0,
            COffHypertensionMeds=1.764, CAgeOffHypertensionMeds=0.0,
            CSmoker=7.837, CAgeSmoker=-1.795,
            CDiabetes=0.658,
            S10=0.9144, MeanTerms=61.18,
        )
    elif sex == "male" and race == "black":
        c = dict(
            CAge=2.469, CSqAge=0.0,
            CTotalChol=0.302, CAgeTotalChol=0.0,
            CHDLChol=-0.307, CAgeHDLChol=0.0,
            COnHypertensionMeds=1.916, CAgeOnHypertensionMeds=0.0,
            COffHypertensionMeds=1.809, CAgeOffHypertensionMeds=0.0,
            CSmoker=0.549, CAgeSmoker=0.0,
            CDiabetes=0.645,
            S10=0.8954, MeanTerms=19.54,
        )
    else:
        raise ValueError("sex must be 'male' or 'female'")

    # Natural logs
    ln_age = math.log(age)
    ln_tc = math.log(tc)
    ln_hdl = math.log(hdl)
    ln_sbp = math.log(sbp)

    # Core terms
    terms = (
        c["CAge"] * ln_age +
        c["CSqAge"] * (ln_age ** 2) +
        c["CTotalChol"] * ln_tc +
        c["CAgeTotalChol"] * ln_age * ln_tc +
        c["CHDLChol"] * ln_hdl +
        c["CAgeHDLChol"] * ln_age * ln_hdl
    )

    # Treated vs untreated SBP
    if on_treatment:
        terms += (
            c["COnHypertensionMeds"] * ln_sbp +
            c["CAgeOnHypertensionMeds"] * ln_age * ln_sbp
        )
    else:
        terms += (
            c["COffHypertensionMeds"] * ln_sbp +
            c["CAgeOffHypertensionMeds"] * ln_age * ln_sbp
        )

    # Smoking
    if smoker:
        terms += c["CSmoker"] + c["CAgeSmoker"] * ln_age

    # Diabetes
    if diabetes:
        terms += c["CDiabetes"]

    # Final 10-year risk (fraction)
    risk_fraction = 1.0 - (c["S10"] ** math.exp(terms - c["MeanTerms"]))

    # Convert to percent
    return risk_fraction * 100.0


# ---------- Streamlit UI ----------

st.set_page_config(
    page_title="ASCVD 10-year Risk Estimator",
    page_icon="❤️",
    layout="centered"
)

st.title("ASCVD 10-year Risk Estimator")
st.caption("Based on ACC/AHA 2013 Pooled Cohort Equations (PCE)")

st.markdown(
    """
**Important:** This tool is for educational use only and does **not** replace clinical judgment,
local guidelines, or professional medical advice.
"""
)

with st.form("ascvd_form"):
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age (years)", min_value=20.0, max_value=90.0, value=55.0, step=1.0)
        sex = st.radio("Sex", options=["Male", "Female"], horizontal=True)
        race = st.selectbox(
            "Race",
            options=["White / Other", "Black"],
            index=0
        )

    with col2:
        tc = st.number_input(
            "Total cholesterol (mg/dL)",
            min_value=100.0,
            max_value=400.0,
            value=213.0,
            step=1.0
        )
        hdl = st.number_input(
            "HDL cholesterol (mg/dL)",
            min_value=10.0,
            max_value=150.0,
            value=50.0,
            step=1.0
        )
        sbp = st.number_input(
            "Systolic blood pressure (mmHg)",
            min_value=80.0,
            max_value=250.0,
            value=120.0,
            step=1.0
        )

    st.markdown("### Risk Factors")
    col3, col4, col5 = st.columns(3)
    with col3:
        on_treatment = st.checkbox("On BP-lowering medication", value=False)
    with col4:
        smoker = st.checkbox("Current smoker", value=False)
    with col5:
        diabetes = st.checkbox("Diabetes", value=False)

    submitted = st.form_submit_button("Calculate 10-year ASCVD Risk")

if submitted:
    # Map UI values to function arguments
    sex_arg = "male" if sex.lower().startswith("m") else "female"
    race_arg = "black" if race.lower().startswith("black") else "white"

    # Basic range check for original model validity
    if age < 40 or age > 79:
        st.warning("⚠️ The original PCE were developed for ages 40–79 years. Use results with caution.")

    try:
        risk = ascvd_10y_risk_pce(
            age=age,
            sex=sex_arg,
            race=race_arg,
            tc=tc,
            hdl=hdl,
            sbp=sbp,
            on_treatment=on_treatment,
            smoker=smoker,
            diabetes=diabetes,
        )

        # Clip to sensible range
        risk = max(0.0, min(risk, 100.0))

        # Determine category
        if risk < 5:
            category = "Low risk (<5%)"
            color = "green"
        elif risk < 7.5:
            category = "Borderline risk (5–7.4%)"
            color = "orange"
        elif risk < 20:
            category = "Intermediate risk (7.5–19.9%)"
            color = "orange"
        else:
            category = "High risk (≥20%)"
            color = "red"

        st.markdown("---")
        st.subheader("Result")

        st.metric(
            label="Estimated 10-year ASCVD Risk",
            value=f"{risk:.1f} %"
        )

        st.markdown(f"**Risk category:** <span style='color:{color}; font-weight:bold'>{category}</span>",
                    unsafe_allow_html=True)

        with st.expander("Details / Notes"):
            st.markdown(
                """
- Population: adults without existing ASCVD, typically age 40–79 years  
- Outcomes: first **hard ASCVD event** (nonfatal MI, CHD death, or stroke)  
- These equations were derived mainly from US cohorts and may **over- or underestimate**
  risk in other populations or in individuals with characteristics far from the cohorts used.
                """
            )

    except Exception as e:
        st.error(f"Error computing risk: {e}")
