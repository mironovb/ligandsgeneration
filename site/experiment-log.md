---
layout: default
title: Experiment Log
nav_order: 5
---

# Experiment log
{: .no_toc }

Every sbatch run, grouped by phase, rendered from `_data/experiments.yml`. All jobs ran on
a university HPC cluster; its preemptible partition has a **4 h wall limit**, which is why
several long runs show `timed-out`. Dates are shown only where a log prints them (training
and the sweep); they are left blank rather than guessed elsewhere.

{: .note }
> **How to append a new run (the living-tracker mechanism).** When a future sbatch
> finishes: open `_data/experiments.yml`, copy one entry block, and fill every field from
> the job's `.out`/`.err` log — `job_id`, `partition`, the line that prints the result
> (into `key_result`), and `status` (one of `completed-clean`, `completed`, `timed-out`,
> `errored`, `incomplete`). Set `phase` to slot it into the right table below, and leave
> `date` empty unless the log prints it. Then add a dated line to the
> [Changelog](changelog.html). This table re-renders automatically — no other edits
> needed.

{% assign phases = "setup,training,generation,xtb,sweep,design,not-run" | split: "," %}
{% assign phase_titles = "Setup & smoke tests,Training (fine-tuning),Generation (mask-1 completion),xTB post-processing,RePaint resample sweep,Design test (completion vs de-novo),Scripted but never run" | split: "," %}

{% for ph in phases %}
## {{ phase_titles[forloop.index0] }}
{: .no_toc }

<div style="overflow-x:auto;">
<table>
  <thead>
    <tr>
      <th>Job ID</th><th>Sbatch</th><th>Partition</th><th>When</th><th>Status</th><th>Outcome</th><th>Key result</th><th>Notes</th>
    </tr>
  </thead>
  <tbody>
  {% for e in site.data.experiments %}{% if e.phase == ph %}
    {% case e.status %}
      {% when 'completed-clean' %}{% assign sc = '#16a34a' %}
      {% when 'completed' %}{% assign sc = '#15803d' %}
      {% when 'timed-out' %}{% assign sc = '#d97706' %}
      {% when 'incomplete' %}{% assign sc = '#d97706' %}
      {% when 'errored' %}{% assign sc = '#dc2626' %}
      {% else %}{% assign sc = '#64748b' %}
    {% endcase %}
    <tr>
      <td>{% if e.job_id != "" %}<code>{{ e.job_id }}</code>{% else %}—{% endif %}</td>
      <td><code>{{ e.sbatch }}</code>{% if e.job_name != "" %}<br><span style="font-size:0.82em; color:#64748b;">-J {{ e.job_name }}</span>{% endif %}</td>
      <td>{{ e.partition }}</td>
      <td>{% if e.date != "" %}{{ e.date }}{% else %}—{% endif %}{% if e.gpu_hours != "" %}<br><span style="font-size:0.82em; color:#64748b;">~{{ e.gpu_hours }} GPU-h</span>{% endif %}</td>
      <td><span style="display:inline-block; padding:0.1em 0.5em; border-radius:10px; font-size:0.8em; font-weight:600; color:#fff; background:{{ sc }};">{{ e.status }}</span></td>
      <td>{{ e.outcome }}</td>
      <td><strong>{{ e.key_result }}</strong></td>
      <td style="font-size:0.86em; color:#475569;">{{ e.notes }}</td>
    </tr>
  {% endif %}{% endfor %}
  </tbody>
</table>
</div>
{% endfor %}

---

**Phase totals.** Training ≈ 10 GPU-h across the three sessions that made progress
(crash → time-limit → clean early-stop), preceded by five failed resume attempts. The
completed RePaint sweep produced **171 valid structures** (29 + 85 + 57), or **210**
including r = 20. The design test settled the headline result: **0 valid / 6,300** from a
bare metal. See [Results](results.html) for the analysis.
