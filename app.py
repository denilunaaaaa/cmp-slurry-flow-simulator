import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="CMP Slurry Flow Simulator", layout="wide")

st.title("CMP Slurry Flow Simulator")
st.write(
    """
    This simulator visualizes a simplified lubrication-theory model for Chemical Mechanical Polishing (CMP).
    It shows how slurry viscosity, rotation speed, gap thickness, and pad tilt affect hydrodynamic pressure,
    shear stress, lift force, and material removal rate.
    """
)

tab1, tab2, tab3 = st.tabs(["Core Interactive", "Validation View", "Design Exploration"])

# -----------------------------
# Helper function
# -----------------------------
def compute_pressure(speed_rpm, viscosity, gap_um, tilt):
    N = 80
    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, y)

    # Convert inputs
    omega = speed_rpm * 2 * np.pi / 60  # rad/s
    R = 0.15  # wafer radius, m
    U = omega * R  # characteristic relative velocity

    h0 = gap_um * 1e-6  # m

    # Simplified tilted film thickness profile
    h = h0 * (1 + tilt * X)

    # Prevent division by zero / negative gaps
    h = np.maximum(h, 0.1e-6)

    # Simplified lubrication-inspired pressure model
    # Pressure increases with viscosity, velocity, and stronger gap gradients.
    pressure = viscosity * U * tilt / (h**2)

    # Normalize for visualization
    pressure = pressure - np.min(pressure)

    return X, Y, h, pressure, U


# -----------------------------
# TAB 1: Core Interactive
# -----------------------------
with tab1:
    st.header("Core Interactive Simulator")

    col1, col2 = st.columns([1, 2])

    with col1:
        speed = st.slider("Rotation speed (rpm)", 10, 300, 100)
        viscosity = st.slider("Slurry viscosity, μ (Pa·s)", 0.001, 0.100, 0.010, step=0.001)
        gap = st.slider("Average slurry gap, h (μm)", 1, 100, 20)
        tilt = st.slider("Pad tilt factor", 0.00, 0.50, 0.10, step=0.01)
        preston = st.slider("Preston coefficient, k", 0.1, 2.0, 1.0, step=0.1)

    X, Y, h, pressure, U = compute_pressure(speed, viscosity, gap, tilt)

    avg_pressure = np.mean(pressure)
    area = np.pi * (0.15**2)
    lift_force = avg_pressure * area
    avg_shear = viscosity * U / (gap * 1e-6)
    removal_rate = preston * avg_pressure * U

    with col2:
        fig, ax = plt.subplots()
        contour = ax.contourf(X, Y, pressure, levels=30)
        fig.colorbar(contour, ax=ax, label="Relative pressure")
        ax.set_title("Pressure Distribution in CMP Slurry Film")
        ax.set_xlabel("x position")
        ax.set_ylabel("y position")
        st.pyplot(fig)

    st.subheader("Calculated Outputs")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Average Pressure", f"{avg_pressure:.2e} Pa")
    c2.metric("Lift Force", f"{lift_force:.2e} N")
    c3.metric("Average Shear Stress", f"{avg_shear:.2e} Pa")
    c4.metric("Relative Removal Rate", f"{removal_rate:.2e}")

    st.write(
        """
        According to lubrication theory, pressure generation is strongly affected by film thickness,
        viscosity, and relative velocity. This simplified simulator captures those trends rather than
        attempting to reproduce a full industrial CMP model.
        """
    )


