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

# Custom CSS for Mobile Responsive Table and Download Buttons
st.markdown("""
<style>
    /* ટેબલ માટે મોબાઈલ ફ્રેન્ડલી ડીઝાઈન */
    .stDataFrame {
        width: 100%;
    }
    .download-btn-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 5px;
    }
    
    /* સાધારણ ટેક્સ્ટ સ્ટાઈલ */
    .stMarkdown p {
        font-size: 16px;
    }
    
    /* આખી સ્ક્રીનમાં માર્જિન સેટ કરવા */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎓 Student Reports Generator")
st.write("તમારી સ્ટુડન્ટ ડેટાની એક્સેલ ફાઈલ અપલોડ કરો અને અલગ-અલગ રિપોર્ટ્સ મેળવો.")

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
            aadhaar_status = df['AADHAAR Validation Status'].str.strip().str.upper()
            is_verified = aadhaar_status == 'VERIFIED'
            same_name = df['Name_clean'] == df['AADHAAR_Name_clean']
            
            # 1. Report: APAAR Pending + સમાન નામ
            apaar_pending_status = ['NA', 'NOT AVAILABLE', 'NAN', 'REQUESTED', 'PENDING']
            apaar_pending = df['APAAR Status'].isna() | df['APAAR Status'].astype(str).str.strip().str.upper().isin(apaar_pending_status)
            df_report1 = df[is_verified & apaar_pending & same_name]
            
            # 2. Report: નામ અને અટક આગળ-પાછળ (Name Swapped)
            swapped_match = df['Swapped_Name'] == df['AADHAAR_Name_clean']
            df_report2 = df[is_verified & swapped_match & ~same_name]
            
            # 3. Report: Verified પણ નામ મિસમેચ
            df_report3 = df[is_verified & (df['Name_clean'] != df['AADHAAR_Name_clean']) & ~swapped_match]
            
            # 4. Report: MBU Pending
            mbu_statuses = ['MBU PENDING (AGE 5-15)', 'MBU PENDING (AGE 15 AND ABOVE)']
            df_report4 = df[df['MBU Status'].astype(str).str.strip().str.upper().isin(mbu_statuses)]
            
            # 5. Report: AADHAAR not available
            df_report5 = df[aadhaar_status == 'AADHAAR NOT AVAILABLE']
            
            # 6. Report: Validation failed
            df_report6 = df[aadhaar_status == 'VALIDATION FAILED']

        st.success("✅ રિપોર્ટ્સ સફળતાપૂર્વક જનરેટ થઈ ગયા છે!")
        
        # --- Summary Section (Mobile Friendly) ---
        st.header("📊 Report Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("કુલ વિદ્યાર્થીઓ", len(df))
        col2.metric("1. APAAR Pending", len(df_report1))
        col3.metric("2. નામ/અટક બદલ", len(df_report2))
        
        col4, col5, col6 = st.columns(3)
        col4.metric("3. Verified મિસમેચ", len(df_report3))
        col5.metric("4. MBU Pending", len(df_report4))
        col6.metric("5. આધાર Not Avl.", len(df_report5))
        
        col7, _, _ = st.columns(3)
        col7.metric("6. Validation Failed", len(df_report6))
        
        st.divider()

        # --- Action Plan & Download Section ---
        st.header("📌 કરવાની થતી કાર્યવાહી અને ડાઉનલોડ (Action Plan & Downloads)")
        st.write("નીચે આપેલ ટેબલમાંથી વિદ્યાર્થીઓની સંખ્યા મુજબ રિપોર્ટ ડાઉનલોડ કરો અને સામે આપેલી કાર્યવાહી પોર્ટલ પર કરો.")

        # Streamlit માં ટેબલની અંદર સીધા ડાઉનલોડ બટન ન મૂકી શકાય, 
        # તેથી આપણે દરેક રિપોર્ટ માટે એક સરસ "કાર્ડ / રો (Row)" જેવી ડીઝાઇન બનાવી છે 
        # જે મોબાઇલમાં ટેબલ કરતા પણ વધુ સારી દેખાય છે.

        def display_report_row(report_name, count, action_text, df_data, file_name):
            with st.container(border=True):
                # મોબાઈલ માટે કોલમ લેઆઉટ (માત્ર 2 કોલમ)
                c1, c2 = st.columns([7, 3]) 
                
                with c1:
                    st.markdown(f"**{report_name}** (વિદ્યાર્થીઓ: {count})")
                    st.info(f"👉 **કાર્યવાહી:** {action_text}")
                
                with c2:
                    st.markdown("<br>", unsafe_allow_html=True) # થોડી જગ્યા માટે
                    st.download_button(
                        label=f"📥 ડાઉનલોડ", 
                        data=convert_df_to_excel(df_data), 
                        file_name=file_name, 
                        use_container_width=True,
                        key=file_name # Unique key for each button
                    )

        # 1. APAAR Pending
        display_report_row(
            "1. APAAR Pending + સમાન નામ", 
            len(df_report1), 
            "UDISE અને આધારમાં સમાન નામ છે પણ APAAR ID જનરેટ કરવાના બાકી (Pending) છે.", 
            df_report1, "1_APAAR_Pending_Same_Name.xlsx"
        )
        
        # 2. Name Swapped
        display_report_row(
            "2. નામ અને અટક આગળ-પાછળ", 
            len(df_report2), 
            "આ બાળકોના નામ સુધારવા માટે શાળા કક્ષાએ 'Update student Name' પર ક્લિક કરી કામ કરવું.", 
            df_report2, "2_Name_Swapped.xlsx"
        )

        # 3. Verified Mismatch
        display_report_row(
            "3. Verified પણ નામ મિસમેચ", 
            len(df_report3), 
            "આધાર Verify થઈ ગયેલ છે, પણ UDISE માં જે નામ છે તે સુધારવાની જરૂર છે.", 
            df_report3, "3_Verified_Name_Mismatch.xlsx"
        )

        # 4. MBU Pending
        display_report_row(
            "4. MBU Pending", 
            len(df_report4), 
            "આ બાળકોના ડેટાને Revalidate કરવાની જરૂર છે.", 
            df_report4, "4_MBU_Pending.xlsx"
        )

        # 5. Aadhaar Not Available
        display_report_row(
            "5. આધાર Not Available", 
            len(df_report5), 
            "આ બાળકોની આધાર કાર્ડની વિગત ભરવાની બાકી છે.", 
            df_report5, "5_Aadhaar_Not_Available.xlsx"
        )

        # 6. Validation Failed
        display_report_row(
            "6. Validation Failed", 
            len(df_report6), 
            "આ બાળકોનું 'Name as per AADHAAR' ખોટું છે. સાચું અને લેટેસ્ટ આધાર કાર્ડ મંગાવી માહિતી સુધારવાની છે.", 
            df_report6, "6_Validation_Failed.xlsx"
        )
        
    except Exception as e:
        st.error(f"ફાઈલ પ્રોસેસ કરવામાં ભૂલ આવી. કૃપા કરીને યોગ્ય ફાઈલ અપલોડ કરો. Error: {e}")
