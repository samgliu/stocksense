from app.ai.gemini_model import generate_analysis


async def analyze_stock(text: str) -> str:
    prompt = f"""
    You are a professional financial analyst assistant.

    Analyze the following stock-related content and return your insights in a clear, structured format. The goal is to extract meaningful information and summarize the content for an investor audience.

    ---
    ### Instructions:
    - Focus on the company's financial performance
    - Identify growth drivers or strategic highlights
    - Note any potential risks or red flags
    - Highlight any opportunities or upcoming catalysts
    - Avoid repeating the original content verbatim

    ---
    ### Input:
    {text}

    ---
    ### Output Format (Markdown):

    **📌 Summary:**  
    _A brief overview of what this content is about._

    **📈 Financial Performance:**  
    _Comment on earnings, revenue, profit, margins, etc._

    **⚠️ Risks:**  
    _List specific risk factors, uncertainties, or market concerns._

    **🌱 Opportunities:**  
    _What could drive growth or improvement going forward._

    **💡 Analyst Insight (Optional):**  
    _Add a final comment or recommendation if relevant._
    """
    return await generate_analysis(prompt)
