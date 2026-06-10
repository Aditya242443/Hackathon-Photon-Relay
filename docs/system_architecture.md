# System Architecture — PhotonRelay

**PhotonRelay** is a Free Space Optical (FSO) communication system that replaces radio frequency (RF) satellite links with near-infrared laser light — delivering **10–100× more bandwidth** at the same power level, with no spectrum licensing required and inherent physical security from the laser's narrow beam width.

---

## Why Not RF?

| Limitation | Impact |
|---|---|
| Bandwidth ceiling | Hard throughput limit — high-resolution data transfer takes hours |
| Inverse-square power loss | Signal degrades catastrophically over long distances |
| Spectrum congestion | RF is crowded, regulated, and increasingly interfered with |
| No real-time recovery | At deep space distances, one-way light travel can take minutes — lost packets cannot be retransmitted in real time |

---

## Three-Node Architecture

### Ground Station
- Communicates with the LEO relay via conventional **RF uplink**
- Optical transmission through Earth's atmosphere is impractical (weather, turbulence)
- No optical hardware required on the ground

### LEO Relay Satellite *(engineering core)*
Carries three interconnected subsystems:

| Subsystem | Purpose |
|---|---|
| **Primary EOS** | Encodes data as OOK laser pulses; receives and decodes incoming pulses |
| **Satellite Tracking** | Locates the IPS in 3D space — AoA → TDOA → orbital prediction |
| **Backtracking** | Intercepts the incoming deep-space beam, filters noise, measures its arrival angle to microradian precision |

- All three subsystems share **one STM32/FPGA** and **one TCXO** — minimises satellite mass and power draw
- Beam steering: **6-DOF Stewart Platform** (coarse) + **Fast Steering Mirror** (sub-microradian fine control)

### Inter Planetary Satellite (IPS)
- Carries a simplified stack — no TDOA array or full backtracking system needed
- Only tracks one known target: the LEO relay's 1064 nm beacon
- Pointing sequence: **Star tracker → Gyro/IMU → Beacon lock → FSM closed loop**

---

## How Data Travels

**Ground → IPS (downlink):**
1. Ground sends data to LEO relay via RF uplink
2. STM32 structures data into CCSDS packets, applies RS(255,223) FEC
3. Bit stream drives servo flap at TCXO clock rate → 1550 nm laser modulated as OOK pulses
4. Hexapod (coarse) + FSM (fine) steer the beam to the IPS
5. IPS primary mirror collects photons → Fabry-Perot filters background noise
6. InGaAs detector + TIA reconstruct the bit stream → STM32 decodes

**IPS → Ground (uplink):** Same path in reverse — IPS transmits OOK on 1550 nm back to LEO relay, LEO relay forwards to ground via RF.

---

## Component List — LEO Relay Satellite

### Primary EOS

| Component | Spec | Function |
|---|---|---|
| NIR Laser Diode | 1550 nm, ~100 mW | Transmits OOK-modulated data pulses toward IPS |
| Servo Motor (LS / Flap) | Micro servo, 0–90° | Physical shutter — open = bit `1`, closed = bit `0` |
| Dichroic Beamsplitter | Reflects 1064 nm / transmits 1550 nm | Separates position beacon and data wavelengths at the receiver aperture |
| InGaAs Photodetector | 900–1700 nm sensitive | Converts incoming 1550 nm OOK pulses to electrical current |
| Transimpedance Amplifier (TIA) | Wideband | Converts photodetector current to a measurable voltage signal |

### Satellite Tracking

| Component | Spec | Function |
|---|---|---|
| CMOS Focal Plane Array | High-res imaging sensor | Captures 1064 nm beacon; feeds astrometric reduction on STM32 |
| 1064 nm Bandpass Filter | FWHM < 10 nm | Blocks all wavelengths except the 1064 nm beacon |
| RF Crosslink Receiver | UHF / S-band antenna | Receives TDOA timestamps from 4 neighbouring LEO satellites |
| FSM Piezo Driver IC | Sub-microradian range | Drives fast steering mirror for real-time fine pointing corrections |
| Shack-Hartmann WFS | Wavefront sensor | Measures wavefront distortions; feeds closed-loop FSM correction signals |
| 6-Point Stewart Platform | 6-DOF hexapod | Vibration isolation + coarse beam steering across several degrees |
| Hexapod Actuator Drivers | H-bridge / stepper drivers | Drives the 6 independently actuated legs of the Stewart platform |

### Backtracking

| Component | Spec | Function |
|---|---|---|
| Primary Mirror (telescope) | Aperture > 200 mm | Collects photons from the expanded deep-space laser footprint |
| Secondary Mirror / Collimator | Reflective collimator | Focuses collected light from the primary mirror into the optical path |
| Optical Baffle | Blackened tube structure | Blocks off-axis stray light — Sun, stars, Earth albedo reflections |
| Fabry-Perot Interferometer | 1550 nm | Removes 99.99% of background light; passes only the 1550 nm signal |
| 1550 nm Bandpass Filter | Secondary filter layer | Additional isolation directly in front of the InGaAs detector |
| InGaAs Detectors ×2 | 1550 nm sensitive | One for ToF ranging; two for wavefront phase measurement |
| Differential Phase Comparator | Analog/digital circuit | Calculates angle of arrival to **microradian** accuracy |

### Shared Across All Three Subsystems

| Component | Shared Between | Why Shared |
|---|---|---|
| STM32 / FPGA (STM32H7 or Xilinx Artix) | ALL | Runs all algorithms on one processor — saves mass and power |
| TCXO (0.1 ppm precision) | ALL | Single timing reference — prevents clock drift across TDOA, ToF, and CCSDS sync |
| FSM Piezo Driver IC | Tracking + Backtracking | Tracking steers the transmit beam; backtracking feeds angle corrections into the same FSM loop |
| Shack-Hartmann WFS | Tracking + Backtracking | Both subsystems use wavefront sensing to close the FSM correction loop |
| InGaAs Photodetector | EOS + Backtracking | EOS receives data signals; backtracking uses it for ToF detection and phase measurement |
| Dichroic Beamsplitter | EOS + Backtracking | EOS separates wavelengths on receive; backtracking uses it for spatial heterodyne detection |

---

## Component List — Inter Planetary Satellite (IPS)

| Component | Spec | Function |
|---|---|---|
| NIR Laser Diode | 1550 nm | Sends OOK-modulated data back to LEO relay |
| Servo Motor (LS / Flap) | Micro servo | OOK modulator for outgoing 1550 nm data laser |
| Dichroic Beamsplitter | Reflects 1064 / transmits 1550 nm | Separates incoming 1064 nm beacon from 1550 nm data signal |
| InGaAs Photodetector | 900–1700 nm | Receives incoming 1550 nm data from LEO relay |
| STM32 / FPGA | Shared | RS FEC decoding, CCSDS parsing, all pointing algorithms |
| TCXO | 0.1 ppm | Timing reference for synchronisation and servo timing |
| Star Tracker | Optical star catalogue | Coarse attitude knowledge by matching observed star field to catalogue |
| Gyroscope / IMU | High-precision MEMS | Propagates attitude knowledge between star tracker update cycles |
| CMOS Focal Array | 1064 nm sensitive | Locks onto 1064 nm position beacon transmitted by the LEO relay |
| 1064 nm Bandpass Filter | Isolates beacon | Passes only the 1064 nm beacon wavelength to the CMOS array |
| FSM Piezo Driver IC | Sub-microradian | Fine steering mirror for closed-loop beacon tracking |
