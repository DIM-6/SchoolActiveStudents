import streamlit as st
import pandas as pd
import io

# --- Helper Functions (લોજીક) ---
def clean_str(x):
    return str(x).strip().upper() if pd.notna(x) else ""

def swap_first_last(name):
    if pd.isna(name): return ""
    words = str(name).strip().upper().split()
    if len(words) > 1:
        # પહેલો અને છેલ્લો શબ્દ બદલવા
        words[0], words[-1] = words[-1], words[0]
    return " ".join(words)

# ડેટાફ્રેમને સીધા એક્સેલ ફાઈલ તરીકે મેમરીમાંથી ડાઉનલોડ કરાવવા માટે
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    return output.getvalue()

# --- Streamlit UI (વેબપેજની ડિઝાઇન) ---
st.set_page_config(page_title="Student Reports Generator", page_icon="🎓")
st.title("🎓 Student Reports Generator")
st.write("તમારી સ્ટુડન્ટ ડેટાની એક્સેલ ફાઈલ અપલોડ કરો અને 4 અલગ-અલગ રિપોર્ટ્સ મેળવો.")

# ફાઈલ અપલોડ વિજેટ
uploaded_file = st.file_uploader("અહીં એક્સેલ ફાઈલ (.xlsx) અપલોડ કરો", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        with st.spinner('ફાઈલ પ્રોસેસ થઈ રહી છે... કૃપા કરીને રાહ જુઓ...'):
            # ફાઈલ રીડ કરવી (શરૂઆતની 2 લાઈન સ્કીપ કરીને)
            df = pd.read_excel(uploaded_file, skiprows=2)
            
            # ડેટા ક્લીનિંગ
            df['Name_clean'] = df['Name'].apply(clean_str)
            df['AADHAAR_Name_clean'] = df['Name As per AADHAAR'].apply(clean_str)
            df['Swapped_Name'] = df['Name_clean'].apply(swap_first_last)
            
            # સામાન્ય શરતો
            is_verified = df['AADHAAR Validation Status'].str.strip().str.upper() == 'VERIFIED'
            same_name = df['Name_clean'] == df['AADHAAR_Name_clean']
            
            # Report 2: APAAR NA + Same Name
            apaar_na = df['APAAR Status'].isna() | df['APAAR Status'].astype(str).str.strip().str.upper().isin(['NA', 'NOT AVAILABLE', 'NAN'])
            df_report2 = df[is_verified & apaar_na & same_name]
            
            # Report 3: Name Swapped (અટક આગળ-પાછળ)
            swapped_match = df['Swapped_Name'] == df['AADHAAR_Name_clean']
            df_report3 = df[is_verified & swapped_match & ~same_name]
            
            # Report 4: Verified + Name Mismatch (ઉપરના બાદ કરતા)
            df_report4 = df[is_verified & (df['Name_clean'] != df['AADHAAR_Name_clean']) & ~swapped_match]
            
            # Report 5: MBU Pending
            mbu_statuses = ['MBU PENDING (AGE 5-15)', 'MBU PENDING (AGE 15 AND ABOVE)']
            df_report5 = df[df['MBU Status'].astype(str).str.strip().str.upper().isin(mbu_statuses)]

        # --- Summary Section ---
        st.success("✅ રિપોર્ટ્સ સફળતાપૂર્વક જનરેટ થઈ ગયા છે!")
        st.header("📊 Report Summary")
        
        # આંકડાઓ દર્શાવવા માટે
        col1, col2 = st.columns(2)
        col1.metric("કુલ વિદ્યાર્થીઓ", len(df))
        col2.metric("1. APAAR NA + સમાન નામ", len(df_report2))
        
        col3, col4, col5 = st.columns(3)
        col3.metric("2. નામ/અટક બદલવાથી મેચ", len(df_report3))
        col4.metric("3. Verified + નામ મિસમેચ", len(df_report4))
        col5.metric("4. MBU Pending", len(df_report5))
        
        st.divider()

        # --- Download Section ---
        st.header("⬇️ રિપોર્ટ્સ ડાઉનલોડ કરો")
        
        st.download_button(label="📥 1. Download: Same Name + APAAR NA", 
                           data=convert_df_to_excel(df_report2), 
                           file_name="Report_2_APAAR_NA_Same_Name.xlsx", 
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                           
        st.download_button(label="📥 2. Download: Name Swapped (અટક આગળ-પાછળ)", 
                           data=convert_df_to_excel(df_report3), 
                           file_name="Report_3_Name_Swapped.xlsx", 
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                           
        st.download_button(label="📥 3. Download: Verified + Name Mismatch", 
                           data=convert_df_to_excel(df_report4), 
                           file_name="Report_4_Verified_Mismatch.xlsx", 
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                           
        st.download_button(label="📥 4. Download: MBU Pending", 
                           data=convert_df_to_excel(df_report5), 
                           file_name="Report_5_MBU_Pending.xlsx", 
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
    except Exception as e:
        st.error(f"ફાઈલ પ્રોસેસ કરવામાં ભૂલ આવી. કૃપા કરીને યોગ્ય ફાઈલ અપલોડ કરો. Error: {e}")
