---
layout: default
title: AI Context
nav_order: 9
exclude_from_ai_context: true
description: "Export the whole tracker as one Markdown document for AI / LLM context — copy to clipboard or download as .md."
---

# AI context export
{: .no_toc }

{% include status.html %}

Paste this entire tracker into an LLM in one shot. This page bundles **every content
page** — Background, Dataset, Methods, Results, Code Review, Experiment Log, Strategy,
Conclusions, and the Changelog — into a single Markdown document, with the data-driven
tables (the experiment log and the paper list) fully expanded. It is regenerated on every
site build, so it always matches what is published here.

{: .note }
> Useful for asking an assistant to summarize the project, sanity-check a claim against its
> cited source, draft text, or answer questions across pages. Numbers carry their on-page
> source tags; the *unverified* / *negative result* callouts are preserved as labels.

<div style="display:flex; flex-wrap:wrap; gap:0.6rem; align-items:center; margin:1.4rem 0 0.6rem;">
  <button id="ai-copy" type="button"
    style="cursor:pointer; font:inherit; font-weight:600; color:#fff; background:#2563eb; border:none; border-radius:6px; padding:0.55em 1.1em;">
    Copy all Markdown
  </button>
  <button id="ai-download" type="button"
    style="cursor:pointer; font:inherit; font-weight:600; color:#1e293b; background:#fff; border:1px solid #cbd5e1; border-radius:6px; padding:0.55em 1.1em;">
    Download .md
  </button>
  <span id="ai-stats" style="color:#64748b; font-size:0.9em;"></span>
</div>

<p style="font-size:0.92em; color:#475569; margin-top:0.4rem;">
  Prefer a raw file or <code>curl</code>? The same content is served as
  <a href="{{ '/llms-full.txt' | relative_url }}">/llms-full.txt</a> (full text), with a
  short <a href="{{ '/llms.txt' | relative_url }}">/llms.txt</a> index
  (the <a href="https://llmstxt.org/">llms.txt</a> convention).
</p>

<textarea id="ai-context" readonly spellcheck="false" aria-label="Full site export as Markdown"
  style="width:100%; height:460px; margin-top:0.5rem; padding:0.8em; box-sizing:border-box;
         font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:0.82em;
         line-height:1.5; color:#1e293b; background:#f8fafc; border:1px solid #cbd5e1;
         border-radius:6px; white-space:pre; overflow:auto; resize:vertical;">{{ site.data.ai_context.full | escape }}</textarea>

<script>
(function () {
  var ta      = document.getElementById('ai-context');
  var copyBtn = document.getElementById('ai-copy');
  var dlBtn   = document.getElementById('ai-download');
  var stats   = document.getElementById('ai-stats');
  if (!ta) { return; }

  // textarea.value is the decoded text — the exact Markdown to copy / download.
  var text = ta.value;

  var words  = (text.trim().match(/\S+/g) || []).length;
  var kb     = Math.round(text.length / 1024);
  var tokens = Math.round(text.length / 4); // rough ~4 chars/token estimate
  stats.textContent = '≈ ' + words.toLocaleString() + ' words · ' +
                      kb.toLocaleString() + ' KB · ~' + tokens.toLocaleString() + ' tokens';

  function flash(btn, msg) {
    if (!btn.dataset.label) { btn.dataset.label = btn.textContent; }
    btn.textContent = msg;
    setTimeout(function () { btn.textContent = btn.dataset.label; }, 1600);
  }

  function fallbackCopy() {
    ta.focus();
    ta.select();
    try {
      flash(copyBtn, document.execCommand('copy') ? 'Copied ✓' : 'Press ⌘/Ctrl+C');
    } catch (e) {
      flash(copyBtn, 'Press ⌘/Ctrl+C');
    }
    if (window.getSelection) { window.getSelection().removeAllRanges(); }
  }

  copyBtn.addEventListener('click', function () {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(
        function () { flash(copyBtn, 'Copied ✓'); },
        fallbackCopy
      );
    } else {
      fallbackCopy();
    }
  });

  dlBtn.addEventListener('click', function () {
    var blob = new Blob([text], { type: 'text/markdown;charset=utf-8' });
    var url  = URL.createObjectURL(blob);
    var a    = document.createElement('a');
    a.href = url;
    a.download = 'lanthanide-ligandgen-context.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    flash(dlBtn, 'Downloaded ✓');
  });
})();
</script>
