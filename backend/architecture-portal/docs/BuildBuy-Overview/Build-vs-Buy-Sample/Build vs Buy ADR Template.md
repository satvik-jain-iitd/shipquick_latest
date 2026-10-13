# ADR Template

This ADR template can be used to capture architecture decisions related to Initiative/Platform/Enterprise design choices, Buy vs Build (BvB) recommendations, or Prescriptive ADRs. Indicate the ADR Type from the choices below.

| Choose One [X] | ADR Type | Description |
| ----- | ----- | ----- |
| | **architecture** | Describes a solution that a team proposes about the architecture of an Initiative/Platform, or to be applied across the Enterprise. This can also set a precedent in that future problems having the same patterns might be able to leverage the same solutions. |
| | **buyvsbuild** | Describes a choice that a team proposes on the implementation of a building block (i.e. Buy, Build, Reuse) |
| | **prescriptive** | Describes various prescriptions that a team proposes based on certain patterns. In most cases, prescriptions are expressed in the form of a decision tree. |

For the Architecture Decision Name above, provide a clear and concise title for the decision (e.g. Use of REST API for Inter-Service Communication).

## ADR Status History

| Authors | Status (Proposed/Accepted/Declined/Deprecated) | Date | Deciders |
| ----- | ----- | ----- | ----- |
| [Staff Engineers/Architects, Solutions Architects, etc] | Proposed | ... | N/A |
| [Staff Engineers/Architects, Solutions Architects, etc] | Accepted | ... | [Head Engineers, Principal Architects, Executives, Enterprise ARB, etc] |
| ... | ... | ... | ... |

## Context & Problem Statement

Describe the context in which the decision is being made. Include relevant background information, the problem that needs to be solved, and any constraints or requirements that are pertinent to the decision.

e.g. The current system uses a mix of different communication protocols between services, leading to increased complexity and maintenance overhead. A standardized approach is needed to streamline development and improve system coherence.

## Decision Drivers

List of key factors/criteria in which the options were evaluated that influenced the decision.

e.g.
- Fit for Purpose
- Speed to Market
- Reusability
- Configurability
- Risk
- Regulatory

## Options Considered

Outline the options that were considered before making the decision. For each option, provide an explanation with pros/cons.

e.g.
- Option 1 gRPC: Offers high performance and strong typing, but adds complexity and requires additional skills from the development team
- Option 2 Message Queues: Suitable for asynchronous communication but adds latency and complexity in message handling

## Decision

Clearly state the decision that has been made. This section should be concise but comprehensive enough to convey the essence of the decision. Explain the rationale behind the decision. This should include the criteria used to evaluate the options and why the chosen solution was considered the best fit.

e.g. We will adopt REST API as the standard protocol for inter-service communication in all new developments. REST API was chosen due to its simplicity, wide adoption, and extensive support in our current technology stack. It also aligns with our goal of improving developer experience and system coherence.

### Prescription

In the case of Prescriptive ADRs, provide a table or decision tree to document the prescriptions based on use cases.

e.g.
| Use Case | Prescription |
| ----- | ----- |
| Within Payment Network, if the API is in the payment flow | Use Core Switch |
| Within Payment Network, if the API is receiving, sending, or otherwise processing Cardholder data and is in scope of PCI | Use Core Switch |

### Consequences

Explain the consequences of the decision, both positive and negative. This includes immediate impacts and long-term effects on the system.

e.g.

**Positive Consequences**
- Simplified inter-service communication
- Improved documentation and developer experience
- Better support for monitoring and logging

**Negative Consequences**
- Initial effort required to refactor existing services
- Potential performance overhead with REST compared to other protocols

## Related Decisions

List any related decisions that are connected to this one. This could include previous decisions that influenced this one, or future decisions that will be impacted by it.

e.g.
- <a href="https://github.example.com/platform-team/ea-design-playbook/blob/main/architecturedecisionrecord/template.md">Authentication and Authorization for REST APIs</a>
- <a href="https://github.example.com/platform-team/ea-design-playbook/blob/main/architecturedecisionrecord/template.md">Versioning Strategy for REST APIs</a>

## References

Include any references to documents, links, or other resources that were used to inform/support the decision.

e.g.
- <a href="https://github.example.com/platform-team/ea-design-playbook/blob/main/architecturedecisionrecord/template.md">RESTful Web Services Cookbook by Subbu Allamaraju</a>
- <a href="https://github.example.com/platform-team/ea-design-playbook/blob/main/architecturedecisionrecord/template.md">Appendix A: Comparison of Communication Protocols</a>
