import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random, string
from io import StringIO

st.set_page_config(page_title="Industry Matching Game", layout="wide")

# ---------- data load ----------
CSV = "https://www.stern.nyu.edu/~adamodar/pc/datasets/wacc.xls"
FALLBACK = """Industry Name,Beta,Cost of Capital,D/(D+E)
Advertising,1.21,7.81,28.67
Aerospace/Defense,0.95,7.6,13.47
Air Transport,1.19,6.72,47.69
Apparel,0.94,7.13,23.83
Auto & Truck,1.46,9.38,16.45
Auto Parts,1.34,8.18,29.31
Bank (Money Center),0.76,4.98,62.15
Banks (Regional),0.4,4.98,34.25
Beverage (Alcoholic),0.81,6.48,30.24
Beverage (Soft),0.64,6.33,17.07
Broadcasting,0.47,5.09,46.19
Brokerage & Investment Banking,1.17,6.08,57.55
Building Materials,1.11,7.85,20.63
Business & Consumer Services,0.89,7.23,16.47
Cable TV,0.74,5.2,59.5
Chemical (Basic),1.01,6.22,49.84
Chemical (Diversified),0.85,5.23,63.78
Chemical (Specialty),0.97,7.25,23.01
Coal & Related Energy,1.07,8.41,6.67
Computer Services,1.09,7.83,20.06
Computers/Peripherals,1.35,9.71,4.42
Construction Supplies,1.15,8.29,14.98
Diversified,0.88,7.3,13.46
Drugs (Biotechnology),1.14,8.49,11.54
Drugs (Pharmaceutical),0.98,7.85,12.69
Education,0.78,6.75,19.6
Electrical Equipment,1.25,8.99,10.72
Electronics (Consumer & Office),0.87,7.63,5.49
Electronics (General),0.97,7.85,9.92
Engineering/Construction,1.21,8.69,12.29
Entertainment,0.83,7.13,13.73
Environmental & Waste Services,0.95,7.43,17.66
Farming/Agriculture,1.13,7.27,34.14
Financial Svcs. (Non-bank & Insurance),0.97,5,73.13
Food Processing,0.61,5.79,30.43
Food Wholesalers,0.87,6.53,31.96
Furn/Home Furnishings,0.82,6.53,29.74
Green & Renewable Energy,0.86,6.04,53.08
Healthcare Products,0.91,7.54,11.34
Healthcare Support Services,0.87,6.83,26.16
Heathcare Information and Technology,1.11,8.22,13.6
Homebuilding,0.91,7.27,17.59
Hospitals/Healthcare Facilities,0.8,6.19,37.47
Hotel/Gaming,1.08,7.36,28.44
Household Products,0.82,7.03,15.36
Information Services,0.92,7,24.91
Insurance (General),0.67,6.34,20.4
Insurance (Life),0.64,5.6,40.42
Insurance (Prop/Cas.),0.48,5.78,12.91
Investments & Asset Management,0.66,6.13,24.64
Machinery,0.96,7.7,12.81
Metals & Mining,1.04,8.2,9.9
Office Equipment & Services,1.33,7.92,32.48
Oil/Gas (Integrated),0.3,5.07,12.16
Oil/Gas (Production and Exploration),0.72,6.25,27.32
Oil/Gas Distribution,0.67,5.78,36.92
Oilfield Svcs/Equip.,0.95,7.04,27.2
Packaging & Container,1.02,6.75,35.53
Paper/Forest Products,0.96,6.93,30.4
Power,0.48,5.01,42.58
Precious Metals,0.84,7.47,6.79
Publishing & Newspapers,0.56,5.95,19.32
R.E.I.T.,0.64,5.32,45.79
Real Estate (Development),0.84,5.82,50.45
Real Estate (General/Diversified),0.81,6.25,34.88
Real Estate (Operations & Services),0.97,7.41,19.77
Recreation,1.02,6.76,38.65
Reinsurance,0.58,5.64,30.3
Restaurant/Dining,0.92,7.16,21.4
Retail (Automotive),0.94,6.78,31.2
Retail (Building Supply),1.54,9.51,18.89
Retail (Distributors),0.95,7.22,22.02
Retail (General),0.81,7.27,7.36
Retail (Grocery and Food),1.12,7.24,34.19
Retail (REITs),0.62,5.57,36.07
Retail (Special Lines),1.09,8.01,16.5
Rubber& Tires,0.53,4.48,78.19
Semiconductor,1.52,10.55,2.53
Semiconductor Equip,1.4,9.89,4.64
Shipbuilding & Marine,0.75,6.69,18.4
Shoe,1.02,8.01,10.67
Software (Entertainment),1.03,8.44,2
Software (Internet),1.69,10.66,10.95
Software (System & Application),1.28,9.34,5.28
Steel,1.06,7.76,19.04
Telecom (Wireless),0.54,5.48,34.19
Telecom. Equipment,0.92,7.72,8.44
Telecom. Services,0.63,5.39,49
Tobacco,0.79,6.94,18.68
Transportation,0.86,6.72,26.71
Transportation (Railroads),0.98,7.27,21.75
Trucking,1.01,7.52,20.15
Utility (General),0.24,4.36,44.9
Utility (Water),0.41,4.93,38.41%"""

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(CSV)
        df = df[["Industry Name", "Beta", "Cost of Capital", "D/(D+E)"]]
        df.columns = ["Industry", "Beta", "WACC", "Debt"]
        df["WACC"] = df["WACC"].str.rstrip("%").astype(float)
        df["Debt"] = df["Debt"].str.rstrip("%").astype(float)
    except Exception:
        df = pd.read_csv(StringIO(FALLBACK))
        df.columns = ["Industry", "Beta", "WACC", "Debt"]
        df["WACC"] = df["WACC"].astype(str).str.rstrip("%").astype(float)
        df["Debt"] = df["Debt"].astype(str).str.rstrip("%").astype(float)
    return df

