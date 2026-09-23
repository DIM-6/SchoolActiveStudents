import streamlit as st
import pandas as pd
import io

# --- Helper Functions (લોજીક) ---
def clean_str(x):
    return str(x).strip().upper() if pd.notna(x) else ""

def is_name_swapped(name, target_name):
    if not name or not target_name: return False
    words = name.split()
    if len(words) > 1:
        last_to_first = words[-1] + " " + " ".join(words[:-1])
        first_to_last = " ".join(words[1:]) + " " + words[0]
        return target_name == last_to_first or target_name == first_to_last
    return False

def is_one_char_diff(name1, name2):
    if not name1 or not name2 or name1 == name2: return False
    len1, len2 = len(name1), len(name2)
    if abs(len1 - len2) > 1: return False 
    if len1 == len2:
        diff_count = sum(1 for a, b in zip(name1, name2) if a != b)
        return diff_count == 1
    else:
        if len1 > len2:
            name1, name2 = name2, name1
        i = 0
        while i < len(name1) and name1[i] == name2[i]:
            i += 1
        return name1[i:] == name2[i+1:]

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
        <li>તમારી શાળાના UDISE+ પોર્ટલના <b>'Student Module'</b> માં લોગીન કરો.</li>
        <li>ડાબી બાજુની <b>Side Panel</b> માં <b>"List of All Students"</b> પર ક્લિક કરો.</li>
        <li>તેની નીચે <b>"Active Students"</b> લખેલું હશે, તેના પર ક્લિક કરો.</li>
        <li>તમારી સ્ક્રીન પર વિદ્યાર્થીઓની યાદી આવશે, તેની ઉપર <b>જમણી બાજુએ ખૂણામાં (Top Right Corner) "Download Excel"</b> નામનું બટન હશે.</li>
        <li>તેના પર ક્લિક કરતા ફાઈલ ડાઉનલોડ થઈ જશે, <b>આ જ ફાઈલ તમારે નીચે અપલોડ કરવાની છે.</b></li>
    </ol>
