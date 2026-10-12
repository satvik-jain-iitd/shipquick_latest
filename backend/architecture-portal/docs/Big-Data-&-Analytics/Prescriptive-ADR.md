This page describes approved enterprise mediation platforms for TECH06.61 Integration standard.


- - -

# Big Data and Analytics Prescriptive ADR


| Choose One [X] |  ADR Type  | Description |
| -------------- | ---------------- | ----------- |
|                | **architecture** | Describes a solution that a team proposes about the architecture of an Initiative/Platform, or to be applied across the Enterprise. This can also set a precedent in that future problems having the same patterns might be able to leverage the same solutions. |
|                |  **buyvsbuild**  | Describes a choice that a team proposes on the implementation of a building block (i.e. Buy, Build, Reuse) |
| X              | **prescriptive** | Describes various prescriptions that a team proposes based on certain patterns. In most cases, prescriptions are expressed in the form of a decision tree. |


## ADR Status History

| Authors | Status (Proposed/Accepted/Declined/Deprecated) | Date | Deciders |
| ----- | ----- | ----- | ----- |
| Lakshmi Isukapally, Kalyan Cherukuri | Proposed | May 16, 2025 | N/A |
| ... | ... | ... | ... |

## Context & Problem Statement

Over time, the proliferation of various data platforms and tools has led to fragmentation and inefficiencies in data management and utilization. This disjointed approach not only hampers the seamless flow of data across the organization but also increases operational complexity and costs. To address these challenges, it is imperative to standardize a few core platforms that can provide comprehensive capabilities and ensure unified data management across the enterprise.

Lumi is the enterprise Unified Data platform with Data warehouse and Data Lake capabilities, It is authoritative data source for governed enterprise data that is useful for many Analytical and Production processing.

This is aligned to our organizational alignment on streamline data management, data processing, and analytics across the enterprise:

- Provides important enterprise datasets through well-defined interfaces
- Supports multiple consumption patterns (batch extracts, APIs, direct queries)
- Provides Analytics capability needing trusted data for insights generation

To ensure a standardized, scalable, and efficient approach to handling Big Data workloads, Lumi must be adopted as the enterprise-wide Data Lakehouse and Big Data processing platform. This decision aligns with our organization's goal of being an authorized data source, centralizing data management, improving performance, efficiency, and enabling advanced analytics across all business units.


## Rationale

Lumi is the prescribed solution due to the following advantages:
-	Enterprise-Wide Standardization: Ensures consistency in data management, processing, and governance.
-	Scalability & Performance: Optimized for high-volume and high-velocity data workloads.
-	AI & ML Readiness: Seamless integration with AiDa for AI-driven analytics and machine learning.
-	Cost Efficiency: Reduces operational costs by optimizations implemented as part of the platform
-	Security & Compliance: Provides built-in access control, encryption, and audit logging.


## Decision
Lumi’s platform capabilities are purpose-built to support the following workloads, eliminating the need for alternative solutions.

Core Use Cases
- Migration from legacy data warehouses (e.g., Cornerstone) and standalone data marts
- Enterprise-wide reporting and analytics workloads
- Real-time, event-driven analytics with sub-minute latency requirements
- High throughput streaming data ingestion and processing
- All Automated insights generation use cases, powering dashboards, and continuous monitoring etc.
- Scalable data aggregation, transformation, and enrichment pipelines


Definitions
1. Operational Database (OLTP)
    - Run-the-business systems. Real-time, high-speed, transactional.
    - Stores data used for daily business processes.
    - Can be relational (SQL) or non-relational (NoSQL)—depending on the system's needs.
    - Prioritizes performance and consistency (Eventually).
2. Analytical Database (OLAP)
    - Understand-the-business systems. Strategic insights, trends, reporting.
    - Used for querying large volumes of data.
    - Optimized for aggregations, joins, complex queries, AI/ML workloads
    - Often fed by data pipelines (ETL/ELT).
3. Curated Data
    - Data that’s been Cleaned, transformed, validated, and enriched.
    - Can be used in dashboards, AI models, regulatory reports, Or can be exposed as API’s
    - Ideally should come with governance, quality checks, and business context.
4. System of Record (SoR)
    - The official "source of truth" for a given business entity.
    - Where data is officially maintained and governed.
5. System of Origination (SoO)
    - Where the data first enters the ecosystem—may or may not be the SoR.
    - Typically captures raw, unvalidated inputs.
6. Authorized Data Source (ADS)
    - System acts as the certified point of provisioning for a given data set. Must manage synchronization with the System of Record.  Lumi is the Designated ADS


## Prescription

#### Detailed Use Case Scenarios
|       Criteria        |     Scenario         |         Recommendation       |        Rationale        |
|   ------------------- | -------------------- | ---------------------------- | ----------------------- |
| Data Processing Type  | Batch /analytical processing requiring sophisticated transformations| Use Lumi| Lumi's data lake house architecture is optimized for these kind of workloads                         |
| | Operational data processing with minimal transformation | Can be outside of Lumi Use Containerized workloads (GKE) | Introduces unnecessary complexity to route through Lumi |
| SLA's | Batch-oriented processing with scheduled windows | Use Lumi |  Aligns with lake house strengths in handling large batch operations |
| | Real-time processing with sub- milli seconds response on operational data | Can be outside of Lumi | Direct stream processing provides lower latency than routing through Lumi |
| | Near real-time processing (near Realtime data processing, that needs to be enriched with Lakehouse data) |  Consider Hybrid Approach On Lumi Or Data as service from Lumi | depending on where data is, Process in Lumi then integrate results |
| Application Category | Tier 0 Applications | Outside Lumi | Bigdata/Precompute should not be part of Tier 0 application Scope |
|  Data Ownership | Enterprise-wide shared data assets |  Use Lumi |  Benefits from centralized governance and unified access controls |
| | Team-specific data with no sharing needs and No need for Direct Database access | Can be  outside of Lumi | Allows teams autonomy while reducing governance overhead |
| | Domain-specific data eventually needing enterprise sharing |Consider using Lumi. Make decision balancing on long-term strategy /immediate timelines | |
| | Internal operational data | Can be  outside of Lumi | can provide more flexible access patterns |
| Use case Type |  Multiple downstream use case consuming the data assets/Products | Use Lumi | Provides consistent, governed interface for multiple consumers |
| | Single-purpose, specialized application | Can be outside of Lumi | Direct connection reduces unnecessary layers |
| | Exploratory or experimental workloads. Temporary setups for POCs | For new -Setup consultation on this with Enterprise Big Data & EA team. For certified – use sandbox | Allows for rapid iteration without much overhead |
| | Data Exchange Zones with Third party (external) | TODO: Pending -Discuss on Ownership | Overlaps between Lumi & non-Lumi TODO: This needs to be standardized at platform level. |

