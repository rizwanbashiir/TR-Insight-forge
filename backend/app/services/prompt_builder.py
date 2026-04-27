def build_business_prompt(kpi_data, forecast_data, segmentation_data):
    """
    Build prompt for Grok API
    """

    prompt = f"""
You are a business intelligence advisor.

Analyze the following business data and provide strategic recommendations.

KPI Report:
{kpi_data}

Revenue Forecast:
{forecast_data}

Customer Segmentation:
{segmentation_data}

Provide:
1. Business growth opportunities
2. Customer retention strategies
3. Revenue optimization suggestions
4. Segment-specific recommendations
5. Actionable next steps

Keep recommendations professional and concise.
"""

    return prompt