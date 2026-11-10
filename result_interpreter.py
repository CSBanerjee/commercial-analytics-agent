from llm_client import LLMClient


class ResultInterpreter:

    def __init__(self):
        self.llm = LLMClient()

    def interpret_result(self, business_question, execution_result):

        # Check whether Python execution was successful
        if execution_result["status"] != "success":

            return (
                "Unable to complete the analysis. "
                f"Execution error: {execution_result['error']}"
            )

        # Extract the analytical result
        analysis_result = execution_result["result"]

        prompt = f"""
        You are a commercial analytics business analyst.

        Your task is to explain the analytical result
        in simple business language.

        BUSINESS QUESTION:
        {business_question}

        ANALYTICAL RESULT:
        {analysis_result}

        INSTRUCTIONS:

        1. Answer the original business question directly.
        2. Use only the information provided in the analytical result.
        3. Do not invent numbers or additional findings.
        4. Preserve the units and currency.
        5. Highlight the important KPIs.
        6. Keep the response concise and business-focused.
        7. Do not include Python code.

        Provide the final business answer.
        """

        final_answer = self.llm.generate_response(prompt)

        return final_answer.strip()