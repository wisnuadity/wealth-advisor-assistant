# Multi-Agent Wealth Advisor Assistant

1. Overview

This project implements a lightweight multi-agent Wealth Advisor Assistant that ingests client financial data, retrieves additional client context through a REST API, performs financial analysis and preliminary anomaly detection, and produces structured outputs to support financial advisor decisions.

The system combines synthetic transaction data stored in JSON, a mock CRM REST API built with Flask, deterministic Python-based financial analysis, and a locally hosted Large Language Model (LLM) through Ollama.

The LLM generates contextual summaries for flagged transactions. It does not determine whether a transaction is anomalous, make financial decisions, or replace human review.

Important: This system provides preliminary financial analysis and decision support. It does not provide personalized investment advice or determine whether a transaction is fraudulent. Flagged transactions require human review.

2. Architecture

#Components

- OrchestratorAgent : Coordinates the workflow, invokes specialized agents, combines results, and handles workflow-level errors.
- DataFetcherAgent : Loads client transaction data from local JSON and retrieves the client profile through the CRM tool.
- FinancialAnalyzerAgent : Calculates income, expenses, net cash flow, expenses by category, and preliminary statistical anomaly flags.
- LLMInsightAgent : Generates contextual summaries for flagged transactions using a local Ollama model. Provides a fallback when summary generation fails.
- CRMTool : Abstracts HTTP communication with the CRM API and handles missing clients and request failures.
- Flask CRM API : Exposes client profiles stored in data/mock_crm.json.
- Human Review Workflow : Allows a reviewer to approve a flag, reject a flag, or override the assessment. Decisions are stored separately from the original analysis.
- main.py : Runs the workflow and saves structured results to JSON.

#Workflow

1. The user starts the application for a client ID.
2. OrchestratorAgent invokes DataFetcherAgent.
3. DataFetcherAgent loads transaction data and requests the client profile through CRMTool.
4. CRMTool retrieves the profile from the Flask CRM API.
5. FinancialAnalyzerAgent calculates financial metrics and flags potentially unusual expenses.
6. LLMInsightAgent generates a contextual summary for each flagged transaction.
7. OrchestratorAgent combines the client context, financial analysis, LLM summaries, and human-review items into structured JSON.
8. The output is saved to outputs/analysis_C001.json.
9. A reviewer can inspect flagged transactions and record decisions through human_review.py.

If LLM summary generation fails, the system uses a fallback summary and retains the original rule-based anomaly information. An LLM failure should not invalidate a successful financial analysis.

#Architecture Diagram

                  User / CLI
                      |
                      v
              OrchestratorAgent
                      |
                      v
               DataFetcherAgent
                 /           \
                v             v
          Local JSON       CRMTool
                              |
                              v
                       Flask CRM API
                              |
                              v
                 FinancialAnalyzerAgent
                              |
                              v
                       LLMInsightAgent
                              |
                       Local Ollama
                       qwen2.5:3b
                              |
                              v
                  Structured JSON Output
                              |
                              v
                       Human Review
                              |
                              v
                  review_decisions.json


3. Project Structure


test_code/
├── agents/
│   ├── __init__.py
│   ├── data_fetcher.py
│   ├── financial_analyzer.py
│   ├── llm_insight.py
│   └── orchestrator.py
├── data/
│   ├── client_financial_data.json
│   └── mock_crm.json
├── tools/
│   ├── __init__.py
│   └── crm_tool.py
├── tests/
│   ├── __init__.py
│   ├── test_crm_tool.py
│   ├── test_financial_analyzer.py
│   ├── test_llm_insight.py
│   └── test_orchestrator.py
├── outputs/
│   ├── analysis_C001.json
│   └── review_decisions.json
├── main.py
├── mock_crm_api.py
├── human_review.py
├── check_data.py
├── test_crm_tool_manual.py
├── test_data_fetcher_manual.py
├── test_financial_analyzer_manual.py
├── test_orchestrator_manual.py
├── test_llm_insight_manual.py
├── requirements.txt
└── README.md


Generated output files are shown as examples. They may not exist until the application has been executed.

4. Requirements

- Python 3.11
- Conda (recommended)
- Ollama
- The qwen2.5:3b model
- Dependencies listed in requirements.txt

#Install Python dependencies

conda create -n wealth-advisor python=3.11 -y
conda activate wealth-advisor
python -m pip install -r requirements.txt


#Install and prepare the local LLM

Install Ollama from:

https://ollama.com/download

Download the model:

ollama pull qwen2.5:3b


Verify the installed model:

ollama list


Ollama must be running and accessible at http://localhost:11434 for local summary generation.

No external LLM API key is required.

5. Run the Application

#Terminal 1: Start the mock CRM API

From the project root:

conda activate wealth-advisor
python mock_crm_api.py

The API runs locally at:

http://127.0.0.1:5000

Keep this terminal open while running the application.

#Terminal 2: Run the assistant

conda activate wealth-advisor
python main.py


To analyze a specific client:

python main.py --client-id C001


To specify a custom output path:

python main.py --client-id C001 --output outputs/my_analysis.json


The default output path is:

outputs/analysis_C001.json

#Optional: Test the LLM agent independently

python test_llm_insight_manual.py


This test checks whether the local model can generate a contextual summary.

6. Sample Results

For the provided synthetic client C001, the application produces the following results:

| Metric | Result |
|---|---:|
| Transactions analyzed | 100 |
| Total income | $30,000.00 |
| Total expenses | $18,694.05 |
| Net cash flow | $11,305.95 |
| Potential anomalies | 3 |
| Human review status | pending |

The current detector flags transactions T020, T078, and T090.

Each flagged transaction includes:

