# PDF Templates + Jurisdiction Disclosures
Status: planned (2026-01-08)
Owner: TBD

## 1) Summary
Introduce a lightweight template registry and jurisdiction-specific disclosure
blocks for the PDF renderer, while keeping rendering deterministic.

## 2) Goals
- Support selecting a named template in `opie_pdf.render`.
- Inject jurisdiction-specific disclosures into the PDF output.
- Keep default output stable when no template/disclosure is specified.

## 3) Non-goals
- Full regulatory compliance or localization platform.
- Complex layout tooling or external template engines.
- Network calls or runtime fetches.

## 4) Proposed structure
- `opie_pdf/templates/` for base templates and registry.
- `opie_pdf/disclosures/` for jurisdiction text packs (JSON or YAML).
- Extend `render_pdf(..., template_id="base", jurisdiction=None)`.

## 5) Diff-by-diff plan
1) Add template registry:
   - Define a minimal template interface and a default "base" template.
   - Provide a registry lookup by `template_id`.
2) Add disclosure packs:
   - Define a simple schema for jurisdiction-specific text blocks.
   - Load disclosures deterministically (sorted keys, stable ordering).
3) Renderer integration:
   - Extend `render_pdf` to accept `template_id` and `jurisdiction`.
   - Inject disclosures into the template at a fixed location.
4) Tests + docs:
   - Tests that specific disclosure text appears in generated PDFs.
   - README snippet showing template/disclosure usage.

## 6) Acceptance criteria
- `render_pdf` supports `template_id` and `jurisdiction` without breaking
  existing call sites.
- Disclosures appear in output when provided; default output remains unchanged.
- PDF output is deterministic for the same input.
