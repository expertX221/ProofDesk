# Judge testing instructions

Public demo: https://proofdesk-blond.vercel.app

Public source: https://github.com/expertX221/ProofDesk

Track: Best Apps and Agents.

## Test the application

1. Open the public demo in a desktop browser. No account or payment is required by the application.
2. Enter `https://github.com/expertX221/ProofDesk` as the public repository.
3. Use the prefilled requirements, or paste your own.
4. Click **Review submission** and wait for the live assessment.
5. Inspect statuses, source evidence, and suggested actions. Expand the description and video-outline drafts, then export JSON.

**Explore a sample report** is a separately labeled fixture and does not call the model. Use **Review submission** to test NVIDIA Nemotron on Nebius Token Factory.

The interface never requires the judge's Nebius key. The deployment owner's server environment holds its inference credential.

## Limits

This is a bounded static evidence review, not execution of the submitted repository. A verified text finding does not prove the reviewed application runs. Links to demos and videos need separate verification. GitHub anonymous API limits and inference availability can affect live testing. Draft descriptions must be reviewed before use.

## Availability

Public access and one live inference request were verified on October 30, 2026. The owner must keep Vercel hosting and Nebius inference access funded and enabled until December 23, 2026 at noon Pacific Time (December 24 at 1:30 AM IST). Future uptime is not established by the October 30 test. There is no automatic expiry implemented in the app.
