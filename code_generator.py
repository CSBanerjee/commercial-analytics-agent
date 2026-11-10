from llm_client import LLMClient
from dataset_metadata import dataset_metadata


class CodeGenerator:

    def __init__(self):
        self.llm = LLMClient()

        self.dataset_path = "/sandbox/commercial_sales_data_usd.csv"

        self.dataset_metadata = dataset_metadata

    # Generate Python code using the business question and RAG context
    def generate_code(self, business_question, kpi_context=""):

        prompt = f"""
        You are an expert Python data analyst.

        Your task is to generate Python code to answer
        the supplied business question.

        BUSINESS QUESTION:
        {business_question}

        DATASET METADATA:
        {self.dataset_metadata}

        RELEVANT BUSINESS KPI DEFINITIONS (RETRIEVED USING RAG):
        {kpi_context}

        INSTRUCTIONS:

        1. Use pandas for data analysis.
        2. Load the dataset using:
           pd.read_csv('{self.dataset_path}')
        3. Use only the columns available in the metadata.
        4. Follow the supplied business calculation definitions.
        5. Use retrieved KPI definitions where relevant.
        6. Do not invent missing data or business definitions.
        7. Do not assume columns or relationships that are not provided.
        8. Handle division by zero where applicable.
        9. Print the final analytical result.
        10. Return only executable Python code.
        11. Do not include markdown code fences.
        12. Do not provide explanations outside the code.

        Generate the Python code now.
        """

        generated_code = self.llm.generate_response(prompt)

        return generated_code.strip()

    # Correct Python code when validation or execution fails
    def correct_code(
        self,
        business_question,
        generated_code,
        error_feedback,
        kpi_context=""
    ):

        prompt = f"""
        You are a Python data analytics developer.

        Your task is to correct the previously generated Python code.

        BUSINESS QUESTION:
        {business_question}

        RELEVANT KPI DEFINITIONS:
        {kpi_context}

        PREVIOUSLY GENERATED CODE:
        {generated_code}

        ERROR ENCOUNTERED:
        {error_feedback}

        DATASET:
        The CSV file is available at:
        {self.dataset_path}

        DATASET COLUMNS:
        month, region, product, actual_sales_usd,
        sales_target_usd, pipeline_value_usd, units_sold

        INSTRUCTIONS:

        1. Identify the cause of the error.
        2. Correct the Python code.
        3. Preserve the original business question and analytical intent.
        4. Follow the supplied KPI definitions when relevant.
        5. Use pandas for data analysis.
        6. Print the final analytical result.
        7. Return only executable Python code.
        8. Do not include explanations or Markdown code fences.

        Generate the corrected Python code now.
        """

        corrected_code = self.llm.generate_response(prompt)

        return corrected_code.strip()