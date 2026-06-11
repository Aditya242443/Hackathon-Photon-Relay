# PhotonRelay

**Free Space Optical (FSO) Communication System**
Far Away Hackathon 2026 — Space & Aerospace

> PhotonRelay replaces radio frequency (RF) satellite links with near-infrared laser light — achieving **10–100× more bandwidth** at the same power level, with no spectrum licensing and inherent physical security from the laser's narrow beam width.

---

## The Problem

All satellites today communicate using RF or microwave transmission. Over long distances, this creates four hard limits:

| Limitation | Impact |
|---|---|
| Bandwidth ceiling | High-resolution data transfer takes hours |
| Inverse-square power loss | Signal degrades catastrophically with distance |
| Spectrum congestion | RF is crowded, regulated, and increasingly interfered with |
| No real-time recovery | At deep space distances, one-way light travel takes minutes — lost packets cannot be retransmitted in real time |

---

## The Solution

PhotonRelay encodes binary data as **near-infrared laser pulses** using On-Off Keying (OOK) modulation — a servo-motor flap in front of a 1550 nm laser diode acts as a physical optical shutter:

- Flap **open (90°)** → laser passes → bit `1`
- Flap **closed (0°)** → laser blocked → bit `0`

Data is structured using the **CCSDS Space Packet Protocol**, error-protected with **Reed-Solomon RS(255,223) FEC**, and carried across a three-node relay chain over two near-infrared wavelengths simultaneously.

---

## System Architecture

```
[GROUND STATION]  ──RF uplink──►  [LEO RELAY SATELLITE]  ──1550 nm OOK──►  [IPS]
                                         ▲                                     │
                                         └──────── 1550 nm return data ────────┘
```

| Node | Role |
|---|---|
| **Ground Station** | Sends and receives mission data via conventional RF — no optical hardware on the ground |
| **LEO Relay Satellite** | Engineering core — tracks the IPS in 3D space, receives the deep-space laser beam, and steers its own transmit laser to sub-microradian accuracy |
| **IPS (Inter Planetary Satellite)** | Sends and receives OOK laser data; acquires the LEO relay via star tracker → beacon lock → FSM closed-loop pointing |

---

## How It Works — Key Technical Pillars

### 1. OOK Modulation
Binary data drives a micro servo motor at a TCXO-clocked bit rate. The servo opens and closes a flap in front of the 1550 nm laser — converting every bit into a light pulse or silence. At the receiver, an InGaAs photodetector and transimpedance amplifier (TIA) reconstruct the original bit stream.

### 2. Wavelength Division Multiplexing (WDM)
Two signals travel simultaneously on the same optical path, separated by a dichroic beamsplitter at the receiver:

| Wavelength | Purpose | Modulation |
|---|---|---|
| **1064 nm** | Position beacon — wide beam, used for tracking and acquisition | Continuous wave |
| **1550 nm** | Data laser — narrow beam, high bandwidth | OOK via servo flap |

Tracking and data links are **physically independent** — losing the data link does not break the tracking lock.

### 3. Three-Stage Satellite Tracking (LEO)
The LEO relay must locate the IPS to sub-microradian precision. A cascade of three stages narrows the uncertainty from kilometres down to microradians:

| Stage | Method | Output |
|---|---|---|
| **Stage 1 — AoA** | Astrometric reduction maps the IPS beacon pixel position against a known star catalogue | Direction to **arcsecond** precision |
| **Stage 2 — TDOA** | 4 neighbouring LEO satellites timestamp the signal arrival; 3 hyperboloid intersections give a unique 3D point | **3D position** of the IPS |
| **Stage 3 — Orbital Determination** | Gauss/Laplace algorithm fits a Keplerian orbit to 3 time-stamped observations | **Future position** predicted — accounts for point-ahead angle |

### 4. Backtracking Deep Space Reception
When a laser arrives from deep space, the LEO relay intercepts it and measures its exact angle of arrival — then steers its own transmit laser back along that same direction:

