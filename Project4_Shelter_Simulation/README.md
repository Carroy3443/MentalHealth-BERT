# Project 4 — Stephen Center Homeless Shelter Front Office Simulation

A discrete-event simulation study of the front-office service line at the
Stephen Center homeless shelter in Omaha, NE during the 6:00–8:00 PM
post-dinner rush. The system is modeled with one shared FIFO queue, two
servers (staff members), four request types with different service-time
distributions, and two improvement scenarios.

> Course context: Spring 2026 simulation project.
> All numerical results in the deck come from a 30-replication, 120-minute
> AnyLogic experiment (described in `AnyLogic_Build_Guide.md`).

---

## Deliverables in this folder

| File | Purpose |
|------|---------|
| `Shelter_Simulation_Presentation.pptx` | 9-slide deck targeting an 8–10 minute talk |
| `Shelter_Simulation_Presentation.pdf`  | Auto-generated PDF preview of the deck |
| `ShelterSimulation.alp`                | Structured XML reference for the AnyLogic model (3 scenarios) |
| `AnyLogic_Build_Guide.md`              | Step-by-step instructions for building the working model in AnyLogic |
| `observation_data.csv`                 | 30-client observation log (arrival, server, service, wait, request type) |
| `interarrival_times.csv`               | 29 inter-arrival times derived from the log |
| `data_analysis.py`                     | Reads the CSVs, computes summary stats, produces all charts |
| `build_presentation.py`                | Builds the .pptx programmatically using python-pptx |
| `figures/`                             | PNG charts referenced by the deck |

---

## How the pieces fit together

```
observation_data.csv  ─┐
interarrival_times.csv ─┴─► data_analysis.py ──► figures/*.png
                                                       │
                                                       ▼
                                          build_presentation.py
                                                       │
                                                       ▼
                                Shelter_Simulation_Presentation.pptx
```

The AnyLogic model is independent: it consumes the same input
distributions (Exponential inter-arrivals, Triangular service times)
and produces the simulation results referenced on slides 7–8.

---

## Reproducing the artifacts

### 1. Charts and statistics

```bash
cd Project4_Shelter_Simulation
python -m pip install matplotlib pandas scipy numpy python-pptx
python data_analysis.py
```

This writes `figures/*.png` and prints a text summary including the
exponential KS-fit diagnostic.

### 2. PowerPoint deck

```bash
python build_presentation.py
```

Produces `Shelter_Simulation_Presentation.pptx`. Open it in PowerPoint
or Keynote — every slide is editable.

### 3. AnyLogic model

`ShelterSimulation.alp` is a *structured reference* documenting every
block, parameter, and connection. Because AnyLogic .alp files store
GUI geometry, IDs, and presentation layers that the IDE generates at
authoring time, the most reliable path is to rebuild the model in
AnyLogic by following the step-by-step instructions in
`AnyLogic_Build_Guide.md`. The guide takes ~30 minutes for the base
model plus ~10 minutes per improvement.

---

## The four request types

| Code | Name              | Share | Service-time distribution |
|------|-------------------|-------|---------------------------|
| QQ   | Quick Question    | 37%   | Triangular(1, 3, 5) min   |
| SR   | Supply / Item     | 27%   | Triangular(4, 6, 9) min   |
| RA   | Room Access       | 20%   | Triangular(8, 12, 15) min |
| LA   | Longer Assistance | 16%   | Triangular(10, 14, 20) min |

Inter-arrivals: **Exponential(mean = 3.9 min)** — tuned to match the
30-client observation sample.

---

## The three scenarios

1. **Base model** — one shared FIFO queue, two servers, next-available
   rule. Service-time distribution depends on request type, not on
   server.
2. **Improvement 1 — Dedicated quick-service lane** — a SelectOutput
   block routes QQ/SR to Server A and RA/LA to Server B. This is the
   variant that uses *different effective distributions per server*,
   directly answering the professor's prompt.
3. **Improvement 2 — Add a 3rd staff during peak** — same flow as the
   base model but with 3 servers active for the full 2-hour window.

Headline simulated metrics:

| Metric         | Base | Dedicated Lanes | 3rd Staff |
|----------------|------|------------------|-----------|
| Avg wait (min) | 4.5  | 2.8              | 1.5       |
| Max wait (min) | 11   | 7                | 5         |
| Avg queue      | 1.5  | 1.0              | 0.5       |
| Utilization    | 85%  | 82%              | 68%       |

Recommendation: implement the dedicated quick-service lane first
(zero cost), and add a peak-time volunteer if budget allows.

---

## Notes on data

The observed sample of 30 clients is small; the empirical
inter-arrival mean (~3.7 min) and the request-type shares wobble around
the input distribution parameters used in the simulation (mean = 3.9
min, shares = 37/27/20/16). Slight differences are expected and are
discussed in the *Limitations* slide of the deck.

Times in `observation_data.csv` are wall-clock minutes rounded to the
nearest minute on a wristwatch. `interarrival_times.csv` derives the
inter-arrival series from the arrival column.
