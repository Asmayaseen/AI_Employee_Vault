# ADR-002: Tiered Progressive Enhancement Strategy

- **Status:** Accepted
- **Date:** 2026-02-05
- **Feature:** All tiers (001-bronze through platinum)
- **Context:** Building an autonomous AI system that handles banking, email, and social media involves high risk. Delivering everything at once increases the chance of catastrophic failures. Need an incremental strategy that reduces risk, enables early validation, and provides natural stopping points.

## Decision

Implement a four-tier progressive enhancement strategy where each tier is independently useful and must be fully functional before proceeding to the next:

- **Bronze (Foundation)**: Obsidian vault + 1 watcher (filesystem) + Claude Code integration + basic skills
- **Silver (Functional)**: Multiple watchers (Gmail, WhatsApp, LinkedIn) + orchestrator + HITL approval workflow + scheduling
- **Gold (Autonomous)**: Cross-domain MCP servers (Odoo, social media) + enterprise error recovery + CEO briefing + comprehensive audit logging
- **Platinum (Production)**: 24/7 cloud deployment + work-zone specialization + vault sync + health monitoring dashboard

Tier gates enforce quality:
- Cannot proceed until current tier is fully functional and documented
- Each tier must include demo capability
- Each tier must pass security review (credential handling, HITL verification)
- Each tier must implement all functionality as Agent Skills

## Consequences

### Positive

- Reduced risk - each tier validated independently before adding complexity
- Natural demo points - each tier is a working product
- Early user feedback - Bronze tier is usable within days
- Clear milestones - progress is measurable and visible
- Each tier independently useful - user can stop at any tier and have a working system
- Security review at each gate catches issues early

### Negative

- Cannot skip tiers even if later features are higher priority
- Some rework between tiers as architecture evolves
- Slower initial progress compared to building everything in parallel
- Tier gates can create artificial blockers if gate criteria are too strict

## Alternatives Considered

- **Big bang delivery**: Rejected as too risky for a system handling banking and personal communications. A single failure in the full system could be catastrophic with no fallback.
- **Feature-by-feature (no tiers)**: Rejected because it lacks structural milestone gates. Without tiers, there's no natural validation checkpoint to ensure the foundation is solid before adding autonomous capabilities.
- **Microservices from day 1**: Rejected as premature complexity. For a single-user system, the operational overhead of managing independent services from the start adds unnecessary infrastructure cost.

## References

- Feature Spec: `/specs/001-bronze-tier/spec.md`, `/specs/002-silver-tier/spec.md`, `/specs/003-gold-tier/spec.md`
- Constitution: `.specify/memory/constitution.md` (Principle VII: Tier-Based Progressive Enhancement)