# -----------------------------
# TAB 2: Validation View
# -----------------------------
with tab2:
    st.header("Validation View")

    st.write(
        """
        This section checks whether the simulator follows expected lubrication-theory trends.
        The goal is not exact experimental validation, but confirmation that the model behaves physically.
        """
    )

    speeds = np.linspace(10, 300, 50)
    pressures_speed = []

    for s in speeds:
        _, _, _, p, _ = compute_pressure(s, 0.01, 20, 0.10)
        pressures_speed.append(np.mean(p))

    fig1, ax1 = plt.subplots()
    ax1.plot(speeds, pressures_speed)
    ax1.set_xlabel("Rotation speed (rpm)")
    ax1.set_ylabel("Average relative pressure")
    ax1.set_title("Validation 1: Pressure Increases with Rotation Speed")
    st.pyplot(fig1)

    viscosities = np.linspace(0.001, 0.1, 50)
    pressures_visc = []

    for mu in viscosities:
        _, _, _, p, _ = compute_pressure(100, mu, 20, 0.10)
        pressures_visc.append(np.mean(p))

    fig2, ax2 = plt.subplots()
    ax2.plot(viscosities, pressures_visc)
    ax2.set_xlabel("Viscosity (Pa·s)")
    ax2.set_ylabel("Average relative pressure")
    ax2.set_title("Validation 2: Pressure Increases with Slurry Viscosity")
    st.pyplot(fig2)

    tilts = np.linspace(0, 0.5, 50)
    pressures_tilt = []

    for t in tilts:
        _, _, _, p, _ = compute_pressure(100, 0.01, 20, t)
        pressures_tilt.append(np.mean(p))

    fig3, ax3 = plt.subplots()
    ax3.plot(tilts, pressures_tilt)
    ax3.set_xlabel("Pad tilt factor")
    ax3.set_ylabel("Average relative pressure")
    ax3.set_title("Validation 3: Zero Tilt Produces Minimal Pressure Generation")
    st.pyplot(fig3)


# -----------------------------
# TAB 3: Design Exploration
# -----------------------------
with tab3:
    st.header("Design Exploration Mode")

    st.write(
        """
        In this mode, the user can compare different polishing conditions.
        The goal is to identify parameter combinations that improve pressure generation
        while avoiding excessive shear stress.
        """
    )

    colA, colB = st.columns(2)

    with colA:
        st.subheader("Design A")
        speed_A = st.slider("Speed A (rpm)", 10, 300, 80)
        viscosity_A = st.slider("Viscosity A (Pa·s)", 0.001, 0.100, 0.010, step=0.001, key="muA")
        gap_A = st.slider("Gap A (μm)", 1, 100, 30)
        tilt_A = st.slider("Tilt A", 0.00, 0.50, 0.10, step=0.01, key="tiltA")

    with colB:
        st.subheader("Design B")
        speed_B = st.slider("Speed B (rpm)", 10, 300, 150)
        viscosity_B = st.slider("Viscosity B (Pa·s)", 0.001, 0.100, 0.020, step=0.001, key="muB")
        gap_B = st.slider("Gap B (μm)", 1, 100, 20)
        tilt_B = st.slider("Tilt B", 0.00, 0.50, 0.20, step=0.01, key="tiltB")

    _, _, _, pA, UA = compute_pressure(speed_A, viscosity_A, gap_A, tilt_A)
    _, _, _, pB, UB = compute_pressure(speed_B, viscosity_B, gap_B, tilt_B)

    avg_pA = np.mean(pA)
    avg_pB = np.mean(pB)

    shear_A = viscosity_A * UA / (gap_A * 1e-6)
    shear_B = viscosity_B * UB / (gap_B * 1e-6)

    labels = ["Average Pressure", "Average Shear Stress"]
    A_values = [avg_pA, shear_A]
    B_values = [avg_pB, shear_B]

    x = np.arange(len(labels))
    width = 0.35

    fig4, ax4 = plt.subplots()
    ax4.bar(x - width/2, A_values, width, label="Design A")
    ax4.bar(x + width/2, B_values, width, label="Design B")
    ax4.set_xticks(x)
    ax4.set_xticklabels(labels)
    ax4.set_title("Design Comparison")
    ax4.legend()
    st.pyplot(fig4)

    st.write(
        """
        A desirable CMP condition should generate enough hydrodynamic pressure for stable polishing,
        but not so much shear stress that it increases defect risk or non-uniformity.
        """
    )