df_all = load_data()

# ---------- session init ----------
ss = st.session_state
for k, v in [
    ("game_active", False),
    ("game_submitted", False),
    ("df", None),
    ("letters", []),
    ("industries_opts", []),
    ("true_map", {}),
    ("answers", {}),
    ("results", []),
    ("score", 0.0),
]:
    if k not in ss:
        ss[k] = v

# ---------- sidebar ----------
with st.sidebar:
    if not ss.game_active:
        st.markdown("### 🎮 Game Setup")
        n = st.slider("Number of industries", 2, 10, 5)
        st.markdown(f"*Selected: {n} industries*")
        
        if st.button("🚀 Start Game", type="primary", use_container_width=True):
            sample   = df_all.sample(n).reset_index(drop=True)
            letters  = list(string.ascii_uppercase[:n])

            # metric strings in TRUE order
            metrics = []
            for _, r in sample.iterrows():
                beta  = float(r["Beta"])
                wacc  = float(r["WACC"])
                debt  = float(r["Debt"])
                if debt <= 1:          # convert 0–1 ratio to 0–100 %
                    debt *= 100
                metrics.append(
                    f"Beta: {beta:.2f}, Debt%: {debt:.2f}%, WACC: {wacc:.2f}%"
                )

            industries = sample["Industry"].tolist()
            industries_opts = industries.copy()
            random.shuffle(industries_opts)

            ss.df          = sample
            ss.letters     = letters
            ss.industries_opts = industries_opts
            ss.true_map    = {L: industries[i] for i, L in enumerate(letters)}
            ss.answers     = {L: "Select..." for L in letters}

            ss.game_active    = True
            ss.game_submitted = False
            ss.balloons_shown = False  # Reset balloons flag for new game
            
        st.markdown("---")
        st.markdown("### 📖 How to Play")
        st.markdown("""
        1. **Observe** the 3D scatter plot
        2. **Match** each lettered point to its correct industry
        3. **Submit** your answers to see results
        
        **Scoring**: +1 for correct, -0.5 for incorrect
        """)
        
        if ss.game_submitted:
            st.markdown("### 🎯 Latest Score")
            st.metric("Score", f"{ss.score:.1f}/{len(ss.letters)}")
    else:
        st.markdown("### 🎮 Game in Progress")
        completed = sum(1 for v in ss.answers.values() if v != "Select...")
        st.progress(completed / len(ss.letters))
        st.markdown(f"**Progress**: {completed}/{len(ss.letters)} completed")

