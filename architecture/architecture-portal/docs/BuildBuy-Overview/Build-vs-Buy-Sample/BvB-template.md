# %title% Assessment

## Attestation

If the Build option was selected and/or BvB Assessment was not performed, attestion will need to be obtained from the Author, EA Representative (e.g. Principle Architect, Staff Architect, Solutions Architect), and other Engineering stakeholders.

| Name | Role | Attested Date |
| ----- | ----- | ----- |
| ... | Author | ... |
| ... | EA Representative | ... |
| ... | ... | ... |

## BvB Status History

| Authors | Status (Proposed/Accepted/Declined/Deprecated) | Date | Deciders |
| ----- | ----- | ----- | ----- |
| [Staff Engineers/Architects, Solutions Architects, etc] | Proposed | ... | N/A |
| [Staff Engineers/Architects, Solutions Architects, etc] | Accepted | ... | [Head Engineers, Principal Architects, Executives, Enterprise ARB, etc] |
| ... | ... | ... | ... |

## Business Vision and Objective

%description%

### Functional Requirements

| Description | Core/Non-Core |
| ----- | ----- |
| ... | ... |

### Non-Functional Requirements

| Description | Core/Non-Core |
| ----- | ----- |
| ... | ... |

### Stakeholders

| Name | Role |
| ----- | ----- |
| ... | ... |

## Assessment

<iframe width="100%" height="1000" frameborder="0" scrolling="no" src="https://spaces.example.com/teams/GR%20Architecture/_layouts/15/Doc.aspx?sourcedoc={282EB8CB-0E22-4EC7-8609-D028F5270374}&action=embedview&wdAllowInteractivity=False&wdHideGridlines=True&wdHideHeaders=True&wdDownloadButton=True&wdInConfigurator=True&wdInConfigurator=True"></iframe>

## Recommendation

Based on the analysis and review of the various options which were assessed using a scorecard, provide the final recommendation in this section.

e.g. Enterprise Architecture conditionally recommends the ARENA redaction SDK for use across generative AI applications. The tool provides the following features that make it ideal for enterprise-grade redaction.

### Features

e.g.
- Provides a comprehensive library of "recognizers" for various types of SDE (50+)
- Easily expandable to new types of SDE
- Operates as an independent microservice
- Has tools for identifying SDE within a string, as well as redacting, masking, or replacing the element
- Uses a combination of regular expressions and NLP models

### Conditions of Recommendation

e.g.
- Testing of response time, latency, and volume thresholds for the microservice and the definition of corresponding SLAs
- Implementation of a 2-way tokenization/pseudonymization solution with capabilities for both anonymization and de-anonymization alongside a secured database for mapping storage
- Creation of module-level documentation for all internally used classes and functionalities

## Related Decisions

List any related decisions that are connected to this one. This could include previous decisions that influenced this one, or future decisions that will be impacted by it.

e.g.
- <a href="https://github.example.com/platform-team/ea-design-playbook/blob/main/architecturedecisionrecord/template.md">ADR 1</a>