#### Service Usage recommendations Data Processing & Analytics
|       Service        |     Description     |      When to Use     |     Ideal Workloads     |     Data Size Range     |     Key Features     |
| -------------------- | ------------------- | -------------------- | ----------------------- | ----------------------- | -------------------- |
| BigQuery | Serverless data warehouse | Use case: large-scale analytics, Enterprise analytics, BI, reporting | Complex queries, data science, enterprise reporting | Minimum: ~50GB to justify cost, Extends up to Exabyte scale | Separation of storage/compute, ML integration, federated queries |
| Dataflow | Stream and batch data processing |Use case: Real-time analytics, ETL. Real-time analytics, ETL/ELT pipelines | Stream processing, data pipelines, ML feature extraction | Extends up to Exabyte scale | Unified batch/streaming, autoscaling, exactly-once processing |
| Dataproc | Managed Spark and Hadoop | Use case: Batch processing, ETL, Big data processing with existing Spark/Hadoop workloads | Data transformation, ML training, legacy Hadoop migrations | Minimum: ~100GB to justify cluster overhead. Can scale up to handling Petabyte scale | On demand cluster creation, autoscaling, integration with GCS and BigQuery |
| Pub/Sub | Messaging and event streaming | Use case: Event-driven applications, streaming data pipeline. For decoupling systems | IoT data ingestion, application integration, activity streams | Minimum: No minimum (pay per message). Unlimited | At-least-once delivery, push/pull delivery, global availability |
| Cloud Composer | Managed Apache Airflow | Use cases – Data Pipelines Workflow orchestration and DAG Scheduling | orchestration, scheduled tasks | N/A (metadata service) | DAG-based workflows, rich operator ecosystem, monitoring |
| Dataplex | Dataplex | Enterprise data management | Cross-organization data governance, data discovery | N/A | Unified management, intelligent data organization, integrated security |

#### Storage Services
|       Service        |     Description     |      When to Use     |     Suggested Workloads     |     Data Size Range     |     Security     |     Key Features     |
| -------------------- | ------------------- | -------------------- | --------------------------- | ----------------------- | ---------------- | -------------------- |
| Cloud Storage | Object storage service | Raw data landing, data lakes, backups, archiving | Unstructured data, media files, backups, data lake foundations | Unlimited (practical limits in PBs) | Wiresafe-Batch to protect sensitive files. | Tiered storage classes, lifecycle policies, strong consistency |
| Cloud SQL | Managed relational database service | Transactional applications, structured data with complex relationships | Realtime / web applications | Minimum ~10GB to be cost-effective Max Up to ~64TB | Wiresafe-Online to encrypt sensitive values/columns | MySQL, PostgreSQL, SQL Server support, automatic backups |
| Cloud Spanner | Globally distributed relational database | Mission-critical applications requiring both scale and consistency | High-throughput transactional systems, globally distributed relational database | Minimum: ~2TB to be cost-effective. Can go up to Petabyte scale | Wiresafe-Online to encrypt sensitive values/columns | Horizontal scaling, 99.999% availability, strong consistency |
| Firestore | NoSQL document database | Web/mobile apps with real-time updates. Use case: Web/mobile app data, semi-structured data | Real-time collaborative applications | Minimum: No minimum (pay for operations). Can go up to up to tens of TBs | Wiresafe-Online to encrypt sensitive values | Real-time listeners, automatic scaling |
| Bigtable | NoSQL wide-column database | High-throughput, low-latency workloads | Time-series data, IoT telemetry kind of data | Minimum: ~1TB to be cost-effective. Can go up to Petabyte scale | Wiresafe-Online to encrypt sensitive values | Consistent sub-10ms latency, scales linearly with nodes |
| AlloyDB | Fully managed PostgreSQL-compatible database service | Enterprise workloads requiring PostgreSQL compatibility with enhanced performance | Transactional Processing | Databases in the 100GB to 10TB+ range | | Column Store Engine, Vectorized Query Execution, Scale-Out Read Capabilities |
| Memorystore | In-memory datastore | Caching, session storage | Application acceleration, real-time leaderboards, session management | Minimum: 1GB. Up to 300GB (Redis) | Wire safe-Online to encrypt sensitive values | Redis and Memcached support, sub-millisecond latency |

## Exemption Process

Teams believing their use case should be exempt from using this platform must submit a formal architecture exception request to the Enterprise Architecture Review Board, including:
- Detailed technical requirements not met by the platform
- Proposed alternative solution with comprehensive security and governance controls
- Cost-benefit analysis justifying the alternative approach
- Migration path to eventually adopt the enterprise platform
