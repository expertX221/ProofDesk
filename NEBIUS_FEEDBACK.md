# Nebius and NVIDIA feedback

## What we actually tested

On October 30, 2026, ProofDesk's public Python web app on Vercel completed a live review of `https://github.com/expertX221/ProofDesk`. The application gathered repository evidence through GitHub, then made a runtime chat-completions request to NVIDIA Nemotron through Nebius Token Factory. This was real inference, not the sample fixture or mocked test.

- Model: `nvidia/Nemotron-3-Ultra-550b-a55b`
- Endpoint configured in source: `https://api.tokenfactory.us-central1.nebius.com/v1`
- Model-request elapsed time measured by the app: **5.9 seconds**
- Full request elapsed time measured by the verification script: **8.2 seconds**
- Prompt tokens reported by the API: **7,975**
- Completion tokens: **1,892**, including **1,034 reasoning tokens**
- Total tokens: **9,867**
- Result: four requirement checks returned and accepted by the report validator.

These are observations from one successful request, not latency benchmarks or a quality evaluation dataset. End-to-end time includes repository retrieval and HTTP overhead. No comparison against other models was performed.

## What worked

Token Factory's OpenAI-compatible chat-completions interface let us keep the backend in Python's standard library, with no inference SDK dependency. Nemotron produced structured JSON that the application parsed into requirement statuses, explanations, evidence references, a description draft, and a demo outline. Model provenance and usage were returned alongside the report, making it possible to expose concrete runtime evidence rather than a generic AI claim.

Token Factory accelerated integration by providing managed inference: this project did not provision GPUs, download weights, or build a model-serving stack. The front end was hosted on Vercel; we did not use Nebius AI Cloud compute, Serverless Jobs, Serverless Endpoints, NemoClaw, or other NVIDIA runtimes and do not claim experience with them.

## Improvements we would value

1. A project-oriented structured-output example with strict JSON schema validation, malformed-output recovery, and evidence citation constraints would reduce integration work for review agents.
2. A clear account/region/model availability check before the first inference call would help builders choose the correct model identifier and regional endpoint.
3. A complete end-to-end tracing example separating source retrieval, model latency, reasoning tokens, and user-visible latency would make cost and responsiveness tuning easier.

These are product suggestions based on building this integration, not claims of observed service defects. We have not yet measured sustained throughput, concurrency, long-term reliability, or Nano/Super/Ultra routing tradeoffs.
