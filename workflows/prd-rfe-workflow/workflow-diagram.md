```mermaid
flowchart LR
    GD[(Google Drive)] -.-> A
    UXR[(UXR MCP)] -.-> A
    UF[(User-uploaded files)] -.-> A
    CODE[(Code)] -.-> A
    
    A[prd.discover] --> REQ[prd.rfe]
    REQ --> review_loop
    
    subgraph review_loop["PRD Review Loop"]
        B[prd.create] --> C[prd.review]
        C --> D[prd.revise]
        D --> B
    end
    
    subgraph feature_loop["Feature Review Loop"]
        E[feature.breakdown] --> F[feature.review]
        F --> G[feature.revise]
        G --> E
    end

    review_loop --> feature_loop
    feature_loop --> PRIO[feature.prioritize]
    PRIO --> H[feature.submit]
    H -.-> JIRA[Jira]
    
    style GD fill:#999,stroke:#666,color:#fff
    style UXR fill:#999,stroke:#666,color:#fff
    style UF fill:#999,stroke:#666,color:#fff
    style CODE fill:#999,stroke:#666,color:#fff
    style JIRA fill:#999,stroke:#666,color:#fff
```

