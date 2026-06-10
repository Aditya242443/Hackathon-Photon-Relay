# Satellite Tracking — PhotonRelay

The primary engineering challenge of any space-based optical communication system is **Acquisition, Tracking, and Pointing (ATP)**. A laser beam is pencil-thin. At deep space distances, even a **1-microradian pointing error** causes the beam to miss its target entirely. GPS does not exist in deep space. The target moves at thousands of metres per second. Both satellites vibrate from reaction wheels, thrusters, and thermal expansion.

PhotonRelay solves this through three interconnected systems.

---

## Part 1 — Three-Stage LEO Tracking System

Each stage narrows the pointing uncertainty further — handing off to the next with progressively finer resolution.

```
kilometres of uncertainty
         ↓
    Stage 1: AoA      →  direction to arcsecond precision
         ↓
    Stage 2: TDOA     →  full 3D position in space
         ↓
    Stage 3: Orbital  →  exact future position predicted
         ↓
sub-arcsecond pointing prediction
```

---

### Stage 1 — Angle of Arrival (AoA) via Astrometric Reduction

**Problem it solves:** Initial directional fix on the IPS from its 1064 nm beacon, with no prior orbital knowledge.

- CMOS focal plane array (behind a **1064 nm bandpass filter**) captures the IPS beacon
- Astrometric reduction on the STM32 maps the beacon's pixel position against a **known star catalogue reference frame**
- Surrounding stars have precisely known angular positions — the beacon's position relative to them gives its angle
- Output: direction of the incoming light to **arcsecond precision**

> AoA gives a direction — not a distance. The IPS could be anywhere along that line of sight. Stage 2 resolves this.

---

### Stage 2 — TDOA Triangulation (4 Neighbouring LEO Satellites)

**Problem it solves:** Converts the directional fix from Stage 1 into a precise **3D position** of the IPS.

- 4 LEO satellites simultaneously receive the IPS signal
- Because they are at different positions, the signal arrives at each with a **minute time difference**
- Each timestamps arrival using its TCXO → sends to the tracking satellite via **RF crosslink**
- Each satellite pair produces a **3D hyperboloid surface** — all points where that time difference holds true
- **Intersection of 3 hyperboloids (from 4 satellites) = one unique point** — the IPS's 3D position

> Three hyperboloids intersect at exactly one point in 3D space. This is the geometric basis of the triangulation.

---

### Stage 3 — Orbital Determination (Gauss / Laplace Method)

**Problem it solves:** Predicts the **exact future position** of the IPS — not just where it is now, but where it will be when the light arrives.

- Three time-stamped IPS positions (from Stage 2, collected at different moments) are fed into the **Gauss or Laplace algorithm** on the STM32
- The algorithm fits a **Keplerian orbit** to the three observations
- Output: a complete orbital element set — the STM32 can predict IPS position at **any future moment**
- The transmit laser is pre-aimed at where the IPS **will be** when light arrives — not where it is now

> **Point-ahead example:** If the IPS is 10,000 km away, light takes ~33 ms to travel there. In that time, the IPS moves ~200 m. The laser must lead by 200 m. Stage 3 computes this exactly.

---

## Part 2 — Backtracking Deep Space Laser Reception

When a laser arrives from deep space, the LEO relay must intercept it, filter out the noise of space, measure the range, and determine the exact angle it arrived from — then use that angle to point its transmit laser back along the same path.

---

### Stage 1 — Intercepting the Footprint

**Problem it solves:** A laser beam expands as it travels. At interplanetary distances it spreads into a footprint **hundreds of km wide** — signal power per unit area is extremely low.

- **Large-aperture primary mirror** (>200 mm diameter) acts as a photon collector across a wide area
- **Secondary mirror + collimator** focus the collected light into the optical path
- **Optical baffle** (blackened tube structure) blocks stray off-axis light — Sun, nearby stars, Earth albedo

---

### Stage 2 — Narrowband Spectral Filtering

**Problem it solves:** Solar background contributes enormous photon counts across all wavelengths — the 1550 nm signal is buried in noise without filtering.

- **Fabry-Perot interferometer** (or atomic line filter): removes **99.99%** of all incoming light, passes only the 1550 nm signal wavelength
- **Secondary 1550 nm bandpass filter** directly in front of the InGaAs detector — additional isolation layer

