# Communication Protocol — PhotonRelay

PhotonRelay's protocol stack has four layers, each solving a distinct problem: **OOK** converts bits to light pulses, **WDM** carries two signals on one beam, **CCSDS** provides structured interplanetary-standard framing, and **Reed-Solomon FEC** guarantees error recovery without any retransmission.

---

## Section 1 — On-Off Keying (OOK) Modulation

**What it is:** The physical-layer scheme that converts a binary bit stream into pulses of 1550 nm laser light using a mechanical servo-motor shutter.

**Encoding logic:**

| Flap State | Servo Angle | Laser | Bit |
|---|---|---|---|
| Open | 90° | Light passes through | `1` |
| Closed | 0° | Light is blocked | `0` |

**How a message becomes light pulses:**
1. Raw data is structured into CCSDS packets and RS(255,223) FEC is applied
2. The resulting bit stream is clocked to the servo driver at the **TCXO rate**
3. Each `1` bit → servo rotates to 90°, flap opens, laser passes → **light pulse**
4. Each `0` bit → servo rotates to 0°, flap closes, laser blocked → **silence**
5. The modulated 1550 nm beam exits through the telescope aperture toward the receiver

**Receive side:**
- **InGaAs photodetector** converts incoming light pulses → electrical current
- **TIA** converts current → measurable voltage
- **STM32** samples at the same TCXO clock rate → reconstructs the original bit stream

---

## Section 2 — Wavelength Division Multiplexing (WDM)

**What it is:** Two separate signals — a position beacon and data — carried simultaneously on the same optical path using two near-infrared wavelengths. A **dichroic beamsplitter** separates them at the receiver with no mechanical switching.

| Wavelength | Role | Modulation | Beam Profile | Received By |
|---|---|---|---|---|
| **1064 nm** | Position / beacon | Continuous wave | Wide divergence — easy to acquire and lock | 1064 nm BPF → CMOS focal array |
| **1550 nm** | Data / message | OOK via servo flap | Narrow beam — high bandwidth | Fabry-Perot filter → InGaAs detector |

**Separation method:**
- Dichroic beamsplitter **reflects 1064 nm** and **transmits 1550 nm**
- Both wavelengths enter the telescope on one aperture and are cleanly separated at this single element

**Why two wavelengths matter:**
- The **1064 nm beacon** runs continuously — the tracking system can maintain lock even if the data link drops
- The **1550 nm data laser** is narrow and OOK-modulated — optimised purely for bandwidth and directionality
- Tracking and data are **physically independent** — losing one does not affect the other

---

## Section 3 — CCSDS Packet Framing

**What it is:** All data is structured using the **Consultative Committee for Space Data Systems (CCSDS) Space Packet Protocol** — the standard used across all interplanetary missions. CCSDS allows the receiver to locate, verify, and parse every frame reliably even after partial data loss mid-stream.

**Frame structure:**

| Field | Content | Purpose |
|---|---|---|
| **Sync Marker** | Fixed pattern e.g. `0xFAF320` | Marks the start of every frame — receiver re-synchronises here even after mid-stream data loss |
| **Primary Header** | Packet version, spacecraft ID, sequence count, data length, TCXO timestamp | Identifies the packet, its origin, sequence order, and exact transmission time |
| **RS Payload** | 223 bytes data → RS-encoded to 255 bytes | Actual mission data, pre-protected with 32 RS redundancy bytes before transmission |
| **CRC-16** | 2-byte checksum over the full frame | Quick integrity check verified before RS decoding is attempted |

**Frame assembly — step by step:**
1. Raw data split into **223-byte chunks**
2. RS(255,223) encoding applied → **255-byte blocks** (32 redundancy bytes appended)
3. CCSDS primary header prepended (spacecraft ID, sequence count, TCXO timestamp, data length)
4. Sync marker prepended to the frame
5. CRC-16 checksum appended
6. Complete frame serialised → sent to servo driver → OOK modulated onto 1550 nm laser

**Frame parsing at the receiver:**
1. STM32 scans the incoming bit stream for the **sync marker** to locate frame boundaries
2. **CRC-16** verified — frame discarded if it fails, before RS decoding is attempted
3. **RS decoder** corrects up to 16 corrupted bytes per 255-byte block
4. CCSDS parser strips the header and extracts the original 223-byte payload

---

## Section 4 — Reed-Solomon Forward Error Correction (FEC)

**What it is:** A deterministic error correction scheme applied to every data block before transmission. If bytes are corrupted or lost in transit, the receiver reconstructs the original data exactly — no retransmission needed.

**How RS(255,223) works:**

| Property | Detail |
|---|---|
| Block structure | 223 bytes of data → encoded into a **255-byte block** |
| Redundancy added | **32 redundancy bytes** appended per block (255 − 223 = 32) |
| Error correction | Up to **16 corrupted or lost bytes per block** recovered perfectly |
| Overhead | ~14% — a small, fixed cost for guaranteed recovery |
| Failure behaviour | If >16 bytes are corrupted → **error is flagged**, never silently returning bad data |

**Why RS instead of ML-based signal reconstruction:**

| Criterion | Reed-Solomon | ML-based |
|---|---|---|
| Correction guarantee | **Mathematically proven** — hard limit | None — output is probabilistic |
| Silent bad data risk | **Impossible** — error is always flagged | A model can confidently return wrong data |
| Determinism | Fixed compute cycles on STM32 | Unpredictable latency and resource use |
| Decision | ✅ Chosen | ❌ Dropped |

> In communication systems, a result that says **"I cannot recover this"** is safer than one that silently returns wrong data. Reed-Solomon provides a hard mathematical bound; ML does not — which is why RS was chosen.
