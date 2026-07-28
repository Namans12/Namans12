# Customize

Every section of `README.md` is wrapped in a marker pair:

```html
<!-- ══════════════════ MODULE: STATS ══════════════════ ... -->
        ...content...
<!-- ══════════════════ END MODULE: STATS ══════════════════ -->
```

**To remove a section**, delete everything from its opening marker to its matching
`END MODULE` line. The modules don't reference each other, so nothing else breaks.

**To reorder sections**, cut and paste whole marker-to-marker blocks. The divider GIFs
sit *between* modules, so move those separately if the spacing looks off.

---

## The palette

Every colour in the README comes from this set. If you restyle, change these
consistently or the page stops looking designed.

| Role | Hex | Used for |
| --- | --- | --- |
| Base | `0D1117` | GitHub's dark canvas — matches so cards look inset |
| Panel | `161B22` | badge label backgrounds |
| Border | `30363D` | card borders |
| Violet | `7C3AED` | primary accent, gradient start |
| Cyan | `22D3EE` | headline text, links, gradient middle |
| Teal | `2DD4BF` | gradient end, tertiary accent |
| Text | `E6EDF3` | headings on coloured backgrounds |
| Muted | `8B949E` | card body text |

Cards use `bg_color=00000000` (fully transparent) so a single image reads correctly on
both GitHub light and dark. If you set a solid background on one card, set it on all of
them — a single opaque card in a transparent row is the most obvious way to make this
look homemade.

---

## Modules

### hero
The waving gradient banner. Change the name via `text=`, the subtitle via `desc=`.
URL-encode them: space is `%20`, `·` is `%C2%B7`.
Other `type=` values: `wave`, `slice`, `egg`, `rect`, `soft`, `cylinder`.

> **Never put a plain `&` in `text=` or `desc=`.** capsule-render drops your text into
> the SVG without escaping it, and a bare `&` makes the file invalid XML. Browsers
> refuse to render invalid SVG, so the *entire banner* silently vanishes — while the URL
> still returns `200 OK`, which is why this is so easy to ship by accident.
>
> Encode it as `%26amp%3B` instead. That reaches the SVG as `&amp;`, which is valid and
> still displays as `&`. The current subtitle uses exactly this.
>
> `verify-links.ps1` now XML-parses every SVG response specifically to catch this.

### typing
A terminal window: a static session log, then one live animated prompt.

**The window frame is a one-cell `<table>`.** Not a stylistic quirk — CSS is stripped
from READMEs, so there is no way to draw a border, rounded corner or panel. Table cells
are the only element GitHub gives a visible border, which makes a one-cell table the
only route to a box.

**`multiline=true` is the important parameter.** It makes lines accumulate, so the
session builds up one line at a time and then loops. Without it, `readme-typing-svg`
types a line, erases it, and types the next — you only ever see one line at once, which
is not what a terminal looks like.

**Alignment uses no-break spaces (`%C2%A0`), not ordinary spaces.** This is the part
that will bite you if you edit the lines:

> SVG collapses any run of plain spaces down to one. Measured in a browser with
> `getComputedTextLength()`: `"$ role -> X"` and `"$ role&nbsp;&nbsp;&nbsp;-> X"` (three
> plain spaces) both render at **96.8px** — identical. Adding `xml:space="preserve"`
> did not help either. The same string with three **no-break** spaces measures
> **114.4px**, so it survives.
>
> Press Start 2P does include U+00A0, so this is safe — confirmed by reading the font's
> cmap directly (656 glyphs mapped).

So the padding that lines up the `->` column is `%C2%A0`, and plain `+` spaces are only
used between words. Change a keyword's length and you must adjust its padding to match.

**On the arrows:** an earlier version of this file claimed Press Start 2P had no arrow
glyph. That was wrong — U+2192 (`→`) *is* present. The lines use ASCII `->` because
that's the style chosen, not because of a font limitation. If you prefer the real arrow,
`%E2%86%92` works.