- Transaction ID, date, amount, and category.
- A rule-based reason explaining why it was flagged.
- A contextual summary generated by the local LLM, when available.
- The summary generation status and model name.
- A review requirement indicator.

Example output structure:

json
{
  "transaction_id": "T078",
  "date": "2026-08-14",
  "amount": 4200.0,
  "category": "international_transfer",
  "reason": "Expense amount exceeds the overall mean by 2.0 population standard deviations.",
  "requires_review": true,
  "contextual_summary": "The transaction exceeds the statistical threshold. Verification with the client is recommended.",
  "contextual_summary_status": "generated",
  "contextual_summary_model": "qwen2.5:3b"
}


The summary above is illustrative. Actual LLM-generated text may vary.

7. Anomaly Detection

The FinancialAnalyzerAgent uses a statistical rule to identify unusually large expenses.

An expense is flagged when its amount is greater than: Average expense + (2 × Standard deviation)

Where:
- Expense amount: The amount of the transaction being evaluated.
- Average expense: The average amount of all expenses.
- Standard deviation: A measure of how much expense amounts vary from the average.

The detector runs only when at least five expense transactions are available.

#Limitations

- All expense categories share the same baseline.
- Some unusual transactions may not be detected.
- A flagged transaction is not necessarily fraudulent.
- The detector does not consider the client's spending history or seasonal patterns.
- This is a basic detection method, not a validated fraud detection model.

The anomaly_test_case field is reserved for evaluation and is not used by the detector.

8. LLM Integration and Fallback

The LLMInsightAgent uses Ollama with qwen2.5:3b to generate concise contextual summaries for flagged transactions.

The LLM is responsible for summarization, not for calculating financial metrics or deciding whether a transaction should be flagged.

The prompt instructs the model to:

- Use supplied transaction facts and the rule-based reason.
- Avoid unsupported claims about the transaction's purpose.
- Avoid concluding that a transaction is fraudulent or unauthorized.
- Recommend verification when appropriate.
- Avoid inferring causal relationships between a transaction and financial goals without evidence.

The system records the summary status as:

- generated : A non-empty summary was returned.
- unavailable : Summary generation failed and the fallback was used.

When summary generation fails, the financial analysis and human-review requirement remain available.

LLM outputs are probabilistic and may still contain unsupported interpretations. They should be treated as supporting information and reviewed before being used in advisory decisions.

9. Human-in-the-Loop Review

Run the review workflow after generating the analysis:

bash
python human_review.py


The script reads the analysis output and allows a reviewer to record a decision for each flagged transaction.

Supported decisions include:

- approve_flag : Approve or retain the anomaly flag after review.
- reject_flag : Reject the anomaly flag after review.
- override : Record an alternative assessment.

The reviewer provides an identity and a non-empty review note. The override option also accepts an alternative assessment.

Decisions are saved to:

outputs/review_decisions.json

Each recorded decision includes the transaction ID, client ID, original flag, decision, reviewer note, reviewer identity, and review timestamp. An override may additionally contain the reviewer's alternative assessment.

The original analysis JSON is not modified by the review script. Consequently, the original requires_review field remains a record of the initial analysis rather than the final reviewer decision.

The review script prevents already-reviewed transactions from being processed repeatedly. To test the workflow again, back up the existing review-decision file before resetting test data.

10. Error Handling and Logging

The implementation includes:

- Validation that financial data belongs to the requested client.
- Handling of missing or invalid transaction data.
- CRM handling for missing clients and HTTP request failures.
- Workflow-level error responses from OrchestratorAgent.
- Logging of workflow execution and failures.
- LLM fallback behavior when summary generation fails.
- Separate persistence of human-review decisions.
- Automated tests using mocked dependencies where appropriate.

11. Testing

Run the automated test suite:

bash
python -m pytest tests/ -v


The current test suite contains 11 tests covering:

- CRM retrieval success.
- CRM client-not-found handling.
- CRM API connection failure.
- Cash-flow calculations.
- Expense aggregation by category.
- Detection of an unusually large expense.
- Empty transaction validation.
- LLM summary generation success.
- LLM summary fallback on failure.
- Successful orchestration.
- Orchestrator handling of a data-fetching failure.

The latest verified test run completed with 11 passed.

The automated LLM tests use mocked HTTP responses and do not require Ollama to generate real summaries during the test run. The separate manual LLM test can be used to verify the local model.

12. Design Decisions and Trade-offs

- Deterministic financial analysis: Python-based rules provide reproducibility and explainability for financial calculations and anomaly detection.
- LLM for contextual summaries: A local LLM adds natural-language context without delegating financial calculations or anomaly decisions to a probabilistic model.
- Local inference: Ollama avoids reliance on a paid external LLM API, with the trade-off of local hardware and model latency requirements.
- Flask mock API: Demonstrates API-based context retrieval without requiring external CRM credentials.
- Tool abstraction: CRMTool isolates HTTP communication from the agent workflow.
- JSON storage: Keeps the prototype portable and easy to inspect, but does not provide database-level concurrency or transaction guarantees.
- Human-review checkpoint: Flagged transactions are not automatically treated as fraud or used to trigger financial actions.
- Fallback behavior: Financial analysis remains usable even when contextual summary generation fails.

13. Assumptions and Scope

- The financial and CRM records are synthetic assessment data.
- The application processes one client per run.
- The CRM API is a local mock service, not a production CRM.
- Transaction amounts are non-negative and transaction types use income or expense.
- The anomaly detector does not use the reserved anomaly_test_case evaluation metadata.
- The LLM is used only to generate contextual summaries.
- Human-review decisions are stored separately from the original analysis.
- The system does not execute trades, transfer funds, or make autonomous investment decisions.

