import streamlit as st 
import requests
import json
import pandas as pd
import time
import plotly.graph_objects as go

st.set_page_config(page_title="Spam Detection Dashboard", layout="wide")

st.title("Real-time Spam Detection Dashboard")
st.markdown("----")

API_URL="http://api:8000"

if 'history' not in st.session_state:
    st.session_state.history=[]

with st.sidebar:
    st.header("Configuration")

    try:
        health= requests.get(f"{API_URL}/health").json()
        st.success("API Connected" if health.get("model_loaded") else "API Issues")

    except:
        st.error("API Not Reachable")

    st.markdown("----")

    if st.button("Clear History"):
        st.session_state.history=[]

    if st.session_state.history:
        total=len(st.session_state.history)
        spam_count=sum(1 for h in st.session_state.history if h.get('is_spam'))
        st.metric("Total Messages", total)
        st.metric("Spam Detected", spam_count)
        st.metric("Spam Rate", f"{(spam_count/total*100):.1f}%")

col1, col2= st.columns([2,1])

with col1:
    st.subheader("Test Spam Detection")

    message=st.text_area("Enter message to analyze", height=150, placeholder="Paste your message here...")

    col1a,col1b=st.columns(2)

    with col1a:
        if st.button("Analyze Single Message", type="primary"):
            if message:
                with st.spinner("Analyzing..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/predict",
                            json={"text": message}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Add to history
                            st.session_state.history.append({
                                "text": message[:100] + "..." if len(message) > 100 else message,
                                "is_spam": result["is_spam"],
                                "confidence": result["confidence"],
                                "time": time.strftime("%H:%M:%S")
                            })
                            
                            # Display result
                            if result["is_spam"]:
                                st.error(f"🚨 **SPAM DETECTED** (Confidence: {result['confidence']*100:.1f}%)")
                            else:
                                st.success(f"✅ **LEGITIMATE MESSAGE** (Confidence: {result['confidence']*100:.1f}%)")
                            
                            st.metric("Prediction Time", f"{result['prediction_time']*1000:.1f} ms")
                        else:
                            st.error("API Error")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter a message first.")
    
    with col1b:
        st.subheader("MQTT Test")
        mqtt_message = st.text_input("Test MQTT message:")
        if st.button("Publish to MQTT"):
            # This would require additional MQTT client setup
            st.info("MQTT publishing would be implemented here")

with col2:
    st.subheader("📊 Detection History")
    
    if st.session_state.history:
        # Create dataframe for display
        df = pd.DataFrame(st.session_state.history)
        
        # Display recent entries
        st.dataframe(df.tail(5), use_container_width=True)
        
        # Create visualization
        if len(df) > 1:
            fig = go.Figure()
            
            # Add spam markers
            spam_times = [i for i, row in enumerate(df.iloc[-10:].itertuples()) if row.is_spam]
            if spam_times:
                fig.add_trace(go.Scatter(
                    x=spam_times,
                    y=[0.5] * len(spam_times),
                    mode='markers',
                    marker=dict(size=15, color='red', symbol='x'),
                    name='Spam Detected'
                ))
            
            # Add confidence line
            fig.add_trace(go.Scatter(
                x=list(range(len(df.iloc[-10:]))),
                y=df.iloc[-10:]['confidence'],
                mode='lines+markers',
                name='Confidence',
                line=dict(color='blue')
            ))
            
            fig.update_layout(
                title="Recent Detection Confidence",
                xaxis_title="Message Sequence",
                yaxis_title="Confidence",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No messages analyzed yet.")

# Batch processing section
st.markdown("---")
st.subheader("📁 Batch Processing")

uploaded_file = st.file_uploader("Upload CSV/TSV with messages:", type=['csv', 'tsv', 'txt'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.tsv'):
            df_upload = pd.read_csv(uploaded_file, sep='\t')
        else:
            df_upload = pd.read_csv(uploaded_file)
        
        st.write("Preview:", df_upload.head())
        
        if st.button("Analyze All Messages"):
            messages = [{"text": str(row[0])} for row in df_upload.iloc[:, 0].values]
            
            with st.spinner(f"Analyzing {len(messages)} messages..."):
                try:
                    response = requests.post(
                        f"{API_URL}/batch_predict",
                        json=messages
                    )
                    
                    if response.status_code == 200:
                        results = response.json()
                        
                        # Create results dataframe
                        results_df = pd.DataFrame(results['results'])
                        
                        st.success(f"✅ Analysis complete! Processed {results['total']} messages")
                        
                        # Show summary
                        spam_count = sum(results_df['is_spam'])
                        st.metric("Spam Messages Found", spam_count)
                        
                        # Download button
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="Download Results as CSV",
                            data=csv,
                            file_name="spam_analysis_results.csv",
                            mime="text/csv"
                        )
                        
                except Exception as e:
                    st.error(f"Batch analysis failed: {e}")
                    
    except Exception as e:
        st.error(f"Error reading file: {e}")