**The font** is [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P), via
`font=Press+Start+2P`. `readme-typing-svg` pulls any Google Font and embeds it in the
SVG, so it renders for everyone with no local install.

`center=true` is deliberately omitted — centring each line inside the box would break
the left-hand `$` column that makes it read as a terminal.

**Sizing the window.** `readme-typing-svg` does *not* shrink to fit: whatever `height=`
you give it becomes the canvas, and any leftover is empty space inside your box. The
first version used `height=190` for content that ended at 89px — 101px of dead air,
which is why the window looked oversized.

Line baselines sit at a fixed **17px** pitch (`17, 34, 51, 68, 85` for five lines) and
that pitch comes from the font size, *not* from `height` — so shrinking the canvas does
not squash the lines. To size it correctly:

```
height = 17 × (number of lines) + ~11
width  = 12 × (longest line in characters) + ~24
```

Press Start 2P is monospace with a 1em advance, so at `size=12` each character is
exactly 12px wide. Current values: 5 lines and a 44-character longest line give
`height=96`, `width=552`.

Add or reword a line and you must recompute both, or you'll get dead space again — or
clipping, which is worse.

> **Use ASCII `->`, never a real arrow.** Press Start 2P is an 8-bit font with no `→`
> glyph. A missing glyph doesn't fall back to another font here — it renders as an empty
> box in the middle of your headline. The same caution applies to `·`, `—` and any other
> typographic character.

Lines live in `lines=`, separated by `;` and URL-encoded: space `+`, `&` `%26`, comma
`%2C`, `@` `%40`, `>` `%3E`. Add or remove them freely. `duration=` is ms per line,
`pause=` is ms between.

Pixel fonts are wide — roughly one full em per character. At `size=13` the longest line
here is about 440px, which is why `width=560`. Lengthen a line and you must widen the
SVG too, or it clips.

### social
Two rows: animated icons, then pixel-art terminal chips.

