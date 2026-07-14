def build_rag_prompt(
    user_question: str,
    retrieved_chunks: list[dict],
    kpi_summary: dict = None,
) -> str:
    """
    Build a structured prompt for Grok using:
    - The user's business question
    - Relevant chunks retrieved from Pinecone
    - Optional KPI summary for extra context
    """

    # Format retrieved chunks as readable context
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        text        = chunk.get("text", "")
        chunk_type  = chunk.get("chunk_type", "")
        period      = chunk.get("period", "")
        score       = chunk.get("score", 0)

        label = f"[Context {i}"
        if chunk_type:
            label += f" — {chunk_type}"
        if period:
            label += f" ({period})"
        label += f" | relevance: {score}]"

        context_parts.append(f"{label}\n{text}")

    context_block = "\n\n".join(context_parts)

    # Optional KPI block
    kpi_block = ""
    if kpi_summary:
        kpi_lines = []
        for key, val in kpi_summary.items():
            if key == "monthly_trend":
                continue          # too long, already in chunks
            kpi_lines.append(f"  - {key}: {val}")
        kpi_block = "\nKey business metrics:\n" + "\n".join(kpi_lines)

    prompt = f"""You are a senior business intelligence advisor helping a small business owner understand their data.

The business owner has uploaded their {kpi_summary.get('file_type', 'business') if kpi_summary else 'business'} data and asked:

QUESTION: {user_question}

Below is the most relevant data retrieved from their business records:

{context_block}
{kpi_block}

Based on the above data, provide:
1. A direct answer to their question in simple language
2. Key insight or pattern you noticed
3. One specific actionable recommendation with expected impact
4. Any risk or warning they should be aware of

Keep your response concise, professional, and focused on practical business decisions.
Do not make up numbers that are not in the context above."""

    return prompt


def build_general_insights_prompt(kpi_summary: dict) -> str:
    """
    Build a prompt for general business health analysis
    when user hasn't asked a specific question.
    """

    file_type    = kpi_summary.get("file_type", "business")
    total_amount = kpi_summary.get("total_amount", "N/A")
    avg_amount   = kpi_summary.get("average_amount", "N/A")
    top_category = kpi_summary.get("top_category", "N/A")
    stores       = kpi_summary.get("unique_stores", "N/A")
    customers    = kpi_summary.get("unique_customers", "N/A")

    # Build monthly trend summary
    monthly = kpi_summary.get("monthly_trend", [])
    trend_summary = ""
    if monthly:
        values    = [m["value"] for m in monthly]
        peak      = max(monthly, key=lambda x: x["value"])
        lowest    = min(monthly, key=lambda x: x["value"])
        trend_summary = (
            f"Monthly data spans {len(monthly)} months. "
            f"Peak month: {peak['month']} with value {peak['value']:,.2f}. "
            f"Lowest month: {lowest['month']} with value {lowest['value']:,.2f}."
        )

    prompt = f"""You are a senior business intelligence advisor.

Analyze the following {file_type} business data and provide a strategic report:

Business Overview:
- File type: {file_type}
- Total amount: {total_amount}
- Average per record: {avg_amount}
- Top category: {top_category}
- Unique stores: {stores}
- Unique customers: {customers}
- {trend_summary}

Provide:
1. Executive summary (2-3 sentences on overall business health)
2. Top 3 strategic recommendations with estimated ROI impact
3. Risk areas to watch
4. 30-day action plan

Be specific, data-driven, and practical. Address a small business owner directly."""

    return prompt


def build_business_health_check_prompt(kpi_summary: dict, file_count: int) -> str:
    """
    Build a comprehensive Business Health Check prompt across all uploaded datasets.
    Focuses specifically on Strengths, Expense Reduction, Dead Inventory, and Strategic Growth.
    """
    total_amount = kpi_summary.get("total_amount", "N/A")
    avg_amount = kpi_summary.get("average_amount", "N/A")
    top_category = kpi_summary.get("top_category", "N/A")
    stores = kpi_summary.get("unique_stores", "N/A")
    customers = kpi_summary.get("unique_customers", "N/A")
    total_orders = kpi_summary.get("total_orders", "N/A")

    monthly = kpi_summary.get("monthly_trend", [])
    trend_summary = ""
    if monthly:
        peak = max(monthly, key=lambda x: x["value"])
        lowest = min(monthly, key=lambda x: x["value"])
        trend_summary = (
            f"Monthly revenue spans {len(monthly)} periods. "
            f"Peak: {peak['month']} ({peak['value']:,.2f}), Lowest: {lowest['month']} ({lowest['value']:,.2f})."
        )

    prompt = f"""You are an elite Chief Financial Officer (CFO) & AI Business Strategist analyzing data combined across {file_count} uploaded workspace datasets.

Combined Workspace KPIs:
- Total Volume / Revenue: {total_amount}
- Average Transaction Value: {avg_amount}
- Total Transactions / Orders: {total_orders}
- Top Performing Category: {top_category}
- Unique Customers: {customers}
- {trend_summary}

Please generate a comprehensive, highly structured Business Health Check report covering exactly these sections:
1. **Executive Health Summary & Score**: Overall assessment of the business trajectory.
2. **Key Business Strengths**: Where the business is excelling (top revenue drivers, customer loyalty, volume).
3. **Expense & Margin Reduction Opportunities**: Specific areas where operational costs or low-margin activities can be cut to boost profit.
4. **Dead / Slow-Moving Inventory & Idle Assets**: Analysis of underperforming categories, idle resources, or stagnant inventory tying up working capital.
5. **Immediate 30-Day Growth Roadmap**: Concise action steps to capitalize on strengths and eliminate waste.

Format your report cleanly using markdown bullet points and bold headers."""

    return prompt