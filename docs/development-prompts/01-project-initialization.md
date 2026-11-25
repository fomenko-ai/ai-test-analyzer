# Project initialization: AI Test Analyzer

Act as a Senior Python Software Architect and Technical Lead.

The repository contains approved requirements, architecture documentation, architectural decision records, configuration examples, and implementation guidelines for the `ai-test-analyzer` project.

## Your first task

Perform a comprehensive review of the existing project documentation.

Read:

- `AGENTS.md`
- `README.md`
- All architecture and requirements documents in `docs/`
- All configuration and contract examples in `examples/`
- Investigation skills in `skills/`

## Objectives

1. Understand the project requirements and architecture.
2. Identify contradictions, missing requirements, and technical risks.
3. Verify proposed dependency versions and compatibility with Python 3.14, distinguishing published metadata from actual installation results.
4. Review Docker image versions and compatibility.
5. Identify external integrations requiring technical validation.
6. Prepare a detailed plan for Phase 0 — Technical Spike.
7. Define acceptance criteria for each technical investigation.

## Constraints

- Use Python 3.14 and the latest stable compatible dependencies.
- Follow the approved Ports and Adapters architecture and KISS, DRY, SOLID, and YAGNI principles.
- Keep all source code, documentation, comments, prompts, and configuration descriptions in English.
- Do not introduce unnecessary dependencies or change approved architectural decisions without approval.
- Do not invent corporate infrastructure details, dependency versions, or successful verification results.
- Do not expose credentials or confidential information.
- Do not create or modify real Jira issues or Confluence pages.
- If requirements are ambiguous or contradictory, stop and ask specific questions. Do not repeat questions already answered in the documentation.
- Do not implement the application or execute the spike until its plan is approved.

## Deliverables

Create `docs/technical-spike-plan.md` containing:

- Documentation review results.
- Identified technical risks and unresolved questions.
- Dependency and Docker compatibility verification plan.
- External integration verification plan.
- Acceptance criteria and required evidence for each check.
- Required access, prerequisites, and any blockers.

Clearly distinguish verified facts, assumptions, and checks still pending.

Stop after completing the documentation review and Technical Spike plan. Present the results for review and wait for approval before proceeding.
