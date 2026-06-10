# 🚀 PhotonRelay: Free Space Optical Communication System

An advanced, near-infrared laser-based communication system designed for deep-space and satellite-to-satellite networks, replacing traditional radio frequency (RF) limitations with sub-microradian optical precision.

---

## 📌 Table of Contents
* [About the Project](#-about-the-project)
* [The Problem with RF & The Solution](#-the-problem-with-rf--the-solution)
* [Core Subsystems & System Architecture](#-core-subsystems--system-architecture)
* [Repository Structure](#-repository-structure)
* [Tech Stack & Tools](#%EF%B8%8F-tech-stack--tools)
* [Getting Started & Simulation Setup](#-getting-started--simulation-setup)
* [Hackathon Timeline & Team Roles](#-hackathon-timeline--team-roles)
* [Scientific Precedent](#-scientific-precedent)

---

## 💡 About the Project
**PhotonRelay** is an interplanetary communication concept developed for the **Far Away Hackathon 2026** (Space & Aerospace Theme). It replaces standard radio wave transmissions with near-infrared ($1550\text{ nm}$) laser light for satellite-to-satellite and Low Earth Orbit (LEO) relay communication. By using optical frequencies, PhotonRelay eliminates spectrum congestion and handles massive throughput increases, achieving bandwidth capabilities 10x to 100x faster than comparable RF systems.

---

## ⚡ The Problem with RF & The Solution

### The RF Bottleneck
* **Bandwidth Ceiling:** RF has a hard throughput limit; transferring high-resolution data over deep space takes hours.
* **Signal Degradation:** The inverse-square law causes radio signal power to drop catastrophically over millions of kilometers.
* **Spectrum Congestion:** RF bands are crowded and heavily regulated; deploying more satellites creates severe interference.
* **Real-Time Recovery Failure:** With one-way light travel times to Mars taking up to 24 minutes, real-time packet retransmission is impossible.

### The PhotonRelay Breakthrough
* **High Bandwidth:** Uses short wavelength lasers to pack orders of magnitude more data per unit time.
* **Inherent Security:** A narrow, pencil-thin beam width makes interception virtually impossible.
* **Unregulated Spectrum:** Optical frequencies in deep space require no spectrum licensing.
* **Optimized Payload:** Drastically lower mass and power consumption compared to bulky RF dishes.

---

## ⚙️ Core Subsystems & System Architecture

The system resolves the complex **Acquisition, Tracking, and Pointing (ATP)** challenges using three integrated innovations:

1. **Three-Stage Satellite Tracking:**
   * *Stage 1 (Astrometric Reduction):* CMOS focal arrays map incoming light onto star catalogs to extract the precise Angle of Arrival (AoA).
   * *Stage 2 (Multi-Satellite TDOA):* Four neighboring LEO satellites use Time Difference of Arrival to calculate a 3D triangulation hyperboloid.
   * *Stage 3 (Orbital Determination):* Gauss/Laplace algorithms predict future satellite point-ahead positioning based on historical coordinates.
2. **Two-Layer Precision Beam Steering:**
   * *Coarse Steering:* A 6-degree-of-freedom **Stewart Platform (Hexapod)** acts as a high-frequency vibration damper and wide-angle tracker.
   * *Fine Steering:* A **Fast Steering Mirror (FSM)** driven by a piezoelectric actuator system corrects micro-vibrations in microseconds using closed-loop data from a Shack-Hartmann wavefront sensor.
3. **Communication & Error Protocols:**
   * *Modulation:* On-Off Keying (OOK) via a fast shutter mechanism (Flap Open = Bit 1, Flap Closed = Bit 0).
   * *Wavelength Division Multiplexing (WDM):* Simultaneously transmits a $1064\text{ nm}$ continuous tracking beacon and a $1550\text{ nm}$ high-speed data stream on a single optical path using a dichroic beamsplitter.
   * *Deterministic Error Correction:* Hardened **Reed-Solomon RS(255,223)** Forward Error Correction combined with **CCSDS Space Packet Protocol framing** to ensure guaranteed math bounds for zero-ambiguity packet recovery.

---

## 📂 Repository Structure
This repository is organized according to mandatory hackathon guidelines:
* **/simulation**: Core Python algorithms, data processing, and On-Off Keying (OOK) signal simulation code.
* **/hardware**: EasyEDA circuit schematics for LEO and InterPlanetary Satellites (IPS), Tinkercad 3D housing layouts, and Wokwi servo simulation files.
* **/docs**: Deep technical markdown documentation including `system_architecture.md`, `communication_protocol.md`, and `satellite_tracking.md`.
* **/presentation**: The final 15-slide project pitch deck presentation PDF.

---

## 🛠️ Tech Stack & Tools
* **Language:** Python 3.8+
* **Libraries:** NumPy (Vectorized signal parsing), Matplotlib (Signal waveform plotting)
* **Design & Electronics Tools:** EasyEDA (Circuit Schematics), Tinkercad (3D Housing), Wokwi (Servo simulation), draw.io (Architecture diagrams)
* **Presentation:** Canva

---

## 🚀 Getting Started & Simulation Setup

### Prerequisites
Ensure you have Python 3.8 or higher installed on your system. 

### Local Deployment
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Aditya242/Hackathon-PhotonRelay.git](https://github.com/Aditya242/Hackathon-PhotonRelay.git)
