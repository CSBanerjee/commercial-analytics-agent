from langgraph.graph import StateGraph, START, END

from agent_state import AgentState
from code_generator import CodeGenerator
from python_executor import PythonExecutor
from result_interpreter import ResultInterpreter
from rag_retriever import RAGRetriever


# Maximum number of code correction attempts
MAX_RETRIES = 2


# Initialize components
code_generator = CodeGenerator()
python_executor = PythonExecutor()
result_interpreter = ResultInterpreter()
rag_retriever = RAGRetriever()


# NODE 0: Retrieve relevant KPI definitions
def retrieve_kpi_context_node(state: AgentState):

    print("\nRetrieving relevant KPI definitions...")

    try:
        kpi_context = rag_retriever.retrieve(
            state["business_question"],
            top_k=2
        )

        return {
            "kpi_context": kpi_context,
            "error": None
        }

    except Exception as e:
        print(f"RAG retrieval warning: {str(e)}")

        return {
            "kpi_context": "",
            "error": None
        }


# NODE 1: Generate Python code
def generate_code_node(state: AgentState):

    print("\nGenerating Python code...")

    try:
        generated_code = code_generator.generate_code(
            state["business_question"],
            state.get("kpi_context", "")
        )

        return {
            "generated_code": generated_code,
            "error": None
        }

    except Exception as e:
        return {
            "generated_code": None,
            "error": f"Code generation failed: {str(e)}"
        }


# NODE 2: Validate generated Python code
def validate_code_node(state: AgentState):

    generated_code = state.get("generated_code")

    if not generated_code:
        return {
            "validation_status": "failed",
            "error": state.get("error") or "No code generated."
        }

    try:
        compile(generated_code, "<generated_code>", "exec")

        return {
            "validation_status": "passed",
            "error": None
        }

    except SyntaxError as e:
        return {
            "validation_status": "failed",
            "error": f"Syntax error: {str(e)}"
        }


# NODE 3: Execute Python code inside Docker
def execute_code_node(state: AgentState):

    print("\nExecuting Python code...")

    try:
        execution_result = python_executor.execute(
            state["generated_code"]
        )

        return {
            "execution_result": execution_result,
            "error": execution_result.get("error")
        }

    except Exception as e:
        return {
            "execution_result": None,
            "error": f"Execution failed: {str(e)}"
        }


# NODE 4: Interpret analytical result
def interpret_result_node(state: AgentState):

    print("\nInterpreting analytical results...")

    try:
        final_answer = result_interpreter.interpret_result(
            state["business_question"],
            state["execution_result"]
        )

        return {
            "final_answer": final_answer,
            "error": None
        }

    except Exception as e:
        return {
            "final_answer": None,
            "error": f"Result interpretation failed: {str(e)}"
        }


# NODE 5: Correct generated Python code
def correct_code_node(state: AgentState):

    print("\nCorrecting generated code...")

    try:
        corrected_code = code_generator.correct_code(
            business_question=state["business_question"],
            generated_code=state["generated_code"],
            error_feedback=state["error"],
            kpi_context=state.get("kpi_context", "")
        )

        return {
            "generated_code": corrected_code,
            "retry_count": state["retry_count"] + 1,
            "error": None,
            "validation_status": None,
            "execution_result": None
        }

    except Exception as e:
        return {
            "retry_count": state["retry_count"] + 1,
            "error": f"Code correction failed: {str(e)}",
            "validation_status": "failed",
            "execution_result": {
                "status": "error",
                "error": str(e)
            }
        }


# ROUTING 1: After code validation
def route_after_validation(state: AgentState):

    if state["validation_status"] == "passed":
        return "execute_code"

    if state["retry_count"] < MAX_RETRIES:
        return "correct_code"

    return "end"


# ROUTING 2: After code execution
def route_after_execution(state: AgentState):

    execution_result = state.get("execution_result")

    if execution_result and execution_result.get("status") == "success":
        return "interpret_result"

    if state["retry_count"] < MAX_RETRIES:
        return "correct_code"

    return "end"


# BUILD LANGGRAPH WORKFLOW
def build_analytics_graph():

    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("retrieve_kpi_context", retrieve_kpi_context_node)
    workflow.add_node("generate_code", generate_code_node)
    workflow.add_node("validate_code", validate_code_node)
    workflow.add_node("correct_code", correct_code_node)
    workflow.add_node("execute_code", execute_code_node)
    workflow.add_node("interpret_result", interpret_result_node)

    # Initial workflow
    workflow.add_edge(START, "retrieve_kpi_context")
    workflow.add_edge("retrieve_kpi_context", "generate_code")
    workflow.add_edge("generate_code", "validate_code")

    # Route after validation
    workflow.add_conditional_edges(
        "validate_code",
        route_after_validation,
        {
            "execute_code": "execute_code",
            "correct_code": "correct_code",
            "end": END
        }
    )

    # Corrected code goes back for validation
    workflow.add_edge("correct_code", "validate_code")

    # Route after execution
    workflow.add_conditional_edges(
        "execute_code",
        route_after_execution,
        {
            "interpret_result": "interpret_result",
            "correct_code": "correct_code",
            "end": END
        }
    )

    # Final answer
    workflow.add_edge("interpret_result", END)

    return workflow.compile()