| Stage | What Happens |
|---|---|
| **Footprint intercept** | Primary mirror (>200 mm aperture) collects photons from the beam footprint, which is hundreds of km wide at interplanetary distances |
| **Spectral filtering** | Fabry-Perot interferometer removes 99.99% of background light; passes only the 1550 nm signal |
| **ToF ranging** | TCXO timestamps the arrival of the CCSDS packet; distance = (arrival − emission time) × speed of light |
| **Spatial heterodyning** | Beam splitter + two InGaAs detectors measure wavefront phase difference → angle of arrival to **microradian** accuracy → feeds FSM pointing loop |

### 5. Beam Steering — Two Layers
- **Stewart Platform (6-DOF hexapod):** coarse pointing and vibration isolation — decouples the entire optical assembly from spacecraft micro-vibrations
- **Fast Steering Mirror (FSM) + Piezo Driver:** fine pointing in microseconds — driven by the Shack-Hartmann wavefront sensor and spatial heterodyne angle output

### 6. CCSDS Packet Framing
All data follows the CCSDS Space Packet Protocol:

| Field | Purpose |
|---|---|
| Sync marker (`0xFAF320`) | Marks every frame start — receiver re-synchronises even after mid-stream data loss |
| Primary header | Spacecraft ID, sequence count, TCXO timestamp, data length |
| RS payload (255 bytes) | 223 bytes of data + 32 RS redundancy bytes |
| CRC-16 | Frame integrity check before RS decoding |

### 7. Reed-Solomon FEC
RS(255,223) provides mathematically guaranteed error correction with **zero silent failure**:
- **223 bytes** data → encoded to **255-byte block** (32 redundancy bytes appended)
- Up to **16 corrupted or lost bytes per block** recovered perfectly
- If the limit is exceeded → error is **explicitly flagged**, never silently returning wrong data
- ~14% overhead — a fixed, small cost for deterministic recovery

> ML-based reconstruction was evaluated and dropped. ML has no guaranteed correction bound and can silently return wrong data. RS codes provide a hard mathematical limit with zero ambiguity.

### 8. IPS Pointing Sequence
The IPS uses a four-phase sequential acquisition — no TDOA or full backtracking stack needed, since it only tracks one known target:

**Star tracker** (absolute attitude) → **Gyro/IMU** (attitude propagation) → **1064 nm beacon lock** (CMOS array) → **FSM closed loop** (microsecond correction) → **Data TX/RX active**

---

## Simulation

The `/simulation` folder contains a Python OOK signal simulator that generates and visualises the modulation scheme.

**Output:** Three Matplotlib plots — clean OOK signal, noise-affected signal, decoded output.

```bash
pip install numpy matplotlib
python simulation/ook_signal.py
```

---

## Repository Structure

```
PhotonRelay/
├── simulation/
│   └── ook_signal.py             # OOK signal simulation and plots
├── hardware/
│   ├── leo_schematic.png         # LEO relay EasyEDA circuit schematic
│   ├── ips_schematic.png         # IPS EasyEDA circuit schematic
│   └── system_diagram.png        # Full system architecture diagram
├── docs/
│   ├── system_architecture.md    # Three-node architecture + full component lists
│   ├── communication_protocol.md # OOK, WDM, CCSDS framing, Reed-Solomon FEC
│   └── satellite_tracking.md     # 3-stage tracking, backtracking, IPS pointing
├── presentation/
│   └── PhotonRelay_Slides.pdf
└── README.md
```

---

## Documentation

| Doc | What it covers |
|---|---|
| [`docs/system_architecture.md`](docs/system_architecture.md) | Full system overview — three-node architecture, end-to-end data flow, and complete component lists for both LEO relay and IPS |
| [`docs/communication_protocol.md`](docs/communication_protocol.md) | Full protocol stack — OOK modulation, WDM dual-wavelength design, CCSDS packet framing, and Reed-Solomon FEC |
| [`docs/satellite_tracking.md`](docs/satellite_tracking.md) | All three tracking systems — 3-stage LEO tracking cascade, 4-stage backtracking reception, IPS simplified pointing, and full precision chain |

---

## Team

| Member | Role |
|---|---|
| Person 1 | Presentation & Visual Design |
| Person 2 | Hardware Design & Schematics |
| Person 3 | Docs, GitHub & Simulation |

---

*Far Away Hackathon 2026 — Space & Aerospace | Submission Deadline: 14 June 2026*
