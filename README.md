# ProofDesk

An evidence-based hackathon submission reviewer, built as a Python web application. Runs with **Python 3.10+ and no pip dependencies**.

## Run

Open a terminal in this folder:

```powershell
python app.py
```

Visit http://127.0.0.1:8000 in your browser. Click **Explore a sample report** for an illustrative report without an API key. A Python interpreter runs the backend; the interface opens in a browser. In an IDE, run `app.py` and keep it running.

## Enable real NVIDIA inference on Nebius

Create a Nebius Token Factory API key in your own account. Keep it out of source code and Git. In PowerShell, enter it privately without saving it in shell history:

```powershell
$proofdeskKey = Read-Host 'Nebius API key' -AsSecureString
$env:NEBIUS_API_KEY = [System.Net.NetworkCredential]::new('', $proofdeskKey).Password
python app.py
```

macOS/Linux: set `NEBIUS_API_KEY` in your environment before launching `python3 app.py`. No .env loader is needed or included.

Default model: `nvidia/Nemotron-3-Ultra-550b-a55b`.
Default endpoint: `https://api.tokenfactory.us-central1.nebius.com/v1`.
Override `NEBIUS_MODEL` and `NEBIUS_BASE_URL` to match a supported NVIDIA model and its Nebius region. Model availability and access depend on your account.

Official integration reference: https://github.com/nebius/token-factory-cookbook/blob/main/models/nemotron/nemotron3-ultra-550b-a55b.md

## Use

1. Paste a public GitHub repository URL (repository root, not a file URL).
2. Edit the prefilled competition requirements.
3. Optionally add demo/video URLs and project context.
4. Click **Review submission**. This fetches selected public files and sends them to NVIDIA Nemotron on Nebius Token Factory.
5. Inspect evidence, prioritize unresolved checks, and export JSON.

Reports include submission description and demo-outline drafts. Review them before use. Sample mode never calls Nebius and does not qualify as a runtime integration demonstration.

## Architecture and limits

Browser → Python HTTP server → public GitHub REST API → NVIDIA Nemotron via Nebius → validated JSON report → browser.

The app reads up to ten eligible small files, prioritizing README and license, bounded to approximately 55,000 characters. It reports scan coverage and GitHub tree truncation. Large repositories may need a targeted follow-up. GitHub's anonymous API rate limit applies. It does not clone, execute, or modify repository code. It does not test the demo or determine video duration/public visibility. A “verified” result indicates support in inspected text, not proof of successful execution or formal compliance. Model assessments may be incorrect.

Evidence and notes are treated as untrusted content in the model instruction. References are checked against fetched evidence IDs; unsupported verified results are downgraded. This reduces errors but does not eliminate prompt injection or model mistakes. Browser output uses text nodes rather than untrusted HTML.

The key remains in the server environment. Reports are held in browser memory; downloaded reports include scanned excerpts. Public files and supplied context are sent to Nebius during live reviews. Default binding is localhost. The optional Google Fonts stylesheet is cosmetic and has system-font fallbacks.

## Deploy as a website

### Vercel

The repository includes `api/index.py` and `vercel.json`. It uses Vercel's Python Functions runtime and retains the dependency-free local launch.

1. In Vercel, import `expertX221/ProofDesk` from GitHub.
2. Choose **Other** as the framework preset and the repository root as the Root Directory. Leave Build Command and Output Directory unset.
3. In the project's Environment Variables, add a **new, unexposed** `NEBIUS_API_KEY` for Production. Never commit `.env` to GitHub. If a key was previously committed, revoke it in Nebius and generate a replacement.
4. Deploy the latest `main` commit. If adding secrets after deploying, redeploy to apply them.
5. Open the deployment URL, test the sample, then complete a live repository review.
6. Confirm judges can open the production URL without your Vercel account; if access protection is enabled, provide the required judge access instructions.

The app requests a 300-second function duration. A deployment and real inference request must still be tested on the target account. Keep hosting and Nebius access active through judging. No public deployment has been verified by these instructions.

Official runtime reference: https://vercel.com/docs/functions/runtimes/python

### Container hosting

A Dockerfile is included. On a Python/container hosting service, configure `NEBIUS_API_KEY` as a secret and run:

```text
python app.py --host 0.0.0.0
```

`PORT` is supported. For Docker:

```text
docker build -t proofdesk .
docker run --rm -p 8000:8000 --env NEBIUS_API_KEY proofdesk
```

This first version has no authentication or per-user usage quotas. Keep a hosted instance private until you add access control and request limits to protect paid inference usage. The POST endpoint rejects browser cross-origin requests; this is not authentication.

## Hackathon handoff

Track: Best Apps and Agents. Add a real live review recording, a hosted/test-build URL, a public repository with this MIT LICENSE, and a public YouTube demo under three minutes. Record actual Nebius/NVIDIA feedback after using the service. Do not represent sample output as live inference. Publishing, live inference verification, and submission are still required.

## Tests

```text
python -m unittest discover -s tests -v
```

MIT licensed. See LICENSE.
