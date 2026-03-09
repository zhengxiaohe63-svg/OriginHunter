# OriginHunter

OriginHunter is a lightweight research tool for **service node
similarity auditing**.

It analyzes candidate service nodes and compares them with a target
service using multiple observable fingerprints, including:

-   HTTP response characteristics
-   Page title and body similarity
-   HTTP headers
-   TLS certificate profiles
-   Favicon hash
-   Content length patterns
-   Infrastructure signals

The tool produces **similarity scores, node classifications, and cluster
analysis** to help researchers understand infrastructure relationships
between service nodes.

OriginHunter does **not attempt to identify or confirm origin
servers**.\
Similarity scores indicate **evidence consistency**, not backend
identity.

------------------------------------------------------------------------

# Key Features

## Multi‑signal similarity analysis

OriginHunter evaluates multiple observable signals:

-   HTTP body similarity
-   HTTP header similarity
-   TLS certificate SAN comparison
-   Favicon hash matching
-   Content length similarity
-   Source evidence scoring

This provides a **more robust similarity model** than simple fingerprint
matching.

------------------------------------------------------------------------

## Transparent scoring model

The tool provides **explainable scoring output**, including:

-   Similarity score
-   Context score
-   Evidence confidence
-   Edge risk assessment
-   Explanation of contributing factors

Example output:

    Why:
    + High body similarity with target
    + Header similarity with target
    + Similar content length
    + Candidate certificate SAN overlaps target SAN set

------------------------------------------------------------------------

## Node classification

Instead of attempting to determine origin servers, OriginHunter
classifies nodes by **service similarity level**:

-   `high_similarity_service_node`
-   `related_service_node`
-   `weakly_related_node`
-   `likely_edge_node`
-   `unreachable_node`

This classification reflects **observable service behavior**, not
infrastructure ownership.

------------------------------------------------------------------------

## Node clustering

OriginHunter groups similar nodes into clusters based on shared
characteristics:

-   body similarity
-   header similarity
-   TLS traits
-   favicon hash
-   classification type

Cluster example:

    Cluster ID: 1
    Node Type: high_similarity_service_node
    Member Count: 4
    Members:
    - 110.242.74.102
    - 111.63.65.103
    - 111.63.65.247
    - 124.237.177.164

Clusters help researchers understand **service node pools** instead of
over‑interpreting individual rankings.

------------------------------------------------------------------------

# Important Disclaimer

OriginHunter is designed for **research and authorized infrastructure
analysis only**.

The tool:

-   does **not bypass CDN protection**
-   does **not identify origin servers**
-   does **not perform intrusive scanning**
-   does **not exploit vulnerabilities**

Similarity scores represent **observable service resemblance**, not
backend confirmation.

Always ensure you have **authorization to analyze target assets**.

------------------------------------------------------------------------

# Installation

Clone the repository:

    git clone https://github.com/yourname/originhunter.git
    cd originhunter

Install dependencies:

    pip install -r requirements.txt

------------------------------------------------------------------------

# Usage

Basic example:

    python cli.py --target example.com

Analyze additional candidate nodes:

    python cli.py --target example.com --candidates 1.2.3.4 5.6.7.8

Resolve common subdomains:

    python cli.py --target example.com --subdomains

Export JSON report:

    python cli.py --target example.com --subdomains --json-out report.json

------------------------------------------------------------------------

# Example Output

    Service Node Similarity Audit

    Top Ranked Service Node:
    IP: 110.242.74.102
    Similarity Score: 54.0
    Evidence Confidence: medium
    Service Node Type: high_similarity_service_node

    Clusters:
    Cluster 1
    Members: 4
    Shared Traits: similar page body, similar headers, similar TLS profile

------------------------------------------------------------------------

# Project Structure

    originhunter/
    │
    ├─ cli.py
    ├─ requirements.txt
    │
    ├─ core/
    │  ├─ analyzer.py
    │  ├─ collector.py
    │  ├─ scorer.py
    │  └─ reporter.py
    │
    ├─ modules/
    │  ├─ dns_resolver.py
    │  ├─ http_fetcher.py
    │  ├─ tls_checker.py
    │  ├─ favicon.py
    │  ├─ fingerprint.py
    │  ├─ similarity.py
    │  ├─ node_classifier.py
    │  └─ asn_checker.py
    │
    └─ utils/
       ├─ hashing.py
       ├─ normalize.py
       └─ json_writer.py

------------------------------------------------------------------------

# Use Cases

OriginHunter can be useful for:

-   infrastructure research
-   service fingerprint comparison
-   node similarity clustering
-   security research labs
-   authorized asset analysis

------------------------------------------------------------------------

# Limitations

OriginHunter intentionally avoids making claims about:

-   origin server identification
-   backend infrastructure discovery
-   CDN bypass techniques

The tool focuses only on **observable similarity signals**.

------------------------------------------------------------------------

# License

MIT License