**Row 1 — the X mark is generated, not sourced.** The
[Cool-GIFs](https://github.com/Anmol-Baranwal/Cool-GIFs-For-GitHub) set predates the
rebrand and carries only the old Twitter bird; there is no animated X in it. Public
animated X logos do exist (LottieFiles has a free one), but hotlinking a third-party
asset is a dependency that can vanish or change without warning — the same class of
problem that took out the trophy and stats cards.

So `assets/x-logo.gif` is built locally by `assets/make-x-logo.py`, and it animates: a
cyan sheen sweeps diagonally across the mark, matching the palette. LinkedIn and Discord
stay as Cool-GIFs animations.

The geometry is the **official mark**, not an approximation. `assets/x.svg` is the
simple-icons path, and it happens to use only straight-line commands (`M L H V Z`), so
the script parses and fills it exactly — outer glyph first, then the inner counter cut
back out. Regenerate with:

```bash
cd assets && python make-x-logo.py
```

> Two GIF traps that bit during this build, worth knowing if you edit the animation:
> **PIL silently drops any frame identical to the one before it.** A 30-frame sweep
> collapsed to 9 because the highlight spent much of its travel off the glyph. The fix
> is to bound the sweep to the mark's own bounding box so every frame differs.
> And a static tail can't be used for the pause between loops — those frames are
> duplicates too, so they vanish. Put the pause on the *last frame's duration* instead.

**Row 2 — shields badges**, with two fixes worth remembering:

- **Gmail's mark is forced white** with `logoColor=white`. Left alone, shields renders
  it in Gmail's brand red, which fights the palette.
- **CodePen has no shields logo at all.** The slug returns a badge with an empty icon
  slot rather than an error, so it's easy to miss. The icon is instead passed inline as
  a base64-encoded SVG:

  ```
  &logo=data:image/svg%2Bxml;base64,<base64 of the svg>
  ```

  That's why the CodePen badge URL is enormous — the whole icon is embedded in it. The
  source SVG came from simple-icons via
  `https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/codepen.svg`, with
  `fill="white"` added before encoding. The same trick works for any brand shields has
  dropped.

The Discord badge is deliberately **not a link**. Discord usernames aren't
URL-addressable — only numeric IDs are — so `discord.com/users/Naman1201` goes nowhere
useful. The username is shown as the badge text instead.

### open-to
Three call-to-action badges. Edit the text between `/badge/` and the colour to change
what you're advertising. Currently: Agentic AI & LLM work, data platform builds, open
source. Delete the whole module if you're not looking for anything.

<a id="intro-video"></a>
### intro-video
`assets/naman-intro.gif` — 520×293, 64 colours, 5.5 MB. It autoplays and loops the
moment the profile loads, and links to `assets/naman-intro.mp4` for the original with
sound.

**Do not lower the framerate to save space.** The first build ran at 10fps and looked
laggy, and the cause was subtler than the low number: the source is 24fps, and 24 ÷ 10
= 2.4, so the encoder had to drop *two* frames then *three*, alternating. Even timing,
uneven motion — the eye reads that as stutter.

The fix is to keep every source frame. GIF delays are whole centiseconds and 100 ÷ 24 =
4.167, which doesn't divide cleanly, so ffmpeg would otherwise alternate 4cs and 5cs
delays. Retiming the clip by ×0.96 first maps all 240 frames onto an exact 25fps grid —
one uniform 4cs delay, nothing dropped, nothing duplicated. The clip ends up 9.6s
instead of 10s, which nobody will notice.

Width came down from 640 to 520 to pay for the extra frames. Frame count and palette
size drive GIF weight far more than dimensions do, and smoothness is worth more than
120 pixels on a hero element.

**Why a GIF and not a video player.** GitHub's sanitizer deletes `<video>` outright —
not just its attributes, the whole element. Verified against GitHub's own renderer:

| Submitted | Returned |
| --- | --- |
| `<video src poster controls>` | *(nothing)* |
| `<video><source src type></video>` | `<source type="video/mp4">` — `src` stripped too |
| `<video autoplay loop muted>` | *(nothing)* |
| `<a href="…mp4"><img src="…gif"></a>` | **kept intact** |

A GIF is the only format that both animates inline *and* is officially supported.

**Why not WebP.** Animated WebP encoded the same clip at **0.96 MB versus 4.1 MB** —
four times smaller at higher resolution and framerate. It was rejected anyway:
[GitHub's own docs](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files)
list the supported formats as PNG, GIF, JPEG, SVG and `.mp4`/`.mov`/`.webm`. WebP is
absent. An unlisted format that happens to work today is exactly the kind of thing that
silently breaks later, and camo caches the breakage.

**The alternative: a real player.** Drag the `.mp4` into any GitHub issue comment box —
don't submit the comment. GitHub uploads it and hands back a
`https://github.com/user-attachments/assets/<uuid>` URL. Put that on **its own line**
in the README and GitHub renders a genuine player with controls and sound. The same
docs confirm `.mp4` is supported up to 10 MB on a free plan; this clip is 2.5 MB.

Trade-off: a player shows a static first frame until clicked, so the profile loses its
motion-on-load. The GIF was chosen because a profile README is skimmed in seconds —
something already moving beats something waiting to be clicked.

**Regenerating the GIF.** Two-pass palette encode; `fps` and `max_colors` dominate the
file size far more than width, and cropping barely helps:

```bash
ffmpeg -i assets/naman-intro.mp4 -vf "setpts=PTS*0.96,fps=25,scale=520:-1:flags=lanczos,palettegen=max_colors=64:stats_mode=diff" palette.png
ffmpeg -i assets/naman-intro.mp4 -i palette.png -lavfi "setpts=PTS*0.96,fps=25,scale=520:-1:flags=lanczos[v];[v][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" assets/naman-intro.gif
```

Verify a rebuild kept its cadence — one distinct delay value is what you want:

```bash
ffprobe -v error -select_streams v:0 -show_entries frame=duration_time -of csv=p=0 assets/naman-intro.gif | sort -u
```

Dropping to 48 colours saves ~1 MB but visibly speckles the desk and laptop.
`bayer_scale` maxes out at 5 — higher values error out rather than compressing further.
Cropping dead space barely helps; frame count and palette size are what matter.

The source artwork lives outside the repo at `../intro-source.png` so the 1.6 MB
original isn't committed alongside the render.

The `<img>` uses an absolute `raw.githubusercontent.com` URL rather than a relative
path, because a profile README renders at `github.com/Namans12`, not inside the repo.

### about
Two-column table — prose left, GIF right. The `width="62%"` / `width="38%"` split is
what keeps the text from crushing on narrow screens; adjust both together.
Swap the GIF for any other from the Cool-GIFs *Work Culture* section.

### whoami
A fenced Python block. **This is the only visual module with zero external
dependencies** — if every service on earth goes down, this still renders. Worth keeping
for that reason alone.

### stack
Grouped rows, one technology cluster per table row.

Icons come from [skillicons.dev](https://skillicons.dev). Use the **canonical** names
from `https://skillicons.dev/api/icons`, not the short aliases — `python` not `py`,
`typescript` not `ts`, `tailwindcss` not `tailwind`. An unrecognised name renders a
blank tile rather than erroring, so it's easy to miss.

skillicons has no icon for Databricks, Spark, Delta Lake, Azure Data Factory, Fabric or
Neo4j, so those use `shields.io` badges. That mix is intentional.

> **Watch out:** shields.io no longer serves several brand logos — `linkedin`,
> `microsoft`, `microsoftazure`, `windows`, `openai` and `codepen` all silently render
> *without* an icon. The badges using those brands are therefore text-only by design.
> Before adding `&logo=something`, confirm it actually renders — compare the response
> size against a badge with no logo at all.

### projects
Live repo cards. To swap a project, change `repo=` in that card's URL. To change how
many, add or remove `<a>` blocks — they're `width="49%"` so they pair two per row.

The `<details>` block underneath holds the long-form write-up for the two flagships.
Add more entries there rather than lengthening the card grid; the cards are for
scanning, the accordion is for people who stopped to read.

> These point at `github-readme-stats-sigma-five.vercel.app`, a community mirror,
> because the official instance is down. See [SETUP.md](SETUP.md) for why and how to
> self-host.

### credentials
Static badges — certifications left, recognition right. Never breaks, no services
involved. Add a row by copying an `<img>` line and the `<br/>` after it.

### stats
Stats card, top languages, streak, activity graph.

The four `github-profile-summary-cards` panels that used to follow were removed —
they reported different commit counts than the stats card sitting right above them,
duplicated the language breakdown, and rate-limited into a red `ERROR!!!` panel. The
commented block in the README explains it and shows how to restore the one card
(productive-time) that added anything.

> **When a card shows an error that won't go away**
>
> GitHub does not hotlink your images — it proxies every one through
> `camo.githubusercontent.com` and **caches the result**. If a service was rate-limited
> at the moment camo fetched it, camo caches the *error image*, and your profile keeps
> showing "Failed to retrieve contributions" or "Cards are temporarily rate limited"
> long after the service is healthy again.
>
> Reloading won't help, and neither will waiting, because camo isn't re-fetching.
> **Change the URL.** Any difference produces a new camo URL and forces a fresh fetch —
> add or tweak a harmless parameter like `&card_width=495`. That is exactly why the
> streak card carries one.
>
> To check whether the service itself is actually broken, request the URL directly
> rather than looking at your profile — `.\verify-links.ps1` does this and bypasses
> camo entirely.

> **The streak card is the weakest link, and it is worth knowing why.** Measured
> directly, `streak-stats.demolab.com` takes **15–20 seconds** to answer when it answers
> at all — two of three consecutive requests timed out at 30s. Camo gives up well before
> that, caches the failure, and the card sits broken on your profile until the URL
> changes.
>
> Nothing in this README can fix that; it is a free shared instance under load. The only
> real remedies are to **self-host it** (fork
> [DenverCoder1/github-readme-streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats),
> deploy to Vercel with a PAT — same procedure as the stats card in
> [SETUP.md](SETUP.md)), or to **delete the card**. If it breaks repeatedly and you
> don't want to self-host, deleting it is a legitimate choice rather than a defeat.

<a id="trophies"></a>
**Trophies** are commented out. `github-profile-trophy.vercel.app` returns
`402 Payment Required` — the maintainer's hosting is over its billing limit, so it's
down for every user, not just you. To bring them back, either uncomment the block once
the service recovers, or fork
[ryo-ma/github-profile-trophy](https://github.com/ryo-ma/github-profile-trophy), deploy
it to Vercel, and point the URL at your own instance.

### snake
Needs the GitHub Action to have run once — see [SETUP.md](SETUP.md) step 3. Until then
both URLs 404 and you'll see a broken image.

Colours are set in `.github/workflows/snake.yml`, not here. `color_dots` takes five
values, lightest (no contributions) to darkest (most).

### currently
Plain table. Keep the four rows short — this section works because it's scannable.

### dev-setup
**These were inferred from your environment and stack, not confirmed.** Edit
`skillicons.dev/icons?i=...` to list what you genuinely use day to day. Currently:
VS Code, Windows, PowerShell, Git, Docker, Postman, Notion, Figma.

### easter-egg
A `<details>` that most visitors never open. Keep it genuine — the whole point is that
it rewards someone who bothered. If you change it, don't turn it into another pitch.

### footer
Mirror of the hero gradient, reversed. If you change the hero colours, reverse the same
values here or the page loses its bookend.

---

## Disabled modules

These are written but commented out, because each needs setup and a half-configured
card looks worse than no card.

<a id="wakatime"></a>
### WakaTime
Coding time by language. Sign up at [wakatime.com](https://wakatime.com), install the
plugin for your editor, then **Settings → make coding activity public**. Replace
`YOUR_WAKATIME_USER` and uncomment.

<a id="spotify"></a>
### Spotify now-playing
Deploy [novatorem](https://github.com/novatorem/novatorem) to Vercel and connect a
Spotify app. Replace `YOUR-NOVATOREM-DEPLOY` and `YOUR_SPOTIFY_ID`, then uncomment.
Worth knowing: it shows what you're listening to, on a page recruiters read.

<a id="blog"></a>
### Blog post feed
Add [gautamkrishnar/blog-post-workflow](https://github.com/gautamkrishnar/blog-post-workflow)
as a second Action pointing at your RSS feed. It rewrites whatever sits between these
two markers, on a schedule. Paste them into the README where you want the list:

```html
<!-- BLOG-POST-LIST:START -->
<!-- BLOG-POST-LIST:END -->
```

> They live here rather than in the README's disabled-modules block for a concrete
> reason: **HTML comments do not nest.** A comment ends at the *first* `-->` it meets,
> so putting these markers inside another commented block terminates it early and dumps
> the rest of the block onto the page as visible text. If you ever comment out a section
> that already contains a comment, delete the inner one first.

---

## What GitHub will silently delete

GitHub sanitizes README HTML. These never work, no matter how they're written:

- `<script>` — stripped entirely
- `<style>` blocks and `style="..."` attributes — stripped, so no CSS animation
- `class=` and `id=` on most elements
- `onerror`, `onclick`, any event handler
- iframes, forms, embeds

Which means **all motion has to come from an animated GIF, an animated SVG served by a
third party, or an Action that regenerates a committed file.** There is no fourth
option. If you find a profile doing something that looks impossible, it's one of those
three.

Layout is limited to `<div align>`, `<table>`, `<picture>`, `<details>`, `<img>` with
`width`/`height`, and `&nbsp;` for spacing.

---

## After any edit

```powershell
.\verify-links.ps1
```

It strips commented-out blocks, checks every remaining URL, and tolerates sites that
refuse bots (LinkedIn answers automated requests with `999`, CodePen with `403` — both
are fine in a browser). Anything it reports as broken genuinely is.
