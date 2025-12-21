# Datathon 2025: Winning Presentation Structure (10 Slides Max)

**Objective:** Secure "Exceptional" scores (17-20 points) in all categories by demonstrating deep critical thinking, innovative visualization, technical mastery, and transformative recommendations.

**Format:** PDF, Landscape, 16:9 Aspect Ratio.
**Length:** Strictly 10 Pages (Cover + 9 Content Slides).

---

## Slide 1: Title & Vision
**Goal:** Professional first impression.
*   **Big Title:** Datathon 2025: Cash Flow Intelligence & Strategic Volatility Management
*   **Subtitle:** Hybrid Ensemble Forecasting, Deep Anomaly Detection, and Actionable Treasury Insights.
*   **Team Name:** [Random Forest]
*   **Visual:** A subtle, high-quality background graphic hinting at data flow or financial stability (AstraZeneca branding colors).

## Slide 2: Executive Summary (The "Hook")
**Goal:** Tell the whole story in 30 seconds.
*   **The Challenge:** Managing multi-entity cash flow visibility amidst market volatility and billing complexities.
*   **Our Solution:** A "Cash Flow Command Center" leveraging a **Hybrid Ensemble Model (Prophet + XGBoost/RF)** for predictions and **Isolation Forests** for anomaly detection.
*   **Key Impact:**
    *   **Accuracy:** Robust short-term (1-month) and medium-term (6-month) forecasts.
    *   **Risk Mitigation:** Automatically flagged top 1% volume anomalies ($X value detected).
    *   **Strategic Value:** Unlocked actionable insights for short-term liquidity and long-term sustainability.

## Slide 3: Problem Statement & Strategic Context (Data Storytelling: 30%)
**Goal:** Demonstrate "Exceptional" deep critical thinking. Connect to larger financial contexts.
*   **Headline:** The Cost of Volatility: From Reactive to Proactive Treasury.
*   **Content:**
    *   Identify the core friction: "Static reporting fails to capture the dynamic nature of global billing cycles and volatility thresholds."
    *   **The "Why":** Explain *implications*—poor visibility leads to inefficient capital allocation and liquidity risk.
    *   **Strategic Alignment:** Map our objectives (Forecast, Detect, Analyze) directly to AstraZeneca's goal of financial robustness.
*   **Visual:** A conceptual diagram connecting "Raw Data Chaos" to "Strategic Clarity."

## Slide 4: Data Engineering & Technical Architecture (Technical: 40%)
**Goal:** Show "Exceptional" attention to detail and innovative preprocessing (Ref: `clean_data.py`).
*   **Headline:** Robust Data Pipeline & Feature Engineering.
*   **Key Technical Highlights:**
    *   **Preprocessing:** Strict fiscal week alignment (`%Y-%U`), standardized date parsing, and missing value handling for Multi-Entity consistency.
    *   **Feature Engineering:**
        *   **Time-Series Lags:** Generated Lag-1 to Lag-12 features to capture weekly seasonality.
        *   **Rolling Statistics:** Implemented Rolling Mean (4-week) and Rolling Std Dev (4-week) to smooth variance and capture recent trends.
    *   **Transformation:** Conversion of all amounts to standardized **Amount_USD** for global aggregation.
*   **Visual:** A clean, professional "Data Pipeline" flowchart (Source $\rightarrow$ Transform/Lag Generation $\rightarrow$ Ensemble Model $\rightarrow$ Dashboard).

## Slide 5: Market Dynamics & Volatility Analysis (Visualization: 30%)
**Goal:** "Highly innovative and impactful visualizations connecting multiple aspects."
*   **Headline:** Deciphering Volatility: Trends & Factor Impact.
*   **Visual Focus (CRITICAL):**
    *   **Market Trend Overlay:** Visualizing `Amount_USD` movement over `Fiscal_Week` with volatility bands.
    *   **Insight:** Use callouts to highlight specific "Volatility Clusters"—periods of high instability detected by rolling standard deviation spikes.
    *   **Correlation Matrix:** A heatmap showing how specific `Category` flows correlate with `Net Cash Position`.

