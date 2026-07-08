# ELEG2202 Fundamentals of Electric Circuits — Study Notes (skeleton)

> **Course type:** Major Required · 3 units
> **Official description:** Intro electric circuits — KVL/KCL, theorems (Thevenin, Norton, superposition), circuit-analysis methods (nodal, mesh), op-amp circuits, linear feedback; AC (impedance, phasors, sinusoids, frequency response); power (transient, 3-phase, inductors, transformers, electromechanical); mandatory labs.
> **Source:** `/app/bootcamps/msc-ire/mae-cuhk/courses/major-required/ELEG2202.md` (read-only)
> **Status:** SKELETON — to be synthesized Sat 2026-07-11 after Anki review + practice

## 🧭 Key topics (priority order for Week 5)

_(filled in Saturday)_

1. KVL / KCL + circuit theorems (Thevenin, Norton, superposition)
2. Circuit analysis methods — nodal, mesh
3. Op-amp circuits + linear feedback
4. AC: impedance, phasors, sinusoids, frequency response
5. Power: transient analysis, 3-phase, inductors, transformers, electromechanical

## 🔑 Key formulas / diagrams

_(filled in Saturday)_

| Domain | Key relations |
|---|---|
| DC resistive | V = IR, P = V²/R, KCL: ΣI = 0 at node, KVL: ΣV = 0 around loop |
| Thevenin / Norton | V_th = V_oc, R_th = R_N = V_oc / I_sc |
| Op-amp (ideal) | V⁺ = V⁻, I⁺ = I⁻ = 0; inverting gain = −Rf/Ri; non-inv gain = 1 + Rf/Ri |
| AC phasor | V = V₀∠θ, Z = R + jX; impedance magnitude |Z| = √(R²+X²) |
| 3-phase | V_L = √3 · V_phase (line-to-line vs phase), P = √3 · V_L · I_L · cos φ |

## 🤖 IRE / my-project hooks

- **Sensor signal conditioning** → op-amp amplifier stages (inverting, non-inv, instrumentation)
- **Motor driver** → H-bridge, PWM, current sense resistor + amplifier
- **PID control** → electronic implementation of P / I / D terms (op-amp summers)
- **Power supply** → rectification, smoothing, regulation for the 3R arm electronics
- **Frequency response** → important for sensor band-limiting, anti-aliasing RC filters before ADC

## 🛰️ Simulator update (sensor modeling + electronics)

_(to design during the weekend session — modeling op-amp-based sensor amplifier?)_

## 📖 Textbook / references

- Sadiku "Fundamentals of Electric Circuits" (CL Chen partnership classic)
- Alexander & Sadiku "Fundamentals of Electric Circuits" (alternate)

## ✏️ Personal study plan

1. Sat AM: Anki deck (KCL/KVL examples, Thevenin equivalent, op-amp configurations)
2. Sat PM: Practice prompts — analyze a sensor preamp + driver circuit
3. Sun AM: Build a one-page op-amp cheat sheet for sensor-conditioning reference

## Status

- [ ] Theory notes completed
- [ ] Code / Simulator linked (sensor amplifier module)
- [ ] Reflection written
- [ ] Connected to PolyU MSc IRE courses
