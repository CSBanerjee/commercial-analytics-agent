from analytics_graph import build_analytics_graph


class CommercialAnalyticsAgent:

    def __init__(self):
        self.graph = build_analytics_graph()

    def run(self, business_question):

        initial_state = {
            "business_question": business_question,
            "kpi_context": None,
            "generated_code": None,
            "validation_status": None,
            "execution_result": None,
            "final_answer": None,
            "error": None,
            "retry_count": 0
        }

        result = self.graph.invoke(initial_state)

        if result.get("final_answer"):
            return result["final_answer"]

        return (
            "Analysis could not be completed.\n"
            f"Reason: {result.get('error', 'Unknown error')}"
        )


if __name__ == "__main__":

    agent = CommercialAnalyticsAgent()

    print("\n====================================")
    print("   COMMERCIAL ANALYTICS AGENT")
    print("====================================")

    while True:

        question = input(
            "\nEnter your business question (or type 'exit'): "
        ).strip()

        if question.lower() in ["exit", "quit"]:
            print("Exiting Commercial Analytics Agent.")
            break

        if not question:
            print("Please enter a business question.")
            continue

        answer = agent.run(question)

        print("\n====================================")
        print("FINAL BUSINESS ANSWER")
        print("====================================")
        print(answer)