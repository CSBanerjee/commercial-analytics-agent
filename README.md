![Uploading Commercial Analytics Agent Blueprint.png…]()

# Commercial Analytics Agent

An educational, portfolio-oriented Agentic AI project that answers commercial sales questions using an LLM, RAG-based KPI retrieval, generated Python analytics code, and controlled execution in Docker.

**Project status: Version 1 core implementation completed and demonstrated.** The application has successfully answered overall sales attainment and regional sales attainment questions end to end. This is a learning and portfolio project, not a production-hardened analytics platform.

## 1. Business problem

Commercial teams need to ask questions in natural language, such as:

- What is our overall sales target attainment?
- Which region had the lowest sales target attainment?
- Which product generated the highest sales?
- What is the sales gap for a particular region?

The agent retrieves relevant business KPI definitions, generates Python code to analyze the approved dataset, executes that code in a Docker environment, and presents the result in business-friendly language.

The current synthetic dataset supports descriptive sales analysis. It does **not** establish the causes of sales performance. Root-cause questions may require opportunity history, win/loss data, sales activities, funnel conversion, pricing, or territory changes.

## 2. Implemented workflow

```text
Business question
       |
       v
Retrieve relevant KPI definitions (RAG)
       |
       v
Generate Python analytics code (LLM)
       |
       v
Validate generated code
       |
       v
Execute code in Docker
       |
       +---- Execution succeeds ----> Interpret result ----> Business answer
       |
       +---- Execution fails -------> Correct code (LLM)
                                           |
                                           v
                                      Validate again
```

The correction loop is bounded by a maximum retry count. The workflow uses LangGraph to manage state, nodes, and conditional routing.

## 3. Technology stack

| Technology | Purpose |
|---|---|
| Python | Application logic and analytics |
| OpenAI API | Code generation, code correction, result interpretation, and embeddings |
| LangGraph | Stateful workflow orchestration and conditional routing |
| LangChain ecosystem | Supporting LLM integration |
| Pandas | CSV-based data analysis |
| NumPy | Embedding similarity calculations |
| OpenAI `text-embedding-3-small` | KPI text and question embeddings |
| Docker | Isolated execution environment for generated Python |
| `uv` | Python environment and dependency management |

The application uses the OpenAI model configured in `llm_client.py`. The embedding model is `text-embedding-3-small`.

## 4. Dataset

**File:** `commercial_sales_data_usd.csv`

The synthetic dataset contains 180 records covering 12 months of 2025, five regions, and three products.

| Column | Meaning |
|---|---|
| `month` | Sales month in `YYYY-MM` format |
| `region` | Sales region |
| `product` | Product category |
| `actual_sales_usd` | Actual sales value in USD |
| `sales_target_usd` | Sales target in USD |
| `pipeline_value_usd` | Potential sales opportunity value in USD |
| `units_sold` | Units sold |

**Dataset grain:** One record represents one month × region × product combination. Expected coverage is 12 × 5 × 3 = 180 records.

### Reference KPI results

These values are reference checks calculated from the current sample dataset. The agent should calculate results from the CSV at runtime rather than use hardcoded answers.

| KPI | Reference result |
|---|---:|
| Total actual sales | $183,825,577.50 |
| Total sales target | $194,503,674.00 |
| Overall sales target attainment | 94.51% |
| Sales shortfall (`target - actual`) | $10,678,096.50 |
| Total pipeline value | $173,051,135.47 |
| Lowest-attainment region | West |
| West sales target attainment | 90.97% |

### KPI definitions

- **Actual sales:** Sum of `actual_sales_usd`.
- **Sales target:** Sum of `sales_target_usd`.
- **Sales target attainment:** `sum(actual_sales_usd) / sum(sales_target_usd) * 100`.
- **Sales gap / shortfall:** `sum(sales_target_usd) - sum(actual_sales_usd)`. A positive value means below target; a negative value means above target.
- **Pipeline value:** Sum of `pipeline_value_usd`. It represents potential opportunity value, not booked or achieved revenue.
- **Units sold:** Sum of `units_sold`.

For overall or grouped attainment, calculate the ratio of summed actual sales to summed target sales. Do not average row-level attainment percentages unless that is the explicitly approved business definition.

## 5. RAG knowledge base

The KPI guide is maintained in `commercial_kpi_guide.txt`.

The RAG preparation and retrieval files are:

| File | Responsibility |
|---|---|
| `commercial_kpi_guide.txt` | Source KPI definitions and business rules |
| `rag_chunking.py` | Splits the KPI guide into text chunks |
| `rag_chunks.json` | Stores the generated chunks |
| `rag_retriever.py` | Creates embeddings and retrieves relevant chunks using cosine similarity |

The retrieved KPI context is supplied to both code generation and code correction. If retrieval fails, the workflow currently continues with empty KPI context and logs a warning.

To regenerate the chunks after editing the KPI guide:

```bash
python3 rag_chunking.py
```

## 6. Project structure

```text
commercial_analytics_agent/
├── app.py                          # Command-line application entry point
├── analytics_graph.py              # LangGraph workflow and nodes
├── agent_state.py                  # Shared workflow state
├── code_generator.py               # Python code generation and correction
├── python_executor.py              # Docker-based Python execution
├── result_interpreter.py            # Business-friendly result interpretation
├── llm_client.py                   # OpenAI client configuration
├── dataset_metadata.py              # Dataset schema and metadata
├── rag_retriever.py                 # KPI embedding and retrieval
├── rag_chunking.py                  # KPI guide chunking
├── commercial_sales_data_usd.csv    # Synthetic sales dataset
├── commercial_kpi_guide.txt         # KPI knowledge base
├── rag_chunks.json                  # Generated RAG chunks
├── Dockerfile                       # Docker execution environment
├── requirements.txt                 # Python dependencies
├── pyproject.toml                   # Project configuration
├── uv.lock                          # Locked dependency versions
├── .python-version                  # Python version configuration
├── .env                             # Local API credentials; do not commit
├── .gitignore                       # Git exclusions
└── README.md
```

## 7. Setup and running

### Prerequisites

- macOS, Linux, or another supported Python environment
- Python version configured for the project
- `uv`
- Docker Desktop or a working Docker Engine
- An OpenAI API key

### Install dependencies

From the project directory:

```bash
uv pip install -r requirements.txt
```

Ensure Docker is running before launching the application because Python analytics code is executed through Docker.

### Configure the API key

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_api_key_here
```

The application loads this key through `llm_client.py`.

**Never commit `.env` or expose a real API key in source code, screenshots, logs, or documentation.** Confirm `.env` is listed in `.gitignore`.

### Run the application

```bash
python3 app.py
```

Enter a business question when prompted. Type `exit` to close the application.

## 8. Example questions

The following questions are suitable for the current dataset:

1. What are total actual sales and total sales target?
2. What is the overall sales target attainment percentage for 2025?
3. Which region had the lowest sales target attainment in 2025?
4. Rank products by actual sales.
5. Show monthly actual sales for the West region.
6. Compare North and West by actual sales and attainment.
7. What was the quarter-over-quarter change in actual sales in 2025?
8. Which region has pipeline value greater than actual sales?

The dataset contains 2025 only, so it cannot support a comparison against 2024. It also does not contain direct evidence to explain why a region missed its target. The agent should state these limitations rather than invent an answer.

## 9. Validation performed

The following end-to-end questions have been run successfully through the application:

| Test question | Expected result | Observed result |
|---|---:|---:|
| What is the overall sales target attainment percentage for 2025? | 94.51% | 94.51% |
| Which region had the lowest sales target attainment in 2025? | West, 90.97% | West, 90.97% |

During the first test, the code correction path was triggered and the corrected code executed successfully. During the second test, the generated code executed successfully without invoking correction.

These are initial functional demonstrations, not a comprehensive evaluation of accuracy, security, performance, or reliability.

## 10. Security and limitations

- Generated Python is executed through a Docker-based executor rather than directly in the main application process.
- The executor is configured with container restrictions. Review `python_executor.py` and `Dockerfile` before using the project with untrusted code or data.
- Syntax validation with `compile()` checks syntax; it is not a security validation mechanism.
- Container isolation reduces risk but should not be described as a complete production security guarantee.
- The sample dataset supports descriptive analysis, not causal diagnosis or forecasting.
- RAG retrieval quality depends on the content and granularity of the KPI guide.
- The current application is a command-line interface. A Streamlit interface, SQL/warehouse connectivity, broader automated evaluation, and production deployment are not part of this Version 1 implementation.

## 11. Development principles

- Use Python and Pandas for deterministic numerical calculations.
- Use the LLM for interpreting questions, generating analytical code, correcting failures, and explaining results.
- Ground KPI calculations in the documented business definitions.
- Do not hardcode calculated answers into prompts.
- Validate generated code and execution results before interpreting them.
- Keep the workflow bounded with controlled retries.
- Distinguish descriptive findings from causal explanations.
- Keep documentation aligned with what is actually implemented.

## 12. Future enhancements

Potential future improvements, outside the completed Version 1 scope:

- Streamlit user interface.
- Automated regression and evaluation suite.
- Stronger execution policy and security review.
- SQL connectivity to an approved data warehouse.
- Additional datasets for pipeline conversion and root-cause analysis.
- Observability for latency, token usage, and model cost.

---

**Version 1 milestone:** The core command-line Commercial Analytics Agent, including RAG-based KPI retrieval, LLM-generated Python analytics, Docker execution, LangGraph orchestration, bounded code correction, and business-friendly result interpretation, has been implemented and demonstrated with the sample dataset.
