type SkillSummary = {
  name: string;
  description: string;
};

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function renderIndexPage(
  skills: SkillSummary[],
  repositoryVersion: string,
  latestReleaseVersion: string | null,
  repository: string,
  repoSlug: string,
): string {
  const releaseLine = latestReleaseVersion
    ? `Latest release: <strong>${escapeHtml(latestReleaseVersion)}</strong>.`
    : "No GitHub release has been published yet.";
  const installAllCommand = `npx skills add ${repoSlug} --all --global`;

  const skillItems = skills
    .map((skill) => {
      const name = escapeHtml(skill.name);
      const description = escapeHtml(skill.description);
      const installCommand = escapeHtml(`npx skills add ${repoSlug} --skill ${skill.name}`);
      return `
            <li class="skill-card">
              <div class="skill-card-header">
                <p class="eyebrow">skill</p>
                <h3><a href="/${name}/SKILL.md">${name}</a></h3>
              </div>
              <p class="skill-description">${description}</p>
              <div class="install-block">
                <p class="install-label">Install this skill</p>
                <pre><code>${installCommand}</code></pre>
              </div>
              <div class="skill-actions">
                <a class="button button-secondary" href="/${name}/SKILL.md">View skill</a>
              </div>
            </li>
            `.trim();
    })
    .join("");

  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Parallel Agent Skills</title>
    <style>
      :root {
        --bg: #f9f8f4;
        --panel: #ffffff;
        --panel-alt: #f5f4f1;
        --text: #181818;
        --muted: #5c5b59;
        --subtle: #858483;
        --accent: #fb631b;
        --accent-hover: #f4793f;
        --border: #e5e5e5;
        --border-strong: #d6d6d6;
        --shadow: 0 1px 0 rgba(24, 24, 24, 0.02);
        --radius: 4px;
      }
      * { box-sizing: border-box; }
      html { scroll-behavior: smooth; }
      body {
        margin: 0;
        background: var(--bg);
        color: var(--text);
        font-family: "Helvetica Neue", Arial, ui-sans-serif, system-ui, sans-serif;
        line-height: 1.45;
      }
      a {
        color: inherit;
        text-decoration: none;
      }
      a:hover {
        text-decoration: underline;
        text-decoration-color: var(--accent);
      }
      main {
        max-width: 1240px;
        margin: 0 auto;
        padding: 24px 20px 80px;
      }
      .topbar {
        margin-bottom: 24px;
        padding: 12px 0;
        border-bottom: 1px solid var(--border);
        color: var(--muted);
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }
      .frame {
        display: grid;
        grid-template-columns: 1fr;
        gap: 20px;
        padding: 28px 24px;
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        box-shadow: var(--shadow);
      }
      .frame + .frame,
      .frame + .skills-section,
      .skills-section + .frame {
        margin-top: 20px;
      }
      .eyebrow {
        margin: 0 0 10px;
        color: var(--muted);
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }
      .hero-title {
        margin: 0;
        max-width: 11ch;
        font-size: clamp(44px, 8vw, 88px);
        line-height: 0.94;
        letter-spacing: -0.04em;
      }
      .meta-block {
        color: var(--muted);
        font-size: 14px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        align-items: flex-start;
      }
      .meta-block p { margin: 0; }
      .button-row,
      .skill-actions,
      .meta-links {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
      }
      .meta-links {
        margin-top: 2px;
      }
      .button-row {
        margin-top: 24px;
      }
      .button {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 14px;
        border: 1px solid transparent;
        border-radius: var(--radius);
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
      }
      .button-primary {
        background: var(--text);
        color: #fff;
      }
      .button-primary:hover {
        background: var(--accent);
        text-decoration: none;
      }
      .button-secondary {
        border-color: var(--border-strong);
        background: var(--panel);
      }
      .button-secondary:hover {
        border-color: var(--text);
        text-decoration: none;
      }
      .install-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
        gap: 24px;
      }
      .section-title {
        margin: 0;
        font-size: clamp(30px, 4vw, 52px);
        line-height: 0.98;
        letter-spacing: -0.04em;
      }
      .catalog-title {
        font-size: clamp(40px, 5vw, 64px);
        line-height: 0.94;
      }
      .section-copy,
      .install-side {
        color: var(--muted);
        font-size: 16px;
      }
      .install-block pre,
      .install-main pre {
        margin: 12px 0 0;
      }
      pre {
        margin: 0;
        padding: 14px 16px;
        overflow-x: auto;
        border: 1px solid var(--border);
        border-radius: var(--radius);
        background: var(--panel-alt);
      }
      code {
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: 13px;
      }
      .install-side ul {
        margin: 12px 0 0;
        padding-left: 18px;
      }
      .install-side li + li { margin-top: 8px; }
      .skills-section { margin-top: 20px; }
      .skills-header {
        padding: 0 4px 16px;
      }
      .skills-grid {
        list-style: none;
        padding: 0;
        margin: 0;
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
      }
      .skill-card {
        position: relative;
        padding: 22px 24px;
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        box-shadow: var(--shadow);
      }
      .skill-card-header h3 {
        margin: 0;
        font-size: 28px;
        line-height: 1.02;
        letter-spacing: -0.03em;
      }
      .skill-description {
        margin: 14px 0 18px;
        color: var(--muted);
        font-size: 16px;
      }
      .install-label {
        margin: 0;
        color: var(--subtle);
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }
      .skill-actions {
        margin-top: 16px;
      }
      @media (max-width: 920px) {
        .install-grid {
          grid-template-columns: 1fr;
        }
        .hero-title { max-width: none; }
        .skills-grid { grid-template-columns: 1fr; }
      }
      @media (max-width: 640px) {
        main { padding: 16px 12px 48px; }
        .frame,
        .skill-card { padding: 20px 18px; }
        .hero-title { font-size: 42px; }
      }
    </style>
  </head>
  <body>
    <main>
      <div class="topbar">Parallel / skills catalog</div>

      <section class="frame">
        <div class="meta-block">
          <p class="eyebrow">overview</p>
          <p>Repository version: <strong>${escapeHtml(repositoryVersion)}</strong></p>
          <p>${releaseLine}</p>
          <div class="meta-links">
            <a href="/index.json">index.json</a>
            <a href="/llms.txt">llms.txt</a>
          </div>
        </div>
        <div>
          <p class="eyebrow">## Parallel Agent Skills</p>
          <h1 class="hero-title">Install Parallel skills with one command.</h1>
          <div class="button-row">
            <a class="button button-primary" href="${escapeHtml(repository)}">GitHub repository</a>
            <a class="button button-secondary" href="#skills">Browse skills</a>
          </div>
        </div>
      </section>

      <section class="frame">
        <div>
          <p class="eyebrow">install</p>
          <h2 class="section-title">Start with all skills.</h2>
        </div>
        <div class="install-grid">
          <div class="install-main">
            <p class="section-copy">
              Install the full Parallel skills collection globally with the Agent Skills CLI.
            </p>
            <pre><code>${escapeHtml(installAllCommand)}</code></pre>
          </div>
          <div class="install-side">
            <p class="eyebrow">other options</p>
            <ul>
              <li><strong>Claude Code</strong>: <code>/plugin marketplace add parallel-web/parallel-agent-skills</code> then <code>/plugin install parallel</code></li>
              <li><strong>OpenAI Codex</strong>: <code>$skill-installer parallel-web/parallel-agent-skills</code></li>
            </ul>
          </div>
        </div>
      </section>

      <section class="skills-section" id="skills">
        <div class="skills-header">
          <p class="eyebrow">catalog</p>
          <h2 class="section-title catalog-title">Skills<br />catalog</h2>
        </div>
        <ul class="skills-grid">
          ${skillItems}
        </ul>
      </section>
    </main>
  </body>
</html>
`;
}
