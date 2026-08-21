import streamlit as st
import pandas as pd
import io

# --- Helper Functions (લોજીક) ---
def clean_str(x):
    return str(x).strip().upper() if pd.notna(x) else ""

# નવું અને સ્માર્ટ લોજીક: અટક આગળ-પાછળ ચેક કરવા માટે
def is_name_swapped(name, target_name):
    if not name or not target_name: return False
    
    words = name.split()
    if len(words) > 1:
        # લોજીક 1: છેલ્લો શબ્દ (અટક) આગળ લાવીને ચેક કરો (દા.ત. DHRUVIT AMITBHAI SOLANKI -> SOLANKI DHRUVIT AMITBHAI)
        last_to_first = words[-1] + " " + " ".join(words[:-1])
        
        # લોજીક 2: પહેલો શબ્દ (અટક) પાછળ લઈ જઈને ચેક કરો (દા.ત. SOLANKI DHRUVIT AMITBHAI -> DHRUVIT AMITBHAI SOLANKI)
        first_to_last = " ".join(words[1:]) + " " + words[0]
        
        # જો કોઈ પણ એક લોજીક સાચું પડે, તો True પરત કરો
        return target_name == last_to_first or target_name == first_to_last
        
    return False

def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    return output.getvalue()

# --- Streamlit UI (વેબપેજની ડિઝાઇન) ---
st.set_page_config(page_title="Student Reports Generator", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    .stDataFrame { width: 100%; }
    .download-btn-container { display: flex; justify-content: center; align-items: center; padding: 5px; }
    .stMarkdown p { font-size: 16px; line-height: 1.5;}
    .block-container { padding-top: 2rem; padding-bottom: 2rem; padding-left: 1rem; padding-right: 1rem; }
    .instruction-box { background-color: #e8f4f8; border-left: 5px solid #17a2b8; padding: 15px; border-radius: 5px; margin-bottom: 20px;}
    .instruction-box h4 { margin-top: 0; color: #0c5460; font-weight: bold;}
    .instruction-box ol { margin-bottom: 0; font-size: 16px; color: #0c5460; line-height: 1.6;}
</style>
""", unsafe_allow_html=True)

st.title("🎓 Student Reports Generator")

# --- Instructions Section ---
st.markdown("""
<div class="instruction-box">
    <h4>📌 રિપોર્ટ માટેની એક્સેલ ફાઈલ ક્યાંથી ડાઉનલોડ કરવી?</h4>
    <ol>
        <li>તમારી શાળાના UDISE+ પોર્ટલના લોગીનમાં જાઓ.</li>
        <li>ડાબી બાજુની <b>Side Panel</b> માં <b>"List of All Students"</b> પર ક્લિક કરો.</li>
        <li>તેની નીચે <b>"Active Students"</b> લખેલું હશે, તેના પર ક્લિક કરો.</li>
        <li>તમારી સ્ક્રીન પર વિદ્યાર્થીઓની યાદી આવશે, તેની ઉપર <b>જમણી બાજુએ ખૂણામાં (Top Right Corner) "Download Excel"</b> નામનું બટન હશે.</li>
        <li>તેના પર ક્લિક કરતા ફાઈલ ડાઉનલોડ થઈ જશે, <b>આ જ ફાઈલ તમારે નીચે અપલોડ કરવાની છે.</b></li>
    </ol>
</div>
""", unsafe_allow_html=True)

st.write("તમારી ડાઉનલોડ કરેલી સ્ટુડન્ટ ડેટાની એક્સેલ ફાઈલ નીચે અપલોડ કરો અને અલગ-અલગ રિપોર્ટ્સ મેળવો.")

uploaded_file = st.file_uploader("અહીં એક્સેલ ફાઈલ (.xlsx) અપલોડ કરો", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        with st.spinner('ફાઈલ પ્રોસેસ થઈ રહી છે... કૃપા કરીને રાહ જુઓ...'):
            df = pd.read_excel(uploaded_file, skiprows=2)
            
            df['Name_clean'] = df['Name'].apply(clean_str)
            df['AADHAAR_Name_clean'] = df['Name As per AADHAAR'].apply(clean_str)
            
            aadhaar_status = df['AADHAAR Validation Status'].str.strip().str.upper()
            is_verified = aadhaar_status == 'VERIFIED'
            same_name = df['Name_clean'] == df['AADHAAR_Name_clean']
            
            # નવા લોજીકનો ઉપયોગ
            is_swapped_series = df.apply(lambda row: is_name_swapped(row['Name_clean'], row['AADHAAR_Name_clean']), axis=1)
            
            # Reports
            apaar_pending_status = ['NA', 'NOT AVAILABLE', 'NAN', 'REQUESTED', 'PENDING']
            apaar_pending = df['APAAR Status'].isna() | df['APAAR Status'].astype(str).str.strip().str.upper().isin(apaar_pending_status)
            
            df_report1 = df[is_verified & apaar_pending & same_name]
            df_report2 = df[is_verified & is_swapped_series & ~same_name]
            df_report3 = df[is_verified & (df['Name_clean'] != df['AADHAAR_Name_clean']) & ~is_swapped_series]
            
            mbu_statuses = ['MBU PENDING (AGE 5-15)', 'MBU PENDING (AGE 15 AND ABOVE)']
            df_report4 = df[df['MBU Status'].astype(str).str.strip().str.upper().isin(mbu_statuses)]
            df_report5 = df[aadhaar_status == 'AADHAAR NOT AVAILABLE']
            df_report6 = df[aadhaar_status == 'VALIDATION FAILED']

        st.success("✅ રિપોર્ટ્સ સફળતાપૂર્વક જનરેટ થઈ ગયા છે!")
        
        # --- Summary ---
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

        # --- Action Plan ---
        st.header("📌 કરવાની થતી કાર્યવાહી અને ડાઉનલોડ")
        def display_report_row(report_name, count, action_text, df_data, file_name):
            with st.container(border=True):
                c1, c2 = st.columns([7, 3]) 
                with c1:
                    st.markdown(f"**{report_name}** (વિદ્યાર્થીઓ: {count})")
                    st.info(f"👉 **કાર્યવાહી:** {action_text}")
                with c2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.download_button(
                        label=f"📥 ડાઉનલોડ", 
                        data=convert_df_to_excel(df_data), 
                        file_name=file_name, 
                        use_container_width=True,
                        key=file_name 
                    )

        display_report_row("1. APAAR Pending + સમાન નામ", len(df_report1), "UDISE અને આધારમાં સમાન નામ છે પણ APAAR ID જનરેટ કરવાના બાકી (Pending) છે. આ બાળકોનું તરત જ APAAR ID Generate થઈ જશે એટલે તાત્કાલિક જનરેટ કરી દેવું.", df_report1, "1_APAAR_Pending_Same_Name.xlsx")
        display_report_row("2. નામ અને અટક આગળ-પાછળ", len(df_report2), "આ બાળકોના નામ સુધારવા માટે શાળા કક્ષાએ 'Update student Name' પર ક્લિક કરી કામ કરવું.", df_report2, "2_Name_Swapped.xlsx")
        display_report_row("3. Verified પણ નામ મિસમેચ", len(df_report3), "આધાર Verify થઈ ગયેલ છે, પણ UDISE માં જે નામ છે તે સુધારવાની જરૂર છે. આવા બાળકોની માહિતી તૈયાર રાખવી, જેને BRC ભવન પર સુધારો કરી શકાશે.", df_report3, "3_Verified_Name_Mismatch.xlsx")
        display_report_row("4. MBU Pending", len(df_report4), "આ બાળકોના ડેટાને Revalidate કરવાની જરૂર છે. અને રીવેલિડેટ કર્યા પછી પણ પેન્ડિંગ આવે તો આ બાળકને આધાર સેન્ટર પર જઈ એક વાર અપડેટ કરાવવું પડશે.", df_report4, "4_MBU_Pending.xlsx")
        display_report_row("5. આધાર Not Available", len(df_report5), "આ બાળકોની આધાર કાર્ડની વિગત ભરવાની બાકી છે. આવા બાળકની વિગત મંગાવીને આ વિગત તાત્કાલિક ભરી દેવી.", df_report5, "5_Aadhaar_Not_Available.xlsx")
        display_report_row("6. Validation Failed", len(df_report6), "આ બાળકોનું 'Name as per AADHAAR' ખોટું છે. સાચું અને લેટેસ્ટ આધાર કાર્ડ મંગાવી માહિતી સુધારવાની છે.", df_report6, "6_Validation_Failed.xlsx")
        
    except Exception as e:
        st.error(f"ફાઈલ પ્રોસેસ કરવામાં ભૂલ આવી. કૃપા કરીને યોગ્ય ફાઈલ અપલોડ કરો. Error: {e}")
