# frozen_string_literal: true

# =============================================================================
# AI-context export generator.
#
# Bundles the whole site into one Markdown document for pasting into an LLM, and
# writes two static files served at the site root:
#
#   /llms-full.txt  — every content page concatenated, in nav order (the export)
#   /llms.txt       — a short index of those pages (the llms.txt convention,
#                     https://llmstxt.org/)
#
# It also stashes the full text in `site.data["ai_context"]` so the human-facing
# /ai-context/ page can embed it for copy-to-clipboard / download-as-.md.
#
# WHY A PLUGIN (not pure Liquid): two pages — the Experiment Log and Background —
# build their real content from `_data/*.yml` via Liquid loops. To capture that,
# we render each page's *Liquid* (which expands the loops, the status include,
# and `relative_url`) but deliberately NOT its Markdown, so the result stays
# Markdown. Doing this at the `:generate` stage is also when `page.content` is
# guaranteed to still be the raw source. Kramdown-only artifacts (callouts,
# the auto "On this page" TOC) are then cleaned up below.
#
# Deployment runs `bundle exec jekyll build` (see ../.github/workflows/pages.yml),
# so custom plugins like this one load normally — this is not GitHub's safe mode.
# =============================================================================

module AiContext
  # Kramdown callout IALs (defined in _config.yml) -> a plain-text label, so the
  # "this is a caveat / negative result" signal survives into the flat export.
  CALLOUT_LABELS = {
    "note"       => "**Note —**",
    "works"      => "**Verified —**",
    "caveat"     => "**Metric caveat —**",
    "unverified" => "**Unverified —**",
    "fails"      => "**Negative result —**",
  }.freeze

  module_function

  # Content pages to export: every page that carries a numeric `nav_order`
  # (that is exactly the sidebar pages), minus anything opting out — sorted the
  # same way the sidebar is.
  def content_pages(site)
    site.pages.select do |p|
      p.data["nav_order"].is_a?(Numeric) &&
        !p.data["exclude_from_ai_context"]
    end.sort_by { |p| p.data["nav_order"] }
  end

  # Render a page's Liquid (expands includes / data loops / relative_url) without
  # converting Markdown. Mirrors what Jekyll::Renderer does for the Liquid step.
  def render_liquid(site, page, payload)
    payload["page"] = page.to_liquid
    liquid_opts = site.config["liquid"] || {}
    info = {
      :registers        => { :site => site, :page => payload["page"] },
      :strict_filters   => liquid_opts["strict_filters"],
      :strict_variables => liquid_opts["strict_variables"],
    }
    site.liquid_renderer.file(page.path).parse(page.content).render!(payload, info)
  rescue StandardError => e
    Jekyll.logger.warn "AI context:", "could not render #{page.path}: #{e.message}"
    page.content
  end

  # Turn rendered-Liquid output into clean, flat Markdown.
  def clean(body)
    s = body.dup

    # Drop the just-the-docs auto "On this page" TOC block (a <details> wrapper).
    s = s.gsub(%r{<details[^>]*>\s*<summary>\s*On this page\s*</summary>.*?</details>}m, "")

    # Callout IAL + its blockquote -> fold the label into the quote's first line.
    s = s.gsub(/^[ \t]*\{:[ \t]*\.(#{CALLOUT_LABELS.keys.join("|")})[ \t]*\}[ \t]*\n+(>.*(?:\n>.*)*)/) do
      label = CALLOUT_LABELS[Regexp.last_match(1)]
      Regexp.last_match(2).sub(/\A>[ \t]?/, "> #{label} ")
    end

    # Any callout IAL not followed by a blockquote -> a standalone label line.
    s = s.gsub(/^[ \t]*\{:[ \t]*\.(#{CALLOUT_LABELS.keys.join("|")})[ \t]*\}[ \t]*$/) do
      CALLOUT_LABELS[Regexp.last_match(1)]
    end

    # Remaining kramdown attribute lists / {:toc} (whole-line, then trailing).
    s = s.gsub(/^[ \t]*\{:[^}\n]*\}[ \t]*$/, "")
    s = s.gsub(/[ \t]*\{:[^}\n]*\}[ \t]*$/, "")

    # Tidy whitespace.
    s = s.gsub(/[ \t]+$/, "")
    s = s.gsub(/\n{3,}/, "\n\n")
    s.strip
  end

  def page_title(page)
    page.data["title"] || page.url
  end

  # baseurl-prefixed URL (correct on the deployed project site, e.g. /ligandgen/...).
  def url_for(site, page)
    base = site.config["baseurl"].to_s
    base.empty? ? page.url : "#{base}#{page.url}"
  end
end

module Jekyll
  class AiContextGenerator < Generator
    safe false
    priority :low # run after data is loaded and other generators have populated pages

    def generate(site)
      pages = AiContext.content_pages(site)
      return if pages.empty?

      payload = site.site_payload
      rendered = pages.map { |p| [p, AiContext.clean(AiContext.render_liquid(site, p, payload))] }

      full  = build_full(site, rendered)
      index = build_index(site, pages)

      site.data["ai_context"] = {
        "full"  => full,
        "index" => index,
        "count" => pages.size,
      }

      add_text_file(site, "llms-full.txt", full)
      add_text_file(site, "llms.txt", index)
      Jekyll.logger.info "AI context:", "exported #{pages.size} pages to /llms.txt + /llms-full.txt"
    rescue StandardError => e
      # Never let this optional feature break the site build.
      Jekyll.logger.warn "AI context:", "skipped (#{e.class}: #{e.message})"
    end

    private

    def build_full(site, rendered)
      title   = site.config["title"] || "Site"
      desc    = site.config["description"]
      out = +"# #{title} — full text export\n\n"
      out << "> #{desc}\n\n" if desc && !desc.empty?
      out << "Single-document export of the entire site, for use as AI / LLM context. "
      out << "Pages appear in site-navigation order; the experiment-log and paper tables are "
      out << "fully expanded. Regenerated on every build.\n\n"
      out << status_line(site)
      out << "## Contents\n\n"
      rendered.each_with_index do |(page, _), i|
        out << "#{i + 1}. #{AiContext.page_title(page)} — `#{AiContext.url_for(site, page)}`\n"
      end
      out << "\n"
      rendered.each_with_index do |(page, body), i|
        out << "\n---\n\n"
        out << "<!-- PAGE #{i + 1}/#{rendered.size} · #{AiContext.page_title(page)} · #{AiContext.url_for(site, page)} -->\n\n"
        out << body
        out << "\n"
      end
      out
    end

    def build_index(site, pages)
      title = site.config["title"] || "Site"
      desc  = site.config["description"]
      full_url = "#{site.config["baseurl"]}/llms-full.txt"
      out = +"# #{title}\n\n"
      out << "> #{desc}\n\n" if desc && !desc.empty?
      out << "Index for use as AI / LLM context (the llms.txt convention — https://llmstxt.org/).\n"
      out << "The full text of every page below is concatenated at #{full_url}.\n\n"
      out << status_line(site)
      out << "## Pages\n\n"
      pages.each do |page|
        line = "- [#{AiContext.page_title(page)}](#{AiContext.url_for(site, page)})"
        d = page.data["description"]
        line << ": #{d}" if d && !d.empty?
        out << line << "\n"
      end
      out << "\n## Full text\n\n"
      out << "- [Complete site as a single Markdown document](#{full_url})\n"
      out
    end

    def status_line(site)
      date = site.config["status_date"]
      summary = site.config["status_summary"]
      return "" unless date || summary
      "**Status as of #{date}.** #{summary}\n\n"
    end

    def add_text_file(site, name, content)
      page = PageWithoutAFile.new(site, site.source, "", name)
      page.content = content
      page.data["layout"] = nil
      page.data["sitemap"] = false
      page.data["render_with_liquid"] = false # content is final; don't reprocess
      site.pages << page
    end
  end
end
