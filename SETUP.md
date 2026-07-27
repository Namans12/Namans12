# Setup

How to get this README live on <https://github.com/Namans12>, and how to keep it
working when a third-party card service falls over.

---

## 1. The profile repository already exists

GitHub renders a README on your profile page only from a **public repository whose
name is exactly your username**. Yours already exists and is correctly set up:

| | |
| --- | --- |
| Repo | `Namans12/Namans12` |
| Visibility | Public ✓ |
| Default branch | **`master`** (not `main`) |
| Current contents | `README.md` — GitHub's untouched default template |

So **do not run `gh repo create`** — it fails with
`Name already exists on this account`. Clone it instead:

```bash
git clone https://github.com/Namans12/Namans12.git
```

The existing README is the stock "Hi there 👋" placeholder with a commented-out list of
prompts. There is nothing in it worth keeping, so replacing it outright is safe.

## 2. Copy the files in

From this folder, copy into the repo root, overwriting the old README:

```
README.md
.github/workflows/snake.yml
```

`CUSTOMIZE.md`, `SETUP.md` and `verify-links.ps1` are for you — commit them too
(they're useful six months from now when you've forgotten how the snake works), or keep
them local. They don't affect what renders on your profile.

```bash
git add . && git commit -m "Profile README: Midnight Aurora" && git push
```

## 3. Turn on the contribution snake

The snake is the one piece that needs GitHub Actions. Until you do this, that image
will 404.

1. **Settings → Actions → General → Workflow permissions**
2. Select **Read and write permissions** → **Save**.
   Without this the workflow can't push the generated SVG and fails with
   `Permission to Namans12/Namans12.git denied`.
3. **Actions** tab → **Contribution Snake** → **Run workflow**.
4. Wait ~40 seconds. A new branch called **`output`** appears containing two SVGs.

After that it re-runs twice daily on its own.

Verify it worked:

```bash
git ls-remote --heads origin output
```

## 4. Check nothing is broken

```powershell
.\verify-links.ps1
```

Every URL in the README gets fetched and reported. Run it now, and again any time
your profile starts looking wrong.

---

## When a card stops rendering

This is the part nobody tells you about. Profile READMEs depend on free, community-run
services, and they break. Two are broken **right now**, and this README is already
built around that:

### `github-readme-stats.vercel.app` is offline

The canonical instance returns `503 DEPLOYMENT_PAUSED`. It is not rate-limiting — the
deployment itself is paused. Every profile on GitHub using the default URL currently
shows a broken stats card.

This README therefore points at a working community mirror:

```
https://github-readme-stats-sigma-five.vercel.app
```

**If that mirror also dies**, you have two options.

*Quick fix* — swap in the other verified mirror. One find-and-replace in `README.md`:

| Replace | With |
| --- | --- |
| `github-readme-stats-sigma-five.vercel.app` | `github-readme-stats-eight-theta.vercel.app` |

*Permanent fix — recommended* — run your own instance. It takes about five minutes and
it can never be paused by someone else:

1. Fork <https://github.com/anuraghazra/github-readme-stats>
2. Create a GitHub personal access token with **no scopes at all**
   (<https://github.com/settings/tokens> → Generate new token (classic) → tick nothing).
   The stats API only reads public data; an unscoped token just raises your rate limit.
3. Import the fork at <https://vercel.com/new>, and add an environment variable
   `PAT_1` set to that token.
4. Deploy. You get a URL like `https://grs-namans12.vercel.app`.
5. Find-and-replace `github-readme-stats-sigma-five.vercel.app` with your own host.

Self-hosting fixes the stats card, the top-languages card, **and** the pinned repo
cards in one move, since all three come from the same service.

### `github-profile-trophy.vercel.app` is offline

Returns `402 Payment Required` — the maintainer's Vercel account has exceeded its
billing limit, so it is down for everyone, including the maintainer's own username.

The trophy block is therefore **commented out** in the README, with
`github-profile-summary-cards` used in its place. That service is live, and frankly
suits the theme better than trophy icons do.

To bring trophies back if the service returns, or to self-host it: see
`CUSTOMIZE.md#trophies`.

### Everything else

These were all verified working when the README was written:

| Service | Used for |
| --- | --- |
| `capsule-render.vercel.app` | header + footer waves |
| `readme-typing-svg.demolab.com` | animated typing headline |
| `streak-stats.demolab.com` | contribution streak |
| `github-readme-activity-graph.vercel.app` | activity graph |
| `github-profile-summary-cards.vercel.app` | language + commit-time cards |
| `skillicons.dev` | tech stack icons |
| `img.shields.io` | badges |
| `komarev.com/ghpvc` | visitor counter |
| `user-images.githubusercontent.com` | animated GIFs |

---

## Troubleshooting

**The README doesn't show on my profile at all.**
The repo name must match your username exactly and be public. `Namans12` ≠ `namans12`
for the *repo name* check even though URLs are case-insensitive — recreate it if the
"secret repository" banner never appeared.

**Images show as broken only for me.**
Corporate networks and some ad blockers block `*.vercel.app` and
`user-images.githubusercontent.com`. Check on mobile data before assuming it's broken.

**The stats card says "Maximum retries exceeded".**
Rate limiting on a shared instance. Self-host (above) — it's the only real fix.

**The snake is stale.**
Scheduled workflows are disabled automatically after 60 days of repository inactivity.
Push any commit, or hit **Run workflow** manually, to wake it up.

**GIFs don't animate in the GitHub mobile app.**
Known app limitation. They animate fine on the web on every platform.
