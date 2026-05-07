# AnyLogic Build Guide — Stephen Center Shelter Front Office

This guide reproduces the three scenarios from the report inside
**AnyLogic 8.x** (Personal Learning Edition is sufficient). Follow the
sections in order; later sections reuse blocks from earlier ones.

> The file `ShelterSimulation.alp` in this folder documents the same
> structure as XML (block names, parameters, distributions, connections).
> Treat it as a reference; build the working model in AnyLogic by
> following the steps below.

---

## 0. Project setup

1. Launch AnyLogic and choose **File → New → Model…**.
2. Name the model `ShelterSimulation`. Set:
   - **Java package**: `sheltersimulation`
   - **Model time unit**: `Minutes`
3. Click **Finish**. A `Main` agent is created automatically — rename it
   to **`MainBase`** in the Projects panel.

---

## 1. Custom agent type — `Client`

1. In the Projects panel, right-click the model and choose
   **New → Agent Type**.
2. Name the new agent **`Client`** and click **Next**.
3. On the *Population* step, select **Single Agent** (we will only use
   it as a flow entity), then click **Finish**.
4. Open the `Client` agent and add **two parameters** (drag from the
   *Parameters* palette):

   | Name           | Type     | Default | Notes                            |
   |----------------|----------|---------|----------------------------------|
   | `requestType`  | `int`    | `0`     | 0=QQ, 1=SR, 2=RA, 3=LA           |
   | `serviceTime`  | `double` | `0.0`   | minutes; set in SelectOutput5    |

That's it for the agent — no extra logic lives inside the agent itself.

---

## 2. Base model — `MainBase`

The base model uses **one shared FIFO queue** and **two homogeneous
servers** (next-available rule). Service time is determined by request
type, not by which server picks up the agent.

### 2.1 Add the blocks

Drag these blocks from the **Process Modeling Library** onto the
`MainBase` canvas, in left-to-right order:

| Block              | Default class      | Rename to              |
|--------------------|--------------------|------------------------|
| Source             | `Source`           | `arrivals`             |
| SelectOutput5      | `SelectOutput5`    | `selectRequestType`    |
| Queue              | `Queue`            | `waitingLine`          |
| Service            | `Service`          | `serviceDesk`          |
| Sink               | `Sink`             | `exit`                 |

Also drag a **ResourcePool** onto the canvas and rename it **`staff`**.

### 2.2 Block-by-block parameters

Click each block and edit its properties in the bottom *Properties*
panel.

#### `arrivals` (Source)

| Property          | Value                            |
|-------------------|----------------------------------|
| New agent         | `Client`                         |
| Arrivals defined by | *Rate*                         |
| Rate              | `exponential(1.0/3.9)`           |
| Rate units        | *per minute*                     |

> **Why this expression?** AnyLogic interprets the *Rate* field as
> arrivals per time unit. Setting it to `exponential(1.0/3.9)` makes
> each inter-arrival ~Exponential with mean 3.9 minutes, which matches
> the observed 30-client sample.

#### `selectRequestType` (SelectOutput5)

This block does the 4-way probabilistic split that the professor asked
about. We only use four of its five outputs; leave the 5th probability
at 0.

| Output | Probability | On exit (action)                                            |
|--------|-------------|-------------------------------------------------------------|
| 1 (QQ) | `0.37`      | `agent.requestType = 0; agent.serviceTime = triangular(1, 3, 5);`  |
| 2 (SR) | `0.27`      | `agent.requestType = 1; agent.serviceTime = triangular(4, 6, 9);`  |
| 3 (RA) | `0.20`      | `agent.requestType = 2; agent.serviceTime = triangular(8, 12, 15);` |
| 4 (LA) | `0.16`      | `agent.requestType = 3; agent.serviceTime = triangular(10, 14, 20);` |
| 5      | `0.0`       | (unused)                                                    |

In the Properties panel, set **Selection method** to *Probability* and
fill in the five probability fields. Then expand each branch's
*Actions* section and paste the matching `On exit` snippet.

#### `waitingLine` (Queue)

| Property        | Value      |
|-----------------|------------|
| Capacity        | `20`       |
| Queuing policy  | *FIFO*     |
| Enable timeout  | unchecked  |
| Enable preemption | unchecked |

#### `serviceDesk` (Service)

| Property              | Value                |
|-----------------------|----------------------|
| Seize / Release       | *units of pool*      |
| Resource pool         | `staff`              |
| Number of seized units | `1`                 |
| Delay time            | `agent.serviceTime`  |
| Delay time units      | *minutes*            |

#### `staff` (ResourcePool)

| Property | Value |
|----------|-------|
| Capacity | `2`   |

#### `exit` (Sink)

Defaults are fine.

### 2.3 Connect the blocks

Draw connectors:

```
arrivals.out
   → selectRequestType.in
   → (out1, out2, out3, out4 each → waitingLine.in)
waitingLine.out → serviceDesk.in
serviceDesk.out → exit.in
```

All four SelectOutput branches should land on the same `waitingLine`
input — that gives you the single shared FIFO queue.

### 2.4 Statistics (recommended)

From the **Analysis** palette add:

- A **TimeMeasureStart** placed *before* `waitingLine.in` and a
  **TimeMeasureEnd** placed *after* `waitingLine.out`. Connect them so
  AnyLogic measures wait time per agent.
- A **Histogram** named `waitTimeHist` whose data source is the
  TimeMeasureEnd you just added.
- A **Variable** `totalServed` of type `int`, initial value `0`. In the
  `exit` Sink's **On enter** action, write `totalServed++;`.