## Slide 6: Forecasting Engine: 1-Month & 6-Month (Technical: 40%)
**Goal:** "Cutting-edge technical solutions" and "Advanced techniques" (Ref: `cash_flow_analysis.py`).
*   **Headline:** Precision Forecasting: Hybrid Ensemble Approach.
*   **Methodology:**
    *   **Component 1 (Seasonality):** **Facebook Prophet** (`weekly_seasonality=True`, `yearly_seasonality=True`) to capture core cyclical patterns.
    *   **Component 2 (Non-Linear Dynamics):** **XGBoost (n=100, lr=0.05)** & **Random Forest (n=100)** to capture complex non-linear relationships and interactions.
    *   **Consolidation:** Weighted ensemble forecast for superior robustness.
*   **Execution:**
    *   **1-Month Horizon:** Tactical, high-precision liquidity view.
    *   **6-Month Horizon:** Strategic trend analysis using recursive multi-step forecasting.
*   **Validation:** RMSE and MAPE metrics presented for train/test splits.

## Slide 7: Factor Analysis & Trading Insights (Visualization: 30%)
**Goal:** "Mastery of visualization tools and storytelling."
*   **Headline:** Actionable Drivers: Efficiency Gap & Burn Analysis.
*   **Visual Focus (CRITICAL):**
    *   **Efficiency Gap Chart:** Filled area chart highlighting the surplus/deficit between "Cash In" vs "Cash Out" (Green/Red regions).
    *   **Burn vs Budget:** Line/Bar combo comparing actual burn rate vs projected budget thresholds.
*   **Insight:** "Category [X] accounts for Y% of monthly variance, signaling a need for renegotiated payment terms."

## Slide 8: Anomaly Detection & Risk Signals (Technical: 40%)
**Goal:** "Identify irregularities cashflow activities that requires business review."
*   **Headline:** Automated Risk Sentinel: Isolation Forest.
*   **Technique:** **Isolation Forest Algorithm** (`contamination=0.01`).
    *   Unsupervised learning to detect outliers in high-dimensional space without labeled data.
*   **Showcase:**
    *   **Scatter Plot:** "Normal" transactions (Blue) vs "Anomalies" (Red) based on `Amount_USD` and frequency.
    *   **Red Flag Reporting:** Alerting on specific outliers (e.g., single transactions > 3 $\sigma$ from mean).
*   **Triage Protocol:** Automated flagging $\rightarrow$ Finance Analyst Review $\rightarrow$ Investigation.

## Slide 9: Strategic Recommendations (Recommendation: 20%)
**Goal:** "Transformative recommendations defining strategies."
*   **Headline:** From Insight to Impact: Optimizing Liquidity.
*   **Recommendation 1 (Liquidity):** "Leverage 1-Month Prophet forecasts to optimize heavy AP runs during projected surplus weeks."
*   **Recommendation 2 (Operations):** "Investigate anomalies flagged by Isolation Forest in the 'Other' category to plug leakage."
*   **Recommendation 3 (Strategic):** "Adopt the 6-Month Hybrid Forecast as the baseline for medium-term treasury hedging strategies."

## Slide 10: Conclusion & Future Roadmap
**Goal:** Leave a lasting impression of "Exceptional" value.
*   **Summary:** We delivered clarity via **Ensemble Forecasting**, accuracy via **Feature Engineering**, and protection via **Isolation Forest Anomaly Detection**.
*   **The Future (Scalability):**
    *   Integration with real-time banking APIs.
    *   Automated causal analysis using GenAI summaries.
*   **Final Call to Action:** "Empowering AstraZeneca to trade volatility for stability with AI-driven intelligence."
*   **Contact/Team Info.**

---

**Note:** Ensure all charts use the **AstraZeneca color palette** (or a professional, complementary scheme) and are readable when exported to PDF.