After both stages: solar background is effectively eliminated; only 1550 nm signal photons reach the detector.

---

### Stage 3 — Time of Flight (ToF) Ranging

**Problem it solves:** Measures the precise **distance to the IPS** from the light travel time embedded in the CCSDS packet.

- Filtered beam hits the **InGaAs photodetector** → TIA converts to voltage → STM32 timestamps arrival to **nanosecond precision** using the TCXO
- The IPS encodes its exact transmission time in the **CCSDS primary header**

```
Distance = (Time of Arrival − Time of Emission) × Speed of Light
```

- Provides range to complement the angular fix from Stages 1–2 → **full 3D position from the received signal alone**

---

### Stage 4 — Spatial Heterodyning and Wavefront Angle Measurement

**Problem it solves:** Measures the **exact angle the beam arrived from**, to microradian precision — the most precise pointing reference in the system. This angle closes the FSM pointing loop.

- A **beam splitter** divides the filtered 1550 nm beam into two paths
- Two **InGaAs detectors** measure the phase of the wavefront at each path
- A beam arriving at a slight angle creates a measurable **phase difference** between the two detectors
- A **differential phase comparator** converts this phase difference into an angle-of-arrival vector to **microradian accuracy**
- This vector is fed directly into the **FSM piezo driver** — the transmit laser is steered to point back along the exact incoming direction
- The **Shack-Hartmann wavefront sensor** provides additional correction input to the same FSM loop

> This stage is the most direct pointing method in the system — it tells the FSM exactly where the IPS signal came from, without relying on any orbital model.

---

## Part 3 — IPS Simplified Pointing Sequence

The IPS only needs to track one known target — the LEO relay's 1064 nm beacon. No TDOA constellation or full backtracking stack is required. Pointing uses a four-phase sequential acquisition from power-on to live data link.

---

### Phase 1 — Coarse Attitude Acquisition (Star Tracker + Gyroscope)

- **Star tracker** matches the observed star field against the onboard catalogue → spacecraft attitude to **arcsecond precision**
- **Gyroscope/IMU** propagates this attitude at high frequency between the slower star tracker update cycles — prevents drift in the intervals
- Output: the IPS knows which direction it is pointing in absolute space

### Phase 2 — LEO Beacon Acquisition (CMOS Array + 1064 nm Filter)

- STM32 uses the star-tracker-derived attitude to point the CMOS focal array toward the **predicted LEO relay position**
- **1064 nm bandpass filter** isolates the beacon from all other incoming light
- Once beacon is detected on the array → system transitions from **search mode** to **lock mode**

### Phase 3 — FSM Closed-Loop Fine Tracking

- The **centroid position** of the 1064 nm beacon on the CMOS array is continuously computed → fed as an **error signal** into the FSM piezo driver
- FSM steers to keep the beacon centred — high-bandwidth closed loop, corrects in **microseconds**
- Locking the receive beacon **simultaneously aligns the transmit laser** — the FSM steers both in the same direction

### Phase 4 — Data Transmission and Reception

- **Servo flap** modulates the 1550 nm laser with CCSDS-framed, RS-encoded OOK data → transmitted to LEO relay
- **InGaAs photodetector** receives incoming 1550 nm signal from LEO relay
- **STM32** applies RS(255,223) decoding → CCSDS parsing → extracts original payload
- FSM loop runs **continuously throughout** — pointing maintained regardless of micro-vibrations

---

## Full Precision Chain — End to End

| Stage | System | Method | Precision Achieved |
|---|---|---|---|
| AoA measurement | LEO Tracking — Stage 1 | Astrometric reduction vs. star catalogue | Arcsecond |
| 3D position fix | LEO Tracking — Stage 2 | TDOA — 4 satellites, 3 hyperboloids | Metres–kilometres |
| Future position | LEO Tracking — Stage 3 | Gauss/Laplace Keplerian orbit fit | Sub-arcsecond |
| Range measurement | Backtracking — Stage 3 | ToF from CCSDS packet timestamp | Nanosecond |
| Beam angle | Backtracking — Stage 4 | Spatial heterodyne phase comparison | **Microradian** |
| Coarse steering | Stewart Platform (hexapod) | 6-DOF mechanical positioning + vibration isolation | Degrees → arcseconds |
| Fine steering | FSM + Piezo Driver | Closed-loop from WFS + wavefront AoA | **Sub-microradian** |
