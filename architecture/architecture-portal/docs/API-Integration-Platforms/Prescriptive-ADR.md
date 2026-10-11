This page describes approved enterprise mediation platforms for TECH06.61 Integration standard.


- - -

## **Prescriptive ADR for API Endpoint Placement**

**Target Audience**

This repository serves as guidance to API Providers across all of ENTERPRISE. API Providers may utilize the information within to align with the resources and tools available to achieve successful deployment of API Products.

**Roles & Responsibilities**

Reference list of different roles involved with API workload at all lifecycle states:

|     |     |
| --- | --- |
| Role | Notes |
| API Provider | API workload owner, responsible for API design, documentation, implementation, access management and complete API lifecycle including maintenance and modernization |
| [EA](https://thesquare.example-org.com/sites/business-unit/technology/enterprise-architecture/SitePageModern/384610/enterprise-architecture) | Enterprise Architecture, provides consulting and architecture reviews; [EA's consulting intake form](https://enterprise-confluence.example.com/confluence/display/ER/Intake+Form) |
| [API Partner Sandbox](https://github.example.com/pages/platform-team/eas-playbook/) | Highly available B2B API sandbox utility, exposes non-production API endpoints for external partners to safely implement and validate their API clients |
| [AED DevPortal](https://developer.example-org.com/) | External API catalog, B2B inbound only; implements self-service partner user journeys including registration, documentation, access management, certificate exchange and more |
| API Platform | ENTERPRISE approved backbone of systems that assist in design, build, manage and consumption of APIs. API Platforms support API Lifecycle, Strategy Implementation, Security, Standardization, Observability, Governance, Automation and Engagement |
| [AppSec](https://security.example.com/architecture-design/#/hc/en-us) | Baya threat assessment and consulting |
| [EID](https://idaas.example.com/) | Enterprise ID team, IDaaS and consulting |
| API Consumer | Internal or external API consumer with client applications initiating requests to APIs |

**Note:** This ADR has content tailored for **API Providers** and **API Consumers**. Teams responsible for the **API Platforms** listed in this page should refer to roles and responsibilities and platform controls described in the [API Platform Group](https://enterprise-confluence.example.com/confluence/spaces/APG/pages/1354029842/API+Platform+Group+Home) space.

**This article defines guidelines for approved integration platforms to support various patterns including:**

**Realtime / Synchronous integrations**

* C2B - web, mobile and other customer channels to Enterprise services (on-prem)

* B2B - 3rd party partner to Enterprise services (on-prem) - inbound

* B2B - Enterprise services (on-prem) to 3rd party partner - outbound

* B2B - Enterprise public cloud to Enterprise services (on-prem) over public internet

* B2B - Enterprise services (on-prem) to 3rd party partner - file transfers, batch processing

* B2B - Enterprise services (on-prem) to 3rd party partner async message-based integration

* B2B - 3rd party partner to Enterprise services (on-prem) async message-based integration

* A2A - Enterprise services (on-prem) to Enterprise services (on-prem)

* A2A - public cloud to Enterprise services (on-prem) over dedicated lines (e.g. DirectConnect, DirectInterconnect, ExpressRoute, VPN etc)

* A2A - Enterprise services (on-prem) to public cloud over dedicated lines

* A2A - public cloud to public cloud same cloud platform VPC

* A2A - public cloud to public cloud different cloud platform VPCs



**Asynchronous integrations**

* B2B - Enterprise services (on-prem) to 3rd party partner async message-based integration

* B2B - 3rd party partner to Enterprise services (on-prem) async message-based integration

* A2A - Enterprise services (on-prem) to Enterprise services (on-prem), public cloud to Enterprise services (on-prem) (e.g. DirectConnect, DirectInterconnect, ExpressRoute, VPN etc), on prem to public cloud, public cloud to public cloud - async message-based integration



**API platform workload placement guidelines:**

Instructions:

1.  API Provider team to identify integration pattern for your new workload; eg B2B inbound
2.  Consider the first option for the applicable pattern; eg REST API services published in AED
3.  If first option cannot be used because of any reason, then consider the next option until a suitable one is found; in this case, follow the EA Playbook template to document the decision as an ADR, including all considered options and review it with an Enterprise Architect
4.  If no option in the list can be used to support the new workload, document it as described in step 3 and also submit a new exception request against TECH06.61 Integration Standard; describe decisions to mitigate risks and implement compensating controls



**Realtime / Synchronous integrations**

* **C2B - web, mobile and other customer channels to Enterprise services (on-prem)**

    *  GraphQL - Choreo

    *  REST APIs - EWP API Gateway

    *  WebSocket APIs - EWP API Gateway - persistent connection for realtime bi-directional communication (web chats etc)

    * RPC / REST APIs - One Data

* **B2B - 3rd party partner to Enterprise services (on-prem) - inbound**

   *  REST - Enterprise DevPortal (external API catalog, uses B2B API GW but scalable onboarding / operational controls)

   *  REST - EWP API Gateway (new integrations, new capabilities)

   *  NeMo CoreSwitch - payment-specific integrations (ATMs, point of sale)

   *  REST - Apigee B2B API Gateway (existing integrations created before 12/31/2024, deprecated for new integrations)

* **B2B - Enterprise services (on-prem) to 3rd party partner - outbound**

   * REST - EWP API Gateway (outbound API integrations)

   * REST - NetSec Network App Proxy (existing outbound API integrations created before 12/31/2024, deprecated for new API integrations)

   * REST - NetSec Network App Proxy (outbound non-API integrations)

* **B2B - Enterprise public cloud to Enterprise services (on-prem) over public internet**

  * REST - EWP API Gateway

* **B2B - Enterprise services (on-prem) to 3rd party partner - file transfers, batch processing**

  * SFTP, Connect:Direct, AS2, FTPS, HTTPS

  * REST, TCP - EWP API Gateway (only message payloads <5MB in realtime integrations that cannot use SFT and do not require SFT capabilities)

* **B2B - Enterprise services (on-prem) to 3rd party partner async message-based integration**

  * Messaging - RTF - implements support for guaranteed delivery for mission critical apps

* **B2B - 3rd party partner to Enterprise services (on-prem) async message-based integration**

  * Messaging - RTF - implements support for guaranteed delivery for mission critical apps

* **A2A - Enterprise services (on-prem) to Enterprise services (on-prem)**

  * gRPC, REST - eCP Hydra Service Mesh

  * gRPC, REST - EAG API Gateway

  * RPC / REST APIs - One Data

  * SOAP – Data Power (existing integrations created before 12/31/2024, deprecated for new integrations)

* **A2A - public cloud to Enterprise services (on-prem) over dedicated lines (e.g. DirectConnect, DirectInterconnect, ExpressRoute, VPN etc)**

  * gRPC, REST - eCP Hydra Service Mesh

  * gRPC, REST - EAG API Gateway

  * RPC / REST APIs - One Data

* **A2A - Enterprise services (on-prem) to public cloud over dedicated lines**

  * gRPC, REST - eCP Hydra Service Mesh

  * gRPC, REST - EAG API Gateway

  * RPC / REST APIs - One Data

* **A2A - public cloud to public cloud same cloud platform VPC**

  * gRPC, REST - eCP Hydra Service Mesh

* **A2A - public cloud to public cloud different cloud platform VPCs**

  * gRPC, REST - eCP Hydra Service Mesh



**Asynchronous integrations**

* **B2B - Enterprise services (on-prem) to 3rd party partner async message-based integration**

  * Messaging - RTF - implements support for guaranteed delivery for mission critical apps

* **B2B - 3rd party partner to Enterprise services (on-prem) async message-based integration**

  * Messaging - RTF - implements support for guaranteed delivery for mission critical apps

* **A2A - Enterprise services (on-prem) to Enterprise services (on-prem), public cloud to Enterprise services (on-prem) (e.g. DirectConnect, DirectInterconnect, ExpressRoute, VPN etc), Enterprise services (on-prem) to public cloud, public cloud to public cloud - async message-based integration**

  * Messaging - RTF - implements support for guaranteed delivery for mission critical apps

  * Messaging - Hyperdrive - high volume and velocity event streaming platform

  * Messaging - xPaaS Kafka - only BIA tier 3 applications; no built-in active/active DR capabilities



**API Lifecycle**

The next sections will describe roles and responsibilities on API workloads across the following lifecycle states:

1. Onboarding - onboarding API workloads in development, test and production
2. Live - managing and operating existing APIs, including client access management, monitoring and support
3. Decommisioned - retirement of API workloads, either replacing it with new versions or sunsetting due to business decisions



**API Onboarding**

**Example B2B API Workload Onboarding Process**

![B2BAPIWorkloadOnboardingHL](images/B2BAPIWorkloadOnboardingHL%20Process.png)


Each approved API platform listed in this article may implement different onboarding developer experiences - but all of them follow this similar process:

1.  Based on the **API Provider Lifecycle,** during the Design and Develop Phases, the **API Provider** determines appropriate API platform placement based on [Prescriptive ADR for API Integration Platforms](https://architecture1.example.com/docs/46ed218e-cb4d-45e8-ba28-ed4e12870517)
    1.  Following alignment with standard prescriptions the **API Provider** determines appropriate API platform placement (LOE = S)\*
    2.  If The **API Provider** determines their build to be an outlier, a consulting engagement\*\* directly with Enterprise Architecture is initiated to determine possible paths to success (LOE = M-L)\*
2.  **API Provider** [creates new](https://enterprise-confluence.example.com/confluence/ea%20design%20playbook:%20Template%20Repo) or expands existing EA Playbook knowledge repository with details about the new integration (LOE = S-M)\*
3.  **API Provider** completes threat modeling for new or modified integrations – engages with **AppSec** as required for consulting and Baya support (LOE = S)\*
4.  **API Provider** initiates new onboarding request - self-service or manual engagement - to the approved **API Platform** (LOE = L)\*
    1.  API metadata is validated - CAR ID lifecycle state, threat assessment status, required controls such as rate limits, connection and IO timeouts are set (LOE = M)\*
    2.  API auth mechanism is setup in low environments - E1/E2 (LOE = M)\*
    3.  API workload is deployed in low environments - E1/E2 (LOE = S)\*
5.  \[B2B\] **API Provider** initiates new onboarding request - self-service or manual engagement - to **[B2B Partner API Sandbox](https://github.example.com/pages/platform-team/eas-playbook/)** (LOE = S)\*
    1.  API Provider initiates and deploys B2B Partner API Sandbox in lower environments - E1/E2 (LOE = M for each environment)\*
6.  **API Provider** completes API design, implementation, deployment and validation in low environments (LOE = M)\*
    1.  API is automatically published into [ThirdEye API Catalog](https://thirdeye.example.com/) (LOE = None)\*
7.  **API Provider** initiates and completes API deployment in E3 (LOE = S)\*
8.  **API Provider** initiates production deployment promotion request to the approved **API Platform** (LOE = S)\*
    1.  API metadata is validated - CAR ID lifecycle state, threat assessment status, required controls such as rate limits, connection and IO timeouts are set (LOE = S)\*
    2.  API auth mechanism is setup in E3 (LOE = M)\*
    3.  API workload is deployed in E3 (LOE = S)\*
9.  **API Provider** initiates production deployment of **B2B Partner API Sandbox** (LOE = S)\*
10.  \[B2B\] **API Provider** initiates new API Product onboarding or content update request to **AED DevPortal** (LOE = XL)\*
11.  **API Provider** share AED DevPortal Product details with **API Consumer(s)** to initiate product onboarding (LOE = S)\*

\*LOE - S = < 1 day of 1 Developers Work Effort, M = 1-2 Weeks of 1 Developer Work Effort, L = 3-4 Weeks of 1 Developer Work Effort, XL = > than 4 weeks of 1 Developer Work Effort

\*\*For initiatives in which standard prescriptions indicated do not provide adequate solution, please reach out to the EA team by requesting a consulting engagement [here](https://enterprise-confluence.example.com/confluence/display/ER/Intake+Form).



**Managing Live APIs**

  * **API Provider** is responsible for client interactions including access management to their APIs via **AED DevPortal (B2B)** and **EID IDaaS**.

  * **API Provider** is responsible to monitor and troubleshoot service issues for their APIs. **API Platform** must offer production support mechanisms such as realtime alerts, access logs and other capabilities to support workload service monitoring and troubleshooting.



**Decommissioning APIs**

  * **API Provider** is responsible to initiate decommissioning requests for their APIs when these are no longer required. 

  * **API Platform** is responsible to implement recurring reports to identify idle API endpoints, or live APIs with no active traffic for over 90 days. Findings are shared with **API Provider** and, when a remediation plan cannot be confirmed within 1 sprint, **AppSec** must be informed. 



**Enterprise Integration Platforms:**



| Enterprise Integration Platform | Onboarding | Monitoring | Support |
| --- | --- | --- | --- |
| **Choreo - GraphQL B2C omni-channel business APIs** | [![choreo](images/onboarding.png)](https://choreodocs.example.com/start/getting-started/) | [![choreo logging](images/monitoring.png)](https://choreodocs.example.com/reference/observability/logging/) | [![choreo logging](images/support.png)](https://choreodocs.example.com/reference/choreo-production-support-process/) |
| **One Data - FaaS compute platform** | [![choreo logging](images/onboarding.png)](https://onedata.example.com/docs/category/getting-started) | [![choreo logging](images/monitoring.png)](https://onedata.example.com/docs/category/observability) | [![choreo logging](images/support.png)](https://onedata.example.com/docs/how-to/troubleshoot/best-practices-and-support)|
| **Enterprise Developer Portal - External API catalog for B2B integrations** | [![choreo logging](images/onboarding.png)](https://enterprise-confluence.example.com/confluence/display/DCE/Self+Service%3A+New+Product+Onboarding+Request+Form)| [![choreo logging](images/monitoring.png)](https://a4dintranet.example.com/)| [![](images/slack.png)](https://slack.com/app_redirect?channel=C04NHBKD7DW) |
| **NeMo CoreSwitch API GW specialized on payment integrations (ATMs, point of sale etc)** | [![choreo logging](images/github.png)](https://github.example.com/platform-team/gmnst-architecture) | [![choreo logging](images/monitoring.png)](https://grafana-r1.example.com/d/nauq8GQnz/payment-network-web-traffic?orgId=1&from=now-30d&to=now&var-source=App-Prometheus-IPC1&var-zone=ipc1) | [![](images/slack.png)](https://slack.com/app_redirect?channel=CD61LLNEA)|
| **EWP - Enterprise Web Proxy external next-gen API GW** |[![choreo logging](images/onboarding.png)](https://connectedgegtm-dev.example.com/dashboard)|[![choreo logging](images/monitoring.png)](https://github.example.com/pages/platform-team/connect-web/monitoringnew)|[![choreo logging](images/support.png)](https://github.example.com/pages/platform-team/connect-web/docs/playbook/support/support-overview)|
| **EAG - Enterprise API Gateway internal next-gen API GW** |[![choreo logging](images/onboarding.png)](https://connectedgegtm-dev.example.com/dashboard)|[![choreo logging](images/monitoring.png)](https://github.example.com/pages/platform-team/connect-web/monitoringnew)|[![choreo logging](images/support.png)](https://github.example.com/pages/platform-team/connect-web/docs/playbook/support/support-overview)|
| **Hydra Service Mesh - Istio-based cloud native service mesh platform** | [![choreo logging](images/onboarding.png)](https://hydra.example.com/) | [![choreo logging](images/monitoring.png)](https://enterprise-confluence.example.com/confluence/pages/viewpage.action?pageId=414762068)| [![choreo logging](images/support.png)](https://cloud.example.com/support-directory)||
| **RTF - Real Time Framework messaging platform** | [![choreo logging](images/onboarding.png)](https://rtfregistry.example.com/)| [![choreo logging](images/monitoring.png)](https://rtfregistry.example.com/) | [![](images/slack.png)](https://slack.com/app_redirect?channel=CCHHL2AA1) |
| **Hyperdrive - high volume and velocity event streaming platform** |[![choreo logging](images/onboarding.png)](https://hyperdrive.example.com/home)|[![choreo logging](images/monitoring.png)](https://spaces.example.com/teams/hyperdrive/SitePages/Tracing-Events.aspx)| [![](images/slack.png)](https://slack.com/app_redirect?channel=CJANZUV5W) |
| **xPaaS Kafka - messaging platform as a service** |[![choreo logging](images/onboarding.png)](https://enterprise-confluence.example.com/confluence/display/ED/eCP+xPaaS+Kafka+Real-time+Data+Streaming+as+a+Service)|[![choreo logging](images/monitoring.png)](https://enterprise-confluence.example.com/confluence/display/ED/eCP+xPaaS+Kafka+Real-time+Data+Streaming+as+a+Service)|[![choreo logging](images/support.png)](https://enterprise-confluence.example.com/confluence/display/ED/eCP+Support+Services) |
| **SFT - External & internal Secure File Transfer platform** | [![choreo logging](images/onboarding.png)](https://sftcentral.example.com/home) | [![choreo logging](images/monitoring.png)](https://sftcentral.example.com/home)| [![choreo logging](images/support.png)](https://thesquare.example-org.com/sites/business-unit/technology/secure-file-transfer/SitePageModern/689719/overview) |
| **Network App Proxy - L3 / L4 outbound proxy** |[![choreo logging](images/onboarding.png)](https://thesquare.example-org.com/sites/enterprise/tools-and-programs/colleague-internet-security/documents/807507/web-exception-requests-current)|[![choreo logging](images/mailto.png)](mailto:proxy_engineering@example.com)|[![choreo logging](images/mailto.png)](mailto:proxy_engineering@example.com)|





- - -



**References:**

*   [TECH06.61 Integration standard](https://spaces.example.com/sites/global%20standards%20library/Shared%20Documents/TECH06.61%20Integration%20Standard.pdf)
*   [TECH06.35 API Security standard](https://spaces.example.com/sites/global%20standards%20library/Shared%20Documents/TECH06.35%20Application%20Programming%20Interface%20(API)%20Security%20Standard.pdf)
