"""PumpCalc: centrifugal pump total-head and motor-sizing Streamlit app."""

from __future__ import annotations

from html import escape
from io import StringIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from pump_calculations import PumpInputs, calculate_pump, system_curve, validate_inputs


# Edit these values before the final college submission.
DEFAULT_STUDENT_NAME = "Jenil Rathod"
DEFAULT_ENROLLMENT_NUMBER = "Enter enrollment number"
DEFAULT_GROUP_NUMBER = "Individual"
DEFAULT_COLLEGE_NAME = "LJ Polytechnic, Ahmedabad"
DEFAULT_COURSE_NAME = "Diploma in Mechanical Engineering — Semester 3"


st.set_page_config(
    page_title="PumpCalc | Pump Sizing Tool",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
        :root {
            --navy: #102a43;
            --blue: #1f5d84;
            --orange: #e47724;
            --paper: #ffffff;
            --mist: #f3f6f8;
            --line: #dbe4ea;
            --ink: #172b3a;
            --muted: #607486;
        }

        .stApp { background: var(--mist); color: var(--ink); }
        [data-testid="stSidebar"] { background: #eaf0f4; border-right: 1px solid var(--line); }
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--navy); }
        .block-container { padding-top: 2rem; padding-bottom: 2.5rem; max-width: 1240px; }

        .project-hero {
            background: var(--paper);
            border: 1px solid var(--line);
            border-left: 6px solid var(--orange);
            border-radius: 8px;
            padding: 1.35rem 1.5rem 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 3px 14px rgba(16, 42, 67, 0.06);
        }
        .project-kicker {
            color: var(--orange);
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            margin-bottom: 0.35rem;
        }
        .project-hero h1 { color: var(--navy); font-size: 2rem; margin: 0; line-height: 1.2; }
        .project-hero p { color: var(--muted); margin: 0.6rem 0 0; max-width: 850px; }

        div[data-testid="stMetric"] {
            background: var(--paper);
            border: 1px solid var(--line);
            border-radius: 7px;
            padding: 0.8rem 1rem;
            min-height: 112px;
            box-shadow: 0 2px 9px rgba(16, 42, 67, 0.04);
        }
        div[data-testid="stMetric"] label { color: var(--muted); }
        div[data-testid="stMetricValue"] { color: var(--navy); }

        .section-note {
            background: #eef5f8;
            border: 1px solid #ccdae3;
            border-radius: 6px;
            padding: 0.85rem 1rem;
            color: #344f60;
            margin: 0.4rem 0 1rem;
        }
        .formula-card {
            background: var(--paper);
            border: 1px solid var(--line);
            border-radius: 7px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.7rem;
        }
        .formula-card strong { color: var(--navy); }
        .status-ok {
            background: #edf7f1;
            border: 1px solid #b9d9c4;
            border-left: 5px solid #2f855a;
            border-radius: 6px;
            padding: 0.8rem 1rem;
            margin: 0.8rem 0;
            color: #22543d;
        }
        .footer-card {
            background: var(--navy);
            color: #eaf2f7;
            border-radius: 7px;
            padding: 1rem 1.2rem;
            margin-top: 1.6rem;
            font-size: 0.88rem;
        }
        .footer-card b { color: #ffffff; }
        .small-muted { color: var(--muted); font-size: 0.84rem; }
        .stTabs [data-baseweb="tab-list"] { gap: 0.25rem; }
        .stTabs [data-baseweb="tab"] { background: #e7edf1; border-radius: 6px 6px 0 0; }
        .stTabs [aria-selected="true"] { color: var(--navy); font-weight: 700; }

        @media (max-width: 700px) {
            .block-container { padding-top: 1rem; }
            .project-hero h1 { font-size: 1.55rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown("## Input panel")
    st.caption("Enter the pump-system data using the units shown.")

    st.markdown("### Operating data")
    flow_lps = st.number_input(
        "Flow rate (L/s)", min_value=0.0, value=10.0, step=0.5, format="%.2f"
    )
    suction_head_m = st.number_input(
        "Static suction lift (m)", min_value=0.0, value=3.0, step=0.5, format="%.2f"
    )
    delivery_head_m = st.number_input(
        "Static delivery head (m)", min_value=0.0, value=17.0, step=0.5, format="%.2f"
    )

    st.markdown("### Suction pipe")
    suction_length_m = st.number_input(
        "Suction-pipe length (m)", min_value=0.0, value=6.0, step=0.5, format="%.2f"
    )
    suction_diameter_mm = st.number_input(
        "Suction-pipe diameter (mm)", min_value=0.0, value=100.0, step=5.0, format="%.1f"
    )

    st.markdown("### Delivery pipe")
    delivery_length_m = st.number_input(
        "Delivery-pipe length (m)", min_value=0.0, value=30.0, step=1.0, format="%.2f"
    )
    delivery_diameter_mm = st.number_input(
        "Delivery-pipe diameter (mm)", min_value=0.0, value=80.0, step=5.0, format="%.1f"
    )

    st.markdown("### Pump and motor")
    friction_factor = st.number_input(
        "Darcy friction factor, f",
        min_value=0.0,
        value=0.020,
        step=0.001,
        format="%.3f",
        help="Use the Darcy friction factor, not the Fanning friction factor.",
    )
    efficiency_percent = st.number_input(
        "Pump efficiency (%)", min_value=0.0, max_value=100.0, value=70.0, step=1.0
    )
    service_factor = st.slider(
        "Motor service factor", min_value=1.00, max_value=1.50, value=1.15, step=0.05
    )

    with st.expander("Project identity", expanded=False):
        student_name = st.text_input("Student name", value=DEFAULT_STUDENT_NAME)
        enrollment_number = st.text_input(
            "Enrollment number", value=DEFAULT_ENROLLMENT_NUMBER
        )
        group_number = st.text_input("Group number", value=DEFAULT_GROUP_NUMBER)

    with st.expander("Model assumptions", expanded=False):
        st.write("Fluid: water")
        st.write("Density: 1000 kg/m³")
        st.write("Gravity: 9.81 m/s²")
        st.write("Both reservoirs are open to atmosphere")
        st.write("Minor losses are not included")


inputs = PumpInputs(
    flow_lps=flow_lps,
    suction_head_m=suction_head_m,
    delivery_head_m=delivery_head_m,
    suction_length_m=suction_length_m,
    suction_diameter_mm=suction_diameter_mm,
    delivery_length_m=delivery_length_m,
    delivery_diameter_mm=delivery_diameter_mm,
    darcy_friction_factor=friction_factor,
    efficiency_percent=efficiency_percent,
    service_factor=service_factor,
)


st.markdown(
    """
    <div class="project-hero">
        <div class="project-kicker">MECHANICAL ENGINEERING MINI PROJECT · PROBLEM 16</div>
        <h1>PumpCalc</h1>
        <p>Centrifugal pump total-head and motor-sizing tool for an open-reservoir water-transfer system.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


input_errors = validate_inputs(inputs)
if input_errors:
    st.error("Please correct the input data before calculating:")
    for message in input_errors:
        st.write(f"• {message}")
    st.stop()


results = calculate_pump(inputs)
motor_text = (
    f"{results.recommended_motor_kw:.2f} kW"
    if results.recommended_motor_kw is not None
    else "> 90 kW"
)


metric_columns = st.columns(5)
metric_columns[0].metric("Total head", f"{results.total_manometric_head_m:.2f} m")
metric_columns[1].metric("Water power", f"{results.water_power_kw:.2f} kW")
metric_columns[2].metric("Shaft power", f"{results.shaft_power_kw:.2f} kW")
metric_columns[3].metric("Shaft power", f"{results.shaft_power_hp:.2f} HP")
metric_columns[4].metric("Recommended motor", motor_text)


if results.recommended_motor_kw is not None:
    st.markdown(
        f"""
        <div class="status-ok">
            <b>Motor selection:</b> Required design power is
            {results.design_motor_power_kw:.2f} kW after applying a
            {inputs.service_factor:.2f} service factor. Select the next common
            rating: <b>{results.recommended_motor_kw:.2f} kW</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.warning(
        "The design power is above the app's 90 kW rating list. Consult a motor "
        "manufacturer or supplier for the next suitable standard rating."
    )


design_warnings: list[str] = []
if inputs.suction_head_m > 7.0:
    design_warnings.append(
        "Static suction lift is above 7 m. Review atmospheric-pressure and cavitation limits."
    )
if results.suction_velocity_m_s > 1.5:
    design_warnings.append(
        "Suction velocity is above 1.5 m/s. Consider a larger suction pipe."
    )
if results.delivery_velocity_m_s > 3.0:
    design_warnings.append(
        "Delivery velocity is above 3.0 m/s. Consider a larger delivery pipe."
    )
if inputs.efficiency_percent < 50 or inputs.efficiency_percent > 90:
    design_warnings.append(
        "The entered efficiency is outside the usual educational design range of 50–90%."
    )
if (
    results.total_manometric_head_m > 0
    and results.total_friction_head_m / results.total_manometric_head_m > 0.25
):
    design_warnings.append(
        "Pipe-friction loss exceeds 25% of total head. Check the pipe diameters and lengths."
    )

for warning in design_warnings:
    st.warning(warning)


overview_tab, graph_tab, calculation_tab, viva_tab = st.tabs(
    ["Results", "Graphs", "Calculation steps", "Theory & viva"]
)


with overview_tab:
    st.subheader("Detailed engineering results")
    left_column, right_column = st.columns([1.12, 0.88], gap="large")

    with left_column:
        result_rows = [
            ("Flow rate", f"{results.flow_m3_s:.5f} m³/s"),
            ("Flow rate", f"{results.flow_m3_h:.2f} m³/h"),
            ("Suction-pipe area", f"{results.suction_area_m2:.6f} m²"),
            ("Suction velocity", f"{results.suction_velocity_m_s:.3f} m/s"),
            ("Delivery-pipe area", f"{results.delivery_area_m2:.6f} m²"),
            ("Delivery velocity", f"{results.delivery_velocity_m_s:.3f} m/s"),
            ("Suction friction loss", f"{results.suction_friction_head_m:.3f} m"),
            ("Delivery friction loss", f"{results.delivery_friction_head_m:.3f} m"),
            ("Total friction loss", f"{results.total_friction_head_m:.3f} m"),
            ("Static head", f"{results.static_head_m:.3f} m"),
            ("Total manometric head", f"{results.total_manometric_head_m:.3f} m"),
            ("Water power", f"{results.water_power_kw:.3f} kW"),
            ("Pump shaft power", f"{results.shaft_power_kw:.3f} kW"),
            ("Design motor power", f"{results.design_motor_power_kw:.3f} kW"),
            ("Recommended motor", motor_text),
        ]
        result_table = pd.DataFrame(result_rows, columns=["Quantity", "Calculated value"])
        st.dataframe(result_table, hide_index=True, width="stretch")

    with right_column:
        st.markdown("#### Head contribution")
        labels = ["Suction lift", "Delivery head", "Suction friction", "Delivery friction"]
        values = [
            inputs.suction_head_m,
            inputs.delivery_head_m,
            results.suction_friction_head_m,
            results.delivery_friction_head_m,
        ]
        colors = ["#1f5d84", "#4d7f9e", "#e47724", "#f2a65a"]
        figure, axis = plt.subplots(figsize=(6.3, 4.1))
        bars = axis.barh(labels, values, color=colors, height=0.62)
        axis.set_xlabel("Head (m)")
        axis.set_title("Components of total manometric head", loc="left", weight="bold")
        axis.grid(axis="x", alpha=0.25, linestyle="--")
        axis.set_axisbelow(True)
        axis.spines[["top", "right"]].set_visible(False)
        maximum_bar = max(values) if max(values) > 0 else 1
        axis.set_xlim(0, maximum_bar * 1.2)
        for bar, value in zip(bars, values):
            axis.text(
                value + maximum_bar * 0.015,
                bar.get_y() + bar.get_height() / 2,
                f"{value:.2f}",
                va="center",
                fontsize=9,
            )
        figure.tight_layout()
        st.pyplot(figure, width="stretch")
        plt.close(figure)

    csv_buffer = StringIO()
    result_table.to_csv(csv_buffer, index=False)
    st.download_button(
        "Download result table (CSV)",
        data=csv_buffer.getvalue(),
        file_name="pumpcalc_results.csv",
        mime="text/csv",
    )


with graph_tab:
    st.subheader("System-head curve")
    st.markdown(
        """
        <div class="section-note">
            Static head remains constant, while Darcy friction loss rises approximately
            with the square of flow rate. The orange point is the selected design condition.
        </div>
        """,
        unsafe_allow_html=True,
    )
    curve_flow, curve_head = system_curve(results)
    figure, axis = plt.subplots(figsize=(9.5, 5.2))
    axis.plot(curve_flow, curve_head, color="#1f5d84", linewidth=2.5, label="System head")
    axis.axhline(
        results.static_head_m,
        color="#7f8c96",
        linestyle="--",
        linewidth=1.3,
        label="Static head",
    )
    axis.scatter(
        [results.flow_m3_h],
        [results.total_manometric_head_m],
        color="#e47724",
        edgecolor="white",
        linewidth=1.5,
        s=95,
        zorder=5,
        label="Design point",
    )
    axis.annotate(
        f"  {results.flow_m3_h:.1f} m³/h, {results.total_manometric_head_m:.2f} m",
        (results.flow_m3_h, results.total_manometric_head_m),
        xytext=(8, 12),
        textcoords="offset points",
        fontsize=9,
        color="#172b3a",
    )
    axis.set_xlabel("Flow rate (m³/h)")
    axis.set_ylabel("System head (m)")
    axis.set_title("System head versus flow rate", loc="left", weight="bold")
    axis.grid(True, alpha=0.28, linestyle="--")
    axis.legend(frameon=False)
    axis.spines[["top", "right"]].set_visible(False)
    figure.tight_layout()
    st.pyplot(figure, width="stretch")
    plt.close(figure)

    st.latex(r"H_{system}(Q)=H_{static}+KQ^2")
    st.caption(
        "The curve represents the pipe system, not a manufacturer's pump performance curve."
    )


with calculation_tab:
    st.subheader("Formula-by-formula calculation")

    st.markdown('<div class="formula-card"><strong>1. Convert the flow rate</strong></div>', unsafe_allow_html=True)
    st.latex(
        rf"Q=\frac{{{inputs.flow_lps:.2f}}}{{1000}}={results.flow_m3_s:.5f}\;m^3/s"
    )

    st.markdown('<div class="formula-card"><strong>2. Pipe areas and velocities</strong></div>', unsafe_allow_html=True)
    st.latex(r"A=\frac{\pi D^2}{4},\qquad V=\frac{Q}{A}")
    st.write(
        f"Suction: A = {results.suction_area_m2:.6f} m², "
        f"V = {results.suction_velocity_m_s:.3f} m/s"
    )
    st.write(
        f"Delivery: A = {results.delivery_area_m2:.6f} m², "
        f"V = {results.delivery_velocity_m_s:.3f} m/s"
    )

    st.markdown('<div class="formula-card"><strong>3. Darcy–Weisbach friction losses</strong></div>', unsafe_allow_html=True)
    st.latex(r"h_f=f\frac{L}{D}\frac{V^2}{2g}")
    st.write(f"Suction friction loss = {results.suction_friction_head_m:.3f} m")
    st.write(f"Delivery friction loss = {results.delivery_friction_head_m:.3f} m")

    st.markdown('<div class="formula-card"><strong>4. Total manometric head</strong></div>', unsafe_allow_html=True)
    st.latex(r"H_m=H_s+H_d+h_{fs}+h_{fd}")
    st.latex(
        rf"H_m={inputs.suction_head_m:.2f}+{inputs.delivery_head_m:.2f}+"
        rf"{results.suction_friction_head_m:.3f}+{results.delivery_friction_head_m:.3f}"
        rf"={results.total_manometric_head_m:.3f}\;m"
    )

    st.markdown('<div class="formula-card"><strong>5. Water and shaft power</strong></div>', unsafe_allow_html=True)
    st.latex(r"P_w=\rho gQH_m")
    st.latex(r"P_{shaft}=\frac{P_w}{\eta_p}")
    st.write(
        f"Water power = {results.water_power_kw:.3f} kW; "
        f"shaft power = {results.shaft_power_kw:.3f} kW "
        f"({results.shaft_power_hp:.3f} HP)."
    )

    st.markdown('<div class="formula-card"><strong>6. Motor selection</strong></div>', unsafe_allow_html=True)
    st.latex(r"P_{design}=P_{shaft}\times SF")
    st.write(
        f"Design power = {results.shaft_power_kw:.3f} × {inputs.service_factor:.2f} "
        f"= {results.design_motor_power_kw:.3f} kW."
    )
    st.write(f"Recommended next common rating: **{motor_text}**")


with viva_tab:
    st.subheader("Theory and viva preparation")
    st.markdown("#### Model assumptions")
    st.markdown(
        """
        - Water density is taken as 1000 kg/m³ and gravitational acceleration as 9.81 m/s².
        - The suction and delivery reservoirs are open to atmosphere.
        - Velocity at each reservoir free surface is treated as negligible.
        - Pipe losses are calculated with the Darcy friction factor entered by the user.
        - Minor losses from valves, bends, strainers and fittings are not included.
        - The motor suggestion is an educational preliminary selection, not a purchase specification.
        """
    )

    st.markdown("#### Quick viva questions")
    with st.expander("What is total manometric head?"):
        st.write(
            "It is the total head that the pump must supply. In this model it equals "
            "static suction lift, static delivery head and the friction losses in both pipes."
        )
    with st.expander("Why does friction loss increase rapidly with flow?"):
        st.write(
            "For fixed pipe dimensions and friction factor, velocity is proportional to flow. "
            "Darcy loss contains V², so the loss is approximately proportional to Q²."
        )
    with st.expander("Why is shaft power greater than water power?"):
        st.write(
            "A real pump is not 100% efficient. Some input energy is lost through hydraulic, "
            "mechanical and volumetric losses. Therefore shaft power equals water power divided by efficiency."
        )
    with st.expander("Why is a service factor used?"):
        st.write(
            "It provides margin for operating variations and avoids selecting a motor whose rating "
            "is exactly equal to the calculated requirement."
        )
    with st.expander("What is the difference between a system curve and a pump curve?"):
        st.write(
            "The system curve shows the head required by the piping system at different flows. "
            "The pump curve is supplied by the manufacturer and shows the head produced by a particular pump."
        )


safe_student = escape(student_name.strip() or "Not entered")
safe_enrollment = escape(enrollment_number.strip() or "Not entered")
safe_group = escape(group_number.strip() or "Not entered")
st.markdown(
    f"""
    <div class="footer-card">
        <b>{escape(DEFAULT_COLLEGE_NAME)}</b><br>
        {escape(DEFAULT_COURSE_NAME)}<br><br>
        Student: <b>{safe_student}</b> &nbsp;·&nbsp;
        Enrollment: <b>{safe_enrollment}</b> &nbsp;·&nbsp;
        Group: <b>{safe_group}</b>
    </div>
    """,
    unsafe_allow_html=True,
)
