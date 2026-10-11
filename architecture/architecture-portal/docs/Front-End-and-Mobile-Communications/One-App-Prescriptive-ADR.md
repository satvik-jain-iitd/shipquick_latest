# Web based experiences Prescriptive ADR 

| Choose One [X] |  ADR Type  | Description |
| -------------- | ---------------- | ----------- |
|                | **architecture** | Describes a solution that a team proposes about the architecture of an Initiative/Platform, or to be applied across the Enterprise. This can also set a precedent in that future problems having the same patterns might be able to leverage the same solutions. |
|                |  **buyvsbuild**  | Describes a choice that a team proposes on the implementation of a building block (i.e. Buy, Build, Reuse) |
| X              | **prescriptive** | Describes various prescriptions that a team proposes based on certain patterns. In most cases, prescriptions are expressed in the form of a decision tree. |


This ADR serves as guidance to all web based experiences. Teams building web based experiences may utilize the information within to align the resource and tools available to acheive succesfull deployment of their web based experience. 

## ADR Status History

| Authors                                                 | Status (Proposed/Accepted/Declined/Deprecated) | Date  | Deciders |
|---------------------------------------------------------| ----- |-------| ----- |
| Michael Rochester                                       | Proposed | -TBC- | N/A |

## Context & Problem Statement

There are many ways to build web based experiences, including platforms, frameworks, libraries, patterns, and tools. Free choice over all these components can lead to a fragmented experience for both developers and users. This ADR aims to provide a prescriptive approach to building web based experiences, ensuring consistency, maintainability, and scalability across the organization.

## Decision Drivers

| **Driver**                | **Description**                                                                                                                                        |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| Capability                | Chosen systems should not inhibit teams ability to deliver highly custom, unique, or novel experiences.                                                    |
| Reusability               | Chosen systems should allow for the central development of certain common capabilities, such as auth, navigation, and data management.                 |
| Performance               | Chosen systems should be performant and scalable, able to handle high traffic and large data sets.                                                     |
| Security                  | Chosen systems should be secure, protecting user data and preventing unauthorized access.                                                              |
| Compliance                | Chosen systems should not only be compliant to Enterprise Compliance standards, but also be customizable enough to adhere to any future compliance standard. |
| Resiliancy                | Chosen systems should be highly fault tolerant, even under extreme load.                                                                               | 
| Developer Experience (DX) | Chosen systems should be easy to use and understand, allowing developers to quickly build and deploy web based experiences.                            |
| Skill availability        | Chosen systems should rely mostly on industry standard techniques and language, allowing for external hires to be onboarded quickly.                   |

| Support                   | Chose systems should have a definitive support system for engineers using the platform. Third party systems need an SLA level that will not hinder development using the system. |

## Options Considered

### One App

Pros
* One App relies on React JS for all general UI development, this allow it to fulfill the Capability, DX, and Skill availability drivers.
* One App has security built in, with out the box features such as CSP, HTTP method restriction, eval inhibition, correct header defaults such as CORS and HSTS.
* One Apps use of micro-frontends allow for entire sections of an app to be re-used, or be 'off the shelf' components developed by other 2nd party teams, such as the global header, global footer, and SSO-auth modules.
* One App's SSR first and micro-fronteded structure allows for high performance derived from low TTFB (due to SSR) and optimized delivery of only the code needed for the current page (due to micro-frontends).
* One App's in house development focus means that the core framework will be updated to adhere to any and all new regulatory, security, and compliance requirements mandated by the enterprise. For example, One App's CICD was update to make complying with TECH 08.21 trivial for all consumers. This allows it to fulfill the Compliance driver.
* The Web Frameworks team provides direct support on the platform via two focussed channels. the slack channel #one-dev, where developer support is available, and the slack channel #one-devops, where CICD and prod support is available.
* One App's use of micro-frontends allows for independent development and deployment of multiple experiences within an application. Even if one part of an application fails, all other parts of the application can remain functional. This allows it to fulfill the Resiliancy driver.

Cons
* Some aspects of One App, such as configuration, and deployment, are in house, requiring a 1 day training course be taken by new hires, regardless of their experience level.
* One App being a highly dynamic framework is not ideal for mostly static experiences, such as marketing sites and brochures.