</div>
""", unsafe_allow_html=True)

# --- ક્યા રિપોર્ટ મળશે તેની માહિતી (રંગબેરંગી બોક્સમાં) ---
with st.expander("ℹ️ આ ટૂલની મદદથી તમને કયા ૭ રિપોર્ટ્સ મળશે? (અહીં ક્લિક કરો)"):
    st.markdown("**આ ટૂલ તમારો સમય બચાવવા માટે નીચે મુજબના ૭ અલગ-અલગ રિપોર્ટ આપોઆપ જનરેટ કરશે:**")
    st.markdown("<br>", unsafe_allow_html=True) # થોડી જગ્યા છોડવા
    
    # માહિતીને 2 કોલમમાં વહેંચી દીધી છે
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.info("🔹 **૧. નામ સમાન પણ APAAR Pending**\n\nજેમનું UDISE અને આધાર કાર્ડમાં નામ સમાન છે પણ APAAR ID જનરેટ કરવાનું બાકી છે.")
        st.warning("🔹 **૩. Verified છે પણ નામમાં સુધારો**\n\nજેમના આધાર વેરીફાઈ થઈ ગયા છે પણ બંને નામના સ્પેલિંગમાં મોટો તફાવત છે.")
        st.error("🔹 **૫. આધાર કાર્ડની વિગત નથી**\n\nજેમની આધાર કાર્ડની વિગત હજુ સુધી ભરેલી જ નથી.")
        st.success("🔹 **૭. સ્પેલિંગમાં ૧ અક્ષરની ભૂલ**\n\nજેમનાં નામમાં માત્ર એક જ અક્ષરની ભૂલ છે, જે શાળા કક્ષાએ સહેલાઈથી સુધારી શકાશે.")
        
    with info_col2:
        st.info("🔹 **૨. નામ અને અટક આગળ-પાછળ (Swapped)**\n\nજેમનું નામ અને અટક આધાર કાર્ડ અને UDISE માં આગળ-પાછળ થઈ ગયા છે.")
        st.warning("🔹 **૪. MBU Pending**\n\nજે બાળકોનું MBU (Mobile/Biometric Update) પેન્ડિંગ છે.")
        st.error("🔹 **૬. આધાર Verification Failed**\n\nજે બાળકોનું આધાર વેરીફીકેશન ફેલ થયું છે અને માહિતી સુધારવાની જરૂર છે.")

st.write("તમારી ડાઉનલોડ કરેલી સ્ટુડન્ટ ડેટાની એક્સેલ ફાઈલ નીચે અપલોડ કરો અને અલગ-અલગ રિપોર્ટ્સ મેળવો.")

uploaded_file = st.file_uploader("અહીં એક્સેલ ફાઈલ (.xlsx) અપલોડ કરો", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        with st.spinner('ફાઈલ પ્રોસેસ થઈ રહી છે... કૃપા કરીને રાહ જુઓ...'):
            df = pd.read_excel(uploaded_file, skiprows=2)
            
            # --- 🛑 ERROR VALIDATION ---
            required_columns = ['Name', 'Name As per AADHAAR', 'AADHAAR Validation Status', 'APAAR Status', 'MBU Status']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if len(missing_columns) > 0:
                st.error("❌ **ખોટી ફાઈલ અપલોડ થઈ છે!**")
                st.warning("તમે અપલોડ કરેલી ફાઈલમાં નીચે મુજબના જરૂરી કોલમ (હેડિંગ) મળ્યા નથી:")
                for col in missing_columns:
                    st.write(f"- {col}")
                st.info("💡 કૃપા કરીને ઉપર આપેલી સૂચના મુજબ UDISE પોર્ટલમાંથી સાચી 'List of All Students' ની ફાઈલ જ અપલોડ કરો.")
                st.stop()

            df['Name_clean'] = df['Name'].apply(clean_str)
            df['AADHAAR_Name_clean'] = df['Name As per AADHAAR'].apply(clean_str)
            
            aadhaar_status = df['AADHAAR Validation Status'].str.strip().str.upper()
            is_verified = aadhaar_status == 'VERIFIED'
            same_name = df['Name_clean'] == df['AADHAAR_Name_clean']
            
            is_swapped_series = df.apply(lambda row: is_name_swapped(row['Name_clean'], row['AADHAAR_Name_clean']), axis=1)
            is_one_char_diff_series = df.apply(lambda row: is_one_char_diff(row['Name_clean'], row['AADHAAR_Name_clean']), axis=1)
            
            apaar_pending_status = ['NA', 'NOT AVAILABLE', 'NAN', 'REQUESTED', 'PENDING']
            apaar_pending = df['APAAR Status'].isna() | df['APAAR Status'].astype(str).str.strip().str.upper().isin(apaar_pending_status)
            
            df_report1 = df[is_verified & apaar_pending & same_name]
            df_report2 = df[is_verified & is_swapped_series & ~same_name]
            df_report3 = df[is_verified & (df['Name_clean'] != df['AADHAAR_Name_clean']) & ~is_swapped_series & ~is_one_char_diff_series]
            
            mbu_statuses = ['MBU PENDING (AGE 5-15)', 'MBU PENDING (AGE 15 AND ABOVE)']
            df_report4 = df[df['MBU Status'].astype(str).str.strip().str.upper().isin(mbu_statuses)]
            df_report5 = df[aadhaar_status == 'AADHAAR NOT AVAILABLE']
            df_report6 = df[aadhaar_status == 'VALIDATION FAILED']
            df_report7 = df[is_verified & is_one_char_diff_series & ~same_name & ~is_swapped_series]

        st.success("✅ રિપોર્ટ્સ સફળતાપૂર્વક જનરેટ થઈ ગયા છે!")
        
        # --- Summary Section (TABLE સ્વરૂપે) ---
        st.header("📊 રિપોર્ટ સમરી")
        
        summary_data = {
            "રિપોર્ટનું નામ": [
                "કુલ વિદ્યાર્થીઓ (Total Students)",
                "૧. નામ સમાન પણ APAAR Pending તેવા વિદ્યાર્થીઓ",
                "૨. નામ અને અટક આગળ પાછળ થઈ શકે તેવા વિદ્યાર્થીઓ",
                "૩. આધાર Verified છે પણ નામમાં સુધારો કરવાનો છે તેવા વિદ્યાર્થીઓ",
                "૪. MBU Pending તેવા વિદ્યાર્થીઓ",
                "૫. આધાર કાર્ડની વિગત નથી તેવા વિદ્યાર્થીઓ",
                "૬. આધાર Verification Failed તેવા વિદ્યાર્થીઓ",
                "૭. સ્પેલિંગમાં ૧ અક્ષરની ભૂલ હોય તેવા વિદ્યાર્થીઓની યાદી"
            ],
            "વિદ્યાર્થીઓની સંખ્યા": [
                len(df),
                len(df_report1),
                len(df_report2),
                len(df_report3),
                len(df_report4),
                len(df_report5),
                len(df_report6),
                len(df_report7)
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.table(summary_df)
        
        st.divider()

        # --- Action Plan & Download Section ---
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

        display_report_row("૧. નામ સમાન પણ APAAR Pending તેવા વિદ્યાર્થીઓ", len(df_report1), "UDISE અને આધારમાં સમાન નામ છે પણ APAAR ID જનરેટ કરવાના બાકી (Pending) છે. આ બાળકોનું તરત જ APAAR ID Generate થઈ જશે એટલે તાત્કાલિક જનરેટ કરી દેવું.", df_report1, "1_APAAR_Pending_Same_Name.xlsx")
        
        display_report_row("૨. નામ અને અટક આગળ પાછળ થઈ શકે તેવા વિદ્યાર્થીઓ", len(df_report2), "આ બાળકોના નામ સુધારવા માટે શાળા કક્ષાએ 'Update student Name' પર ક્લિક કરી કામ કરવું.", df_report2, "2_Name_Swapped.xlsx")
        
        display_report_row("૩. આધાર Verified છે પણ નામમાં સુધારો કરવાનો છે તેવા વિદ્યાર્થીઓ", len(df_report3), "આધાર Verify થઈ ગયેલ છે, પણ UDISE માં જે નામ છે તે સુધારવાની જરૂર છે. આવા બાળકોની માહિતી તૈયાર રાખવી, જેને BRC ભવન પર સુધારો કરી શકાશે.", df_report3, "3_Verified_Name_Mismatch.xlsx")
        
        display_report_row("૪. MBU Pending તેવા વિદ્યાર્થીઓ", len(df_report4), "આ બાળકોના ડેટાને Revalidate કરવાની જરૂર છે. અને રીવેલિડેટ કર્યા પછી પણ પેન્ડિંગ આવે તો આ બાળકને આધાર સેન્ટર પર જઈ એક વાર અપડેટ કરાવવું પડશે.", df_report4, "4_MBU_Pending.xlsx")
        
        display_report_row("૫. આધાર કાર્ડની વિગત નથી તેવા વિદ્યાર્થીઓ", len(df_report5), "આ બાળકોની આધાર કાર્ડની વિગત ભરવાની બાકી છે. આવા બાળકની વિગત મંગાવીને આ વિગત તાત્કાલિક ભરી દેવી.", df_report5, "5_Aadhaar_Not_Available.xlsx")
        
        display_report_row("૬. આધાર Verification Failed તેવા વિદ્યાર્થીઓ", len(df_report6), "આ બાળકોનું 'Name as per AADHAAR' ખોટું છે. સાચું અને લેટેસ્ટ આધાર કાર્ડ મંગાવી માહિતી સુધારવાની છે.", df_report6, "6_Validation_Failed.xlsx")
        
        display_report_row("૭. સ્પેલિંગમાં ૧ અક્ષરની ભૂલ હોય તેવા વિદ્યાર્થીઓની યાદી", len(df_report7), "આ બાળકોના નામમાં માત્ર 1 જ અક્ષરનો ફેરફાર છે (દા.ત. અક્ષર રહી ગયો હોય કે ખોટો હોય). UDISE માં સામાન્ય સુધારો કરવાથી બંને નામ સમાન થઈ જશે.", df_report7, "7_One_Char_Spelling_Mistake.xlsx")
        
    except Exception as e:
        st.error(f"ફાઈલ પ્રોસેસ કરવામાં અણધારી ભૂલ આવી. કૃપા કરીને ફાઈલ ચેક કરો. Error: {e}")