- AnyLogic automatically tracks resource utilization on the `staff`
  pool — view it in the simulation window after a run.

### 2.5 Simulation experiment

Open the auto-created `Simulation` experiment and set:

| Property        | Value             |
|-----------------|-------------------|
| Model time unit | *Minutes*         |
| Stop            | *Stop at simulation time* |
| Stop time       | `120`             |
| Random seed     | *Random* (different per run) |

Run the model; verify on a single replication that:

- `totalServed` finishes between ~26 and ~34
- The queue length never exceeds the capacity of 20
- `serviceDesk` shows ~80–90% utilization

### 2.6 30 replications

To get the validation numbers in the slide deck, add a **Parameter
Variation** experiment:

1. **File → New → Experiment → Parameter Variation**.
2. Top-level agent: `MainBase`. Stop time: `120` minutes.
3. *Vary parameters* — leave at defaults.
4. *Replications per iteration*: `30`.
5. *Random seed*: *Use unique seed per replication*.
6. Run and read off the aggregate avg wait, avg queue, utilization.

---

## 3. Improvement 1 — Dedicated quick-service lane

This is the variant that uses **SelectOutput on `agent.requestType`** to
route short requests (QQ, SR) to one server and long requests (RA, LA)
to the other. This directly answers the professor's prompt about
servers having different effective distributions.

### 3.1 Create a new top-level agent `MainImprovement1`

Right-click the project → **New → Agent Type → Single Agent**, name it
`MainImprovement1`. Open it.

### 3.2 Reuse the source + SelectOutput5

Drag the same `Source` (`arrivals`) and `SelectOutput5`
(`selectRequestType`) blocks with **identical settings** as in §2.2.

### 3.3 Add the routing SelectOutput

Drag a **regular `SelectOutput`** (2-way) block. Rename it
**`routeByType`**.

| Property  | Value                       |
|-----------|-----------------------------|
| Condition | `agent.requestType <= 1`    |

This sends QQ (0) and SR (1) out of `outT`, and RA (2) and LA (3) out
of `outF`.

### 3.4 Two queues, two services, two pools

Add two `Queue` blocks (`queueA`, `queueB`), two `Service` blocks
(`serverA`, `serverB`), and two `ResourcePool`s (`staffA`, `staffB`).

| Block      | Capacity / Pool        | Delay time          |
|------------|------------------------|---------------------|
| `queueA`   | capacity 20, FIFO       | —                   |
| `queueB`   | capacity 20, FIFO       | —                   |
| `serverA`  | pool=`staffA`, units=1  | `agent.serviceTime` |
| `serverB`  | pool=`staffB`, units=1  | `agent.serviceTime` |
| `staffA`   | capacity 1              | —                   |
| `staffB`   | capacity 1              | —                   |

Add a `Sink` named `exit`.

### 3.5 Connect

```
arrivals.out → selectRequestType.in
selectRequestType.out1..out4 → routeByType.in
routeByType.outT → queueA.in → serverA.in → exit.in
routeByType.outF → queueB.in → serverB.in → exit.in
```

### 3.6 Experiment

Add a Parameter Variation experiment named
`Improvement1Replications` exactly like §2.6, but pointing at
`MainImprovement1`.

---

## 4. Improvement 2 — Add a 3rd staff member during peak

This variant matches the base model 1-for-1 but uses **3 servers** for
the entire 2-hour observation window (a simplification of "add a
volunteer for the 6:00–7:00 PM peak").

### 4.1 Create `MainImprovement2`

Right-click → **New → Agent Type → Single Agent**, name
`MainImprovement2`.

### 4.2 Copy the base flow

The simplest path:

1. Open `MainBase`, select all blocks (Ctrl+A on the canvas), copy.
2. Switch to `MainImprovement2`, paste.

### 4.3 Change two values

| Block        | Property | New value |
|--------------|----------|-----------|
| `staff`      | Capacity | `3`       |
| `serviceDesk` | (no change) | — keep `agent.serviceTime` |

That's the only change. Same arrivals, same SelectOutput5, same
distributions.

### 4.4 Experiment

Add `Improvement2Replications` Parameter Variation experiment as in
§2.6 but pointing at `MainImprovement2`.

---

## 5. Reading off the comparison numbers

After running each Parameter Variation experiment over its 30
replications:

| Metric              | Where to read                                    |
|---------------------|--------------------------------------------------|
| Average wait time   | Mean of TimeMeasureEnd histogram across runs     |
| Maximum wait time   | Max of TimeMeasureEnd across runs                |
| Average queue length | Mean of `waitingLine.size()` over time          |
| Server utilization  | `staff` (or `staffA`/`staffB`) utilization stat  |
| Clients served      | Mean of `totalServed`                            |

Plug those into the comparison table on Slide 8 of the deck.

---

## 6. Troubleshooting

- **"Cannot find symbol agent"** in a SelectOutput action → make sure
  you used `agent.requestType` (the implicit `agent` variable inside an
  *On exit* action) and not `Client.requestType`.
- **All clients leave on a single SelectOutput branch** → check the
  Selection method is *Probability*, not *Condition*, and that all four
  probabilities sum to ≤ 1.0 (the engine routes leftover probability to
  output 5).
- **Server B never serves anyone in Improvement 1** → make sure both
  `serverA` and `serverB` are connected to `exit`, and that the
  `routeByType.outT`/`outF` connections go to the correct queues.
- **Utilization > 100%** in the base model → that means demand exceeds
  capacity in this 2-hour window; this is expected on some replications
  and is exactly the bottleneck the improvements are meant to relieve.
