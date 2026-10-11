# Design Language System Prescriptive ADR

| Choose One [X] |  ADR Type  | Description |
| -------------- | ---------------- | ----------- |
|                | **architecture** | Describes a solution that a team proposes about the architecture of an Initiative/Platform, or to be applied across the Enterprise. This can also set a precedent in that future problems having the same patterns might be able to leverage the same solutions. |
|                |  **buyvsbuild**  | Describes a choice that a team proposes on the implementation of a building block (i.e. Buy, Build, Reuse) |
| X              | **prescriptive** | Describes various prescriptions that a team proposes based on certain patterns. In most cases, prescriptions are expressed in the form of a decision tree. |

This ADR serves as guidance to all web based experiences. Teams building web based experiences may utilize the information within to align the resource and tools available to acheive succesfull deployment of their web based experience. 

## ADR Status History

| Authors         | Status (Proposed/Accepted/Declined/Deprecated) | Date  | Deciders |
|-----------------| ---------------------------------------------- |-------| -------  |
| Edward Hurst    | Proposed                                       | -TBC- | N/A      |

## Context & Problem Statement

Within frontend engineering there are a number of interaction patterns that are frequently reused across applications. Whilst the individual applications and frameworks that encapsulate these experiences may use different approaches, this is often invisible to consumers who will expect UI patterns to offer a consistent brand identity and provide common functionality and behavior. This ADR aims to provide a prescriptive approach to implementing these common interactions, enabling greater consistency in behaviour, branding, and reducing technical overhead across the organization.

## Decision Drivers

| **Driver**                | **Description**                                                                                                                                                    |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Brand Consistency         | Chosen systems should provide a consistent visual aesthetic to enable all components to follow the same visual affordance and digital brand identity.              |
| Accessibility (a11y)      | Chosen systems must be accessibile, allowing consumers to make use of assistive technologies in accordance with industry recommendations and Enterprise policies.  |
| Reusability               | Chosen systems should allow for development teams to easily create experiences that reuse the same patterns without resulting in duplicated effort.                |
| Compatibility             | Chosen systems should be compatible with technologies and standards available to modern browsers and devices supported by Enterprise.                                    |
| Developer Experience (DX) | Chosen systems should be easy to use and understand, allowing developers to quickly build and deploy web based experiences.                                        |
| Composable                | Chosen systems should not inhibit a team's ability to deliver highly custom, unique, or novel experiences.                                                         |
| Performance               | Chosen systems should be performant and scalable, able to be used in applications that handle high traffic and large data sets.                                    |
| Support                   | Chose systems should have a definitive support system for engineers using the platform.                                                                            |

## Options Considered

### Design System Components

Pros:
* The Design System owns the digital brand of the enterprise and provides a centralised system of record for design decisions such as typography, colors, allowing it to provide a consistent visual affordance across components.
* Design System components are built from the ground up with accessibility principles and are rigorously tested with assistive technologies to ensure that they follow best practice, and comply with Enterprise policies.
* Design System components are designed to be composable, allowing teams to utilise multiple components to make custom patterns and experiences that can themselves be reused across the enterprise.
* Design System components are built using React and Typescript, enabling IDE integration with code hinting systems to empower Developers, enhance DX and promote faster development, additionally this allows for easy onboarding for new developers, and enables them to quickly become productive.
* Design System components are built with a focus on performance, ensuring that they are lightweight and fast to load, even in high traffic applications.
* A dedicated Design System team provides support and guidance to developers across the enterprise, ensuring that they are used effectively and follow best practices.

Cons:
* Components can be restrictive, as they are designed to follow a specific set of design principles and patterns that needs to support a number of use cases across the enterprise, which may not always provide the flexibility desired by a specific application.
* Design System components may not be suitable for all use cases, particularly those that require highly custom or unique experiences that do not fit within the Design System's design principles.

### Local Component Library
Pros:
* Local component libraries can be tailored to the specific needs of an application, allowing for greater flexibility and control over the design and behavior of components.
* Local component libraries can be built faster than Design System components, as they do not need to go through the same level of review and testing, allowing teams to quickly iterate on their designs and implement new features.

Cons:
* Individual teams making components will need to spend significant effort to follow best practices for accessibility, leading to potential issues for users with disabilities if the same rigorous testing and review process is not followed.
* Custom component libraries can lead to inconsistencies in design and behavior across applications, as each team may implement components differently.
* Custom component libraries may not be compatible with the latest web standards and technologies, leading to potential issues with performance and scalability.
* Maintenance and updates are still required, leading to duplication of effort and potential conflicts as each team may have their own version of the same components.
* Custom component libraries may not be well supported, leading to potential issues for developers who need help or guidance on how to use the components effectively.
* Custom component libraries may not be well integrated with the Design System, leading to potential issues for developers who need to ensure that their applications follow the same design principles and patterns.

## Decision

### Internet & Customer Facing Applications
For internet and customer facing applications, where it is critical to maintain a consistent user experience and brand identity, the decision is to use Design System components. This ensures that these applications follow the same design principles and patterns, providing a consistent visual affordance, a singular digital brand identity across the enterprise, and familiar interactions for users.

Applications that want to provide more unique experiences that do not fit within the Design System's design principles and patterns, or that require highly custom or unique experiences, should use the Design System components as a foundation and look to extend them with local components to provide additional functionality or customization.

### Intranet Based Applications
Where applications are built for internal use, such as intranet based experiences, the decision is to use Design System components for the same reasons as internet applications. This ensures that all internal applications follow the same design principles and patterns, providing a consistent visual affordance and accessibility standards across the enterprise.

It's accepted that some internal applications may require more unique experiences that do not fit within the Design System's design principles and patterns. In these cases, teams should still use Design System components as a foundation and look to extend them with local components to provide additional functionality or customization.

### Customization and Unique Experiences

Where customization is required, teams should look to communicate with the Design System team to discuss how best to extend the Design System components to meet their needs. This may involve creating new components that follow the same design principles and patterns, or extending existing components to provide additional functionality or customization.

## Exemption Process

Teams believing their use case should be exempt must submit a formal architecture exception request to the Enterprise Architecture Review Board, including:
- Detailed technical requirements not met by the system
- Proposed alternative solution with comprehensive accessibility review steps.
- Cost-benefit analysis justifying the alternative approach
- Migration path to eventually adopt the enterprise platform