### One CMS

Pros
* One CMS is a managed editor experience, allowing for easy content management and updates by product and buisness partners without requiring developer involvement. This allows it to fulfill the Capability driver. This also fulfills the Developer Experience driver, however it explicitly fullfils the DX driver for non-technical users.
* One CMS is centrally managed, reducing the cost of maintenance and hosting of websites. This fullfils the Performance, and Security driver, as both of these are solved for centrally.
* One CMS has a set of components that can be re-used across any One CMS application, accelerating delivery. This allows it to fulfill the Reusability driver.
* One CMS' in house development focus means that the core platform will be updated to adhere to any and all new regulatory, security, and compliance requirements mandated by the enterprise. This allows it to fulfill the Compliance driver.
* The One CMS team provides direct support on the platform, allowing for easy access to help and guidance. This allows it to fulfill the Support driver.

Cons
* One CMS does not allow for arbitrary runtime extensions, meaning that it is harder to build highly dynamic applications, and data driven applications, such as logged in experiences, and monitoring dashboard

## Decision

For dynamic experiences of any size, such as logged in experiences, dashboards, and data driven applications, the decision is to use One App.

One Apps capabilities are purpose-built to support the following use-cases, eliminating the need for alternative solutions:

 * Large Websites: The micro-frontend architecture of One App allows for the development of large websites maintained by multiple independent teams, while still allowing for a consistent user experience and shared components.
 * High Interaction Websites: One App's use of ReactJS allows for the development of highly interactive websites, such as those with large forms, multi-step journeys, and complex user interactions.
 * High Performance Websites: One App's SSR first approach and micro-frontend architecture allow for the development of applications that respond quickly to both initial requests, and subsequent interaction.
 * Small Websites: One App's micro-frontend architecture explicitly supports a 'Single Module' Application, allowing for the development of small websites that can be managed, maintained, and deployed to production with the absolute minimum team effort.

For more static and content driven experiences such as marketing sites, and brochures, the decision is to use One CMS. It allows non-technical users to manage content efficiently without requiring developer involvement.

### Prescription

| Use Case                                                                                                       | Prescription |
|----------------------------------------------------------------------------------------------------------------|--------------|
| Websites that load and present significant amounts of data                                                     | Use One App  |
| Websites that involve high amounts of interaction, large forms, multi-step joruneys, etc                       | Use One App  |
| Websites of any size that are dynamic, react to user input, or require browser managed state                   | Use One App  |
| Websites that involve multiple critical journeys that are related, but need to be resilient to partial failure | Use One App  |
| Websites that are mostly static, and have little if any dynmaic interaction                                    | Use One CMS  |
| Websites managed and updated by business or product teams without involvement from technical teams             | Use One CMS  |

### Consequences

**Positive Consequences** 
- With a clear path for building different types of applications, there will be less varience in DX, and UX across the organization. Once engineers become skilled at creating one type of site, they can bring that skill anywhere else in the enterprise and be immediately effective.
- As these choices are internally supported, engineers who use them will always have someone internal to ask for help, and receive guidance on the best way of doing things.
- Since so few choices still cover such a wide range of applications, large system changes will be easier to implement, as there will be less variance in the code base.
- Since the underlying technologies for both choises are industry standard (ReactJS for one-app, and HTML for one CMS), it will be easy to find new hires who are already familiar with the systems, and can be onboarded quickly.

**Negative Consequences**
- With two choices, certain components will have to be built to support two systems, such as auth, and shared components like headers and footers.

### Out Of Scope: Documentation Sites

Developer documentation sites are a mix between dynamic, and content driven sites. Although One App or One CMS could be used to build these sites, discussion on which is best, or weather to use a completely different aproach such as Confluence, is out of scope for this ADR.

## Exemption Process

Teams believing their use case should be exempt from using this platform must submit a formal architecture exception request to the Enterprise Architecture Review Board, including:
- Detailed technical requirements not met by the platform
- Proposed alternative solution with comprehensive security and governance controls
- Cost-benefit analysis justifying the alternative approach
- Migration path to eventually adopt the enterprise platform
