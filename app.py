import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURATION ---
# Paste your Google Sheet 'Publish to Web' CSV link here
CSV_URL = "PASTE_YOUR_GOOGLE_SHEET_CSV_LINK_HERE"

# Define the columns we care about (excluding Timestamp)
PROPERTY_COLS = [
    "05 Marla", "08 Marla", "10 Marla", 
    "01 Kanal", "02 Kanal", 
    "04 Marla Commercial", "08 Marla Commercial"
]

# --- PAGE SETUP ---
st.set_page_config(page_title="DHA Phase 10 Rates", layout="wide")

# --- DATA LOADING FUNCTION ---
@st.cache_data(ttl=60)  # Refresh data every 60 seconds
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        # Convert Timestamp to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        # Sort by date to ensure latest is at the bottom
        df = df.sort_values(by='Timestamp').reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# --- SIDEBAR (ADMIN & NAV) ---
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Public Dashboard", "Admin Entry"])

# --- PUBLIC DASHBOARD ---
if menu == "Public Dashboard":
    st.title("📈 DHA Phase 10 File Rates")
    st.markdown("Live updates based on daily market entries.")

    df = load_data()

    if not df.empty:
        # Get Latest (Today) and Previous (Yesterday/Last Entry)
        current = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else current
        
        # Display Last Updated Time
        st.caption(f"Last Updated: {current['Timestamp'].strftime('%d %b %Y, %I:%M %p')}")

        # Create Metrics Grid
        st.subheader("Current Market Rates")
        cols = st.columns(4) # 4 columns per row
        
        for i, col_name in enumerate(PROPERTY_COLS):
            # Calculate Change
            curr_val = current[col_name]
            prev_val = previous[col_name]
            change = curr_val - prev_val
            
            # Determine Color for Delta
            if change > 0:
                delta_color = "normal" # Green
            elif change < 0:
                delta_color = "inverse" # Red
            else:
                delta_color = "off"

            # Distribute into rows of 4
            with cols[i % 4]:
                st.metric(
                    label=col_name,
                    value=f"{curr_val}",
                    delta=f"{change:+}",
                    delta_color=delta_color
                )
        
        st.divider()

        # --- CHARTS ---
        st.subheader("Price Trends")
        
        # Multiselect for chart properties
        chart_props = st.multiselect(
            "Select properties to compare:",
            PROPERTY_COLS,
            default=["05 Marla", "01 Kanal"]
        )

        if chart_props:
            fig = px.line(
                df, 
                x='Timestamp', 
                y=chart_props,
                markers=True,
                title="Historical Rate Trend",
                labels={'value': 'Rate (Lakhs)', 'Timestamp': 'Date'}
            )
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
        
        # Show Raw Data (Optional collapse)
        with st.expander("View Historical Data"):
            st.dataframe(df.sort_values(by='Timestamp', ascending=False), use_container_width=True)

    else:
        st.warning("No data available yet. Waiting for first entry.")

# --- ADMIN ENTRY SECTION ---
elif menu == "Admin Entry":
    st.title("🔒 Admin Data Entry")
    
    password = st.text_input("Enter Admin Password", type="password")
    
    # Simple Client-Side Password Protection
    if password == "admin123": # CHANGE THIS PASSWORD
        st.success("Access Granted")
        
        st.info("💡 Use the Google Form below to enter daily rates.")
        
        # Replace with your actual Google Form Link
        FORM_LINK = "PASTE_YOUR_GOOGLE_FORM_LINK_HERE"
        
        st.markdown(f"""
        ### Data Entry Portal
        [**Click Here to Open Data Entry Form**]({FORM_LINK})
        """)
        
        st.divider()
        st.subheader("Recent Entries Log")
        df = load_data()
        if not df.empty:
            st.dataframe(df.tail(10), use_container_width=True)
    else:
        if password:
            st.error("Incorrect Password")
        st.warning("This section is for employees only.")