# ---------- main ----------
st.title("🎯 Industry Matching Game")

# Add a description
with st.expander("ℹ️ About this game", expanded=False):
    st.markdown("""
    This game consists of matching industries with their correct beta, leverage (D/(D+E)) and WACC. 
    
    There are different ways of playing this game. The easiest way is to focus on one metric -- e.g., the beta -- and then rank the industries 
    from the lowest to highest beta. If two industries have very similar betas, consider their other metrics (e.g., leverage). For example, 
    industries that sell basic services and goods are likely to have very low betas. However, such industries may still differ in terms of their leverage.
    For example, more mature industries and those with more tangible assets tend to have greater leverage than younger industries and those with more
    intangibles. This game definitely requires some **detective work**! 🕵️🔍

    The data used in this application are taken from Professor Damodaran's website.
    """)

if ss.game_active:
    df      = ss.df
    letters = ss.letters

    # Add a progress indicator
    progress_text = f"📊 **Round in Progress** | Industries: {len(letters)} | Match the financial metrics to their industries!"
    st.markdown(f"<div style='text-align: center; padding: 10px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 20px;'>{progress_text}</div>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2, gap="medium")

    # graph (left)
    with col_left:
        # Create color scheme based on WACC values
        colors = ['#FF6B6B' if wacc > 9 else '#4ECDC4' if wacc < 7 else '#45B7D1' 
                  for wacc in df["WACC"]]
        
        fig = go.Figure(go.Scatter3d(
            x=df["Beta"], y=df["Debt"], z=df["WACC"],
            text=letters, mode="markers+text", textposition="top center",
            marker=dict(
                size=12,
                color=colors,
                opacity=0.8,
                line=dict(width=2, color='white')
            ),
            textfont=dict(size=14, color='white', family="Arial Black")
        ))
        
        fig.update_layout(
            scene=dict(
                xaxis_title="Beta", 
                yaxis_title="Debt %", 
                zaxis_title="WACC %",
                xaxis=dict(
                    gridcolor='#999999',
                    gridwidth=2,
                    showgrid=True,
                    zeroline=True,
                    zerolinecolor='#333333',
                    zerolinewidth=3,
                    showbackground=True,
                    backgroundcolor='rgba(250,250,250,0.8)'
                ),
                yaxis=dict(
                    gridcolor='#999999',
                    gridwidth=2,
                    showgrid=True,
                    zeroline=True,
                    zerolinecolor='#333333',
                    zerolinewidth=3,
                    showbackground=True,
                    backgroundcolor='rgba(250,250,250,0.8)'
                ),
                zaxis=dict(
                    gridcolor='#999999',
                    gridwidth=2,
                    showgrid=True,
                    zeroline=True,
                    zerolinecolor='#333333',
                    zerolinewidth=3,
                    showbackground=True,
                    backgroundcolor='rgba(250,250,250,0.8)'
                )
            ),
            height=600, 
            margin=dict(l=0, r=0, t=20, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    # dropdowns (right)
    with col_right:
        if not ss.game_submitted:
            st.markdown("### 🎲 Match each metric to its industry")
            st.markdown("*Select the correct industry for each lettered point's Beta, Debt%, and WACC combination.*")
            
            for i, L in enumerate(letters):
                beta  = float(df.at[i, "Beta"])
                wacc  = float(df.at[i, "WACC"])
                debt  = float(df.at[i, "Debt"])
                if debt <= 1:
                    debt *= 100
                metric_display = f"Beta: {beta:.2f}, Debt%: {debt:.2f}%, WACC: {wacc:.2f}%"
                
                current  = ss.answers[L]
                used     = {v for k, v in ss.answers.items() if k != L}
                opts     = ["Select..."] + [
                    ind for ind in ss.industries_opts if ind not in used or ind == current
                ]
                
                # Add emoji indicators based on selection status only
                status_emoji = "🔵" if current != "Select..." else "⚪"
                
                sel = st.selectbox(
                    f"{status_emoji} **Point {L}**: {metric_display}",
                    opts,
                    index=opts.index(current) if current in opts else 0,
                    key=f"sel_{L}"
                )
                ss.answers[L] = sel

            # submit with improved styling
            st.markdown("---")
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button("🚀 Submit Answers", type="primary", use_container_width=True):
                    if "Select..." in ss.answers.values():
                        st.error("⚠️ Complete all selections first.")
                    elif len(set(ss.answers.values())) < len(letters):
                        st.error("⚠️ Each metric combo can be chosen only once.")
                    else:
                        correct = 0
                        results = []
                        for i, L in enumerate(letters):
                            g = ss.answers[L]
                            a = ss.true_map[L]
                            mark = "✅" if g == a else "❌"
                            if mark == "✅":
                                correct += 1
                            results.append((L, df.at[i, "Industry"], a, mark))
                        ss.score   = correct - 0.5 * (len(letters) - correct)
                        ss.results = results
                        ss.game_submitted = True
                        ss.game_active = False  # unlock sidebar immediately
                        st.rerun()

# ---------- results (centered) ----------
if ss.game_submitted:
    lft, ctr, rgt = st.columns([1, 2, 1])
    with ctr:
        # Score display with visual styling
        score_color = "#28a745" if ss.score >= len(ss.letters) * 0.8 else "#ffc107" if ss.score >= 0 else "#dc3545"
        st.markdown(f"<div style='text-align: center; padding: 20px; background-color: {score_color}; color: white; border-radius: 15px; margin-bottom: 20px;'><h2>🎯 Final Score: {ss.score:.1f}/{len(ss.letters)}</h2></div>", unsafe_allow_html=True)
        
        if ss.results and len(ss.results) == len(ss.letters) \
           and all(r[3] == "✅" for r in ss.results):
            if not hasattr(ss, 'balloons_shown') or not ss.balloons_shown:
                st.balloons()
                ss.balloons_shown = True
            st.markdown("### 🎉 Perfect Round! Outstanding!")

        st.markdown("### 📋 Detailed Results")
        for L, industry, correct_industry, mark in ss.results:
            color = "#d4edda" if mark == "✅" else "#f8d7da"
            border_color = "#28a745" if mark == "✅" else "#dc3545"
            
            # Get the metrics for this point
            beta  = float(ss.df.at[ss.letters.index(L), "Beta"])
            wacc  = float(ss.df.at[ss.letters.index(L), "WACC"])
            debt  = float(ss.df.at[ss.letters.index(L), "Debt"])
            if debt <= 1:
                debt *= 100
            metric_display = f"Beta: {beta:.2f}, Debt%: {debt:.2f}%, WACC: {wacc:.2f}%"
            
            st.markdown(f"""
            <div style='padding: 10px; margin: 5px 0; background-color: {color}; 
                        border-left: 4px solid {border_color}; border-radius: 5px;'>
                <strong>{mark} Point {L}</strong> ({metric_display})<br>
                <small>Correct Industry: {correct_industry}</small>
            </div>
            """, unsafe_allow_html=True)

# ---------- footer ----------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 14px; padding: 20px;'>"
    "Industry Matching Game | Developed by Prof. Marc Goergen with the help of ChatGPT and Claude"
    "</div>", 
    unsafe_allow_html=True
)
