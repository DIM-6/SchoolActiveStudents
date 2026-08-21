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
        words[0], words[-1] = words[-1], words[0]
    return " ".join(words)

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    return output.getvalue()

# --- Streamlit UI (વેબપેજની ડિઝાઇન) ---
st.set_page_config(page_title="Student Reports Generator", page_icon="🎓", layout="wide")
st.title("🎓 Student Reports Generator")
st.write("તમારી સ્ટુડન્ટ ડેટાની એક્સેલ ફાઈલ અપલોડ કરો અને 4 અલગ-અલગ રિપોર્ટ્સ મેળવો.")

# ફાઈલ અપલોડ વિજેટ
uploaded_file = st.file_uploader("અહીં એક્સેલ ફાઈલ (.xlsx) અપલોડ કરો", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        with st.spinner('ફાઈલ પ્રોસેસ થઈ રહી છે... કૃપા કરીને રાહ જુઓ...'):
            df = pd.read_excel(uploaded_file, skiprows=2)
            
            # ડેટા ક્લીનિંગ
            df['Name_clean'] = df['Name'].apply(clean_str)
            df['AADHAAR_Name_clean'] = df['Name As per AADHAAR'].apply(clean_str)
            df['Swapped_Name'] = df['Name_clean'].apply(swap_first_last)
            
            # સામાન્ય શરતો
            is_verified = df['AADHAAR Validation Status'].str.strip().str.upper() == 'VERIFIED'
            same_name = df['Name_clean'] == df['AADHAAR_Name_clean']
            
            # Report 1: APAAR Pending + સમાન નામ (NA, Not Available, Requested, Pending બધું કવર થશે)
            apaar_pending_status = ['NA', 'NOT AVAILABLE', 'NAN', 'REQUESTED', 'PENDING']
            apaar_pending = df['APAAR Status'].isna() | df['APAAR Status'].astype(str).str.strip().str.upper().isin(apaar_pending_status)
            df_report1 = df[is_verified & apaar_pending & same_name]
            
            # Report 2: નામ અને અટક આગળ-પાછળ (Name Swapped)
            swapped_match = df['Swapped_Name'] == df['AADHAAR_Name_clean']
            df_report2 = df[is_verified & swapped_match & ~same_name]
            
            # Report 3: Verified પણ નામ મિસમેચ
            df_report3 = df[is_verified & (df['Name_clean'] != df['AADHAAR_Name_clean']) & ~swapped_match]
            
            # Report 4: MBU Pending
            mbu_statuses = ['MBU PENDING (AGE 5-15)', 'MBU PENDING (AGE 15 AND ABOVE)']
            df_report4 = df[df['MBU Status'].astype(str).str.strip().str.upper().isin(mbu_statuses)]

        st.success("✅ રિપોર્ટ્સ સફળતાપૂર્વક જનરેટ થઈ ગયા છે!")
        
        # --- Summary Section ---
        st.header("📊 Report Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("કુલ વિદ્યાર્થીઓ", len(df))
        col2.metric("1. APAAR Pending + સમાન નામ", len(df_report1))
        col3.metric("2. નામ/અટક આગળ-પાછળ", len(df_report2))
        col4.metric("3. Verified + નામ મિસમેચ", len(df_report3))
        col5.metric("4. MBU Pending", len(df_report4))
        
        st.divider()

        # --- Action Plan Table (કરવાની થતી કાર્યવાહી) ---
        st.header("📌 કરવાની થતી કાર્યવાહી (Action Plan)")
        action_plan_data = {
            "રિપોર્ટનું નામ": [
                "1. APAAR Pending + સમાન નામ", 
                "2. નામ અને અટક આગળ-પાછળ", 
                "3. Verified પણ નામ મિસમેચ", 
                "4. MBU Pending"
            ],
            "કરવાની થતી કાર્યવાહી (Action)": [
                "UDISE અને AADHAAR માં સમાન નામ છે પણ APAAR ID જનરેટ કરવાના બાકી (Pending) છે.",
                "આ બાળકોના નામ સુધારવા માટે શાળા કક્ષાએ 'Update student Name' પર ક્લિક કરી કામ કરવું.",
                "AADHAAR Verify થઈ ગયેલ છે, પણ UDISE માં જે નામ છે તે સુધારવાની જરૂર છે.",
                "આ બાળકોના ડેટાને Revalidate કરવાની જરૂર છે."
            ]
        }
        st.table(pd.DataFrame(action_plan_data))

        st.divider()

        # --- Download Section ---
        st.header("⬇️ રિપોર્ટ્સ ડાઉનલોડ કરો")
        
        # ડાઉનલોડ બટન્સ (બે કોલમમાં વ્યવસ્થિત ગોઠવવા માટે)
        d_col1, d_col2 = st.columns(2)
        
        with d_col1:
            st.download_button("📥 1. Download: APAAR Pending + સમાન નામ", 
                               data=convert_df_to_excel(df_report1), 
                               file_name="1_APAAR_Pending_Same_Name.xlsx", 
                               use_container_width=True)
                               
            st.download_button("📥 2. Download: નામ અને અટક આગળ-પાછળ", 
                               data=convert_df_to_excel(df_report2), 
                               file_name="2_Name_Swapped.xlsx", 
                               use_container_width=True)
        with d_col2:
            st.download_button("📥 3. Download: Verified પણ નામ મિસમેચ", 
                               data=convert_df_to_excel(df_report3), 
                               file_name="3_Verified_Name_Mismatch.xlsx", 
                               use_container_width=True)
                               
            st.download_button("📥 4. Download: MBU Pending", 
                               data=convert_df_to_excel(df_report4), 
                               file_name="4_MBU_Pending.xlsx", 
                               use_container_width=True)
        
    except Exception as e:
        st.error(f"ફાઈલ પ્રોસેસ કરવામાં ભૂલ આવી. કૃપા કરીને યોગ્ય ફાઈલ અપલોડ કરો. Error: {e}")
