# MAEG3010 Mechanics of Materials — Study Notes

> **Course type:** Major Required · 3 units
> **Official description:** Study of mechanics of materials — linear elasticity, stress and strain, stress-strain relations, loading and deformation, statically indeterminate problems, torsion, shear forces and bending moments, stresses in beams, deflection of beams, stresses in thin-walled pressure vessels, column and buckling.
> **Textbook:** Hibbeler Mechanics of Materials
> **Source:** `/app/bootcamps/msc-ire/mae-cuhk/courses/major-required/MAEG3010.md` (read-only)

## 🧭 Key topics (priority order for Week 4)

1. **Stress and strain / Hooke's law** — σ = Eε
   - Normal stress vs shear stress, axial vs shear strain
   - Hooke's law only valid in the linear-elastic region
2. **Torsion of circular shafts** — τ = Tr/J
   - J = polar moment of inertia for solid (πd⁴/32) vs hollow (π(D⁴−d⁴)/32) shafts
   - Angle of twist: φ = TL/(JG)
3. **Shear force & bending moment diagrams (SFD/BMD)**
   - At any cut: ΣF = 0, ΣM = 0
   - dV/dx = −w(x), dM/dx = V → relationships for quick checks
4. **Bending stresses + beam deflection**
   - σ = My/I (max at extreme fiber, y = c)
   - Deflection via double-integration or standard formulas (simply supported, cantilever)
5. **Column buckling** — Euler: P_cr = π²EI/(KL)²
   - K depends on end conditions (1=fixed-pinned, 2=fixed-fixed, etc.)
   - Slenderness ratio determines Euler vs inelastic regime
6. **Thin-walled pressure vessels**
   - Cylindrical: σ_hoop = pr/t, σ_long = pr/(2t)
   - Spherical: σ = pr/(2t)

## 📐 Key formulas (the cheat sheet)

| Domain | Formula | Notes |
|---|---|---|
| Axial | σ = P/A, ε = δ/L | Hooke's law: σ = Eε |
| Torsion | τ = Tr/J, φ = TL/(JG) | J solid = πd⁴/32 |
| Bending | σ = My/I, M_max = σ·S | Section modulus S = I/c |
| Deflection | y'' = M(x)/(EI) | double-integration method |
| Buckling | P_cr = π²EI/(KL)² | effective length KL matters |
| Pressure vessel | σ_hoop = pr/t, σ_long = pr/(2t) | thin wall: t ≪ r |

## 🎯 Learning outcomes (course-defined)

- Analyze stress and strain in structural members
- Determine internal forces and stresses in beams and shafts
- Solve deflection and buckling problems

## 🤖 Relevance to my robotics projects

- **3R arm simulator** — already considered material strength + deflection for the physical-version 3R arm (per upstream notes). Quantify instead of just feel it.
- **Soft gripper build (`builds/soft_gripper/`)** — bending / buckling comes up if the gripper frame is rigid enough relative to the actuator force; thin-walled vessel theory may be relevant if pneumatic.
- **Future FYP** — every load-bearing link in any robot hits at least one of: bending, torsion, buckling. This course is the foundation for not over-designing (waste) or under-designing (failure).

## 🛠️ How this maps to the simulator update

| Week 4 update | Simulator-side hook |
|---|---|
| Stress analysis | Add a `stress` panel to the 3R arm viewer showing max σ per link under current pose |
| Beam deflection | Compute y_max for cantilever link and overlay on the visual |
| Buckling check | For any compression-loaded link, compute slenderness and flag P_cr proximity |

## 🔁 Study plan (this weekend)

1. ✅ Read source `.md` (done in skill run)
2. ⏭ Flashcards (Anki) — see `../../skills/bootcamp-content-assistant/cards.tsv`
3. ⏭ Practice problems — see `practice.md` (6 explain-prompts)
4. ⏭ Solve 3 problems of each difficulty tier before checking source
5. ⏭ Map the formulas onto my 3R arm dimensions (link length, cross-section, material → E, yield)
6. ⏭ Update simulator with stress overlay

## ❓ Open questions to revisit later

- Statically indeterminate problems were in the official description but not listed in key topics — seek out Hibbeler Ch. 4 examples.
- Thin-walled pressure vessel hoop vs longitudinal ratio (2:1) — confirm by deriving from first principles in the practice session.
