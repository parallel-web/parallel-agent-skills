export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const archiveMatch = url.pathname.match(/^\/archives\/([^/]+)\/([^/]+)\.zip$/);

    if (archiveMatch) {
      const [, skillName, version] = archiveMatch;
      const redirectUrl = `https://github.com/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/releases/download/v${version}/${skillName}-${version}.zip`;
      return new Response(null, {
        status: 302,
        headers: {
          Location: redirectUrl,
          "Cache-Control": "public, max-age=300",
        },
      });
    }

    return env.ASSETS.fetch(request);
  },
};
