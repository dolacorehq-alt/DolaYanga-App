import streamlit as st
import pandas as pd
import hashlib
import hmac
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from pathlib import Path

DATA_FILE = Path(__file__).with_name("transactions.csv")
CONTACT_FILE = Path(__file__).with_name("contact_messages.csv")
DISPLAY_DATE_FORMAT = "%d/%m/%Y"
DATE_INPUT_FORMAT = "DD/MM/YYYY"
LOGO_PATH = Path(__file__).with_name("Dola Yanga logo.png")
PIN_HASH_ITERATIONS = 200_000
MAX_LOGIN_ATTEMPTS = 5
LOCK_MINUTES = 5
ADMIN_PHONE_NUMBERS = {"0887137444"}
WEAK_PINS = {"0000", "1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888", "9999", "1234", "4321", "2580"}

NETWORKS = ["Airtel Money", "TNM Mpamba"]
TRANSACTION_TYPES = [
    "Money Received",
    "Money Sent",
    "Withdrawal",
    "Airtime",
    "Bill Payment",
    "Merchant Payment",
    "Other",
]
SPENDING_TYPES = [
    "Money Sent",
    "Withdrawal",
    "Airtime",
    "Bill Payment",
    "Merchant Payment",
    "Other",
]

TRANSLATIONS = {
    "en": {
        "language": "Language",
        "title": "DolaYanga",
        "subtitle": "Track your Airtel Money and TNM Mpamba transactions",
        "small_subtitle": "Simple mobile money tracker for Malawi",
        "guest_warning": "Guest Mode: transactions entered now are temporary and may be lost unless you create an account.",
        "account_action": "Create Account / Log In",
        "not_ready": "Account creation and login will be added in the public version.",
        "account": "Account",
        "guest_mode": "Guest Mode",
        "logged_in_as": "Logged in as",
        "create_account": "Create Account",
        "login": "Log In",
        "logout": "Log Out",
        "phone_number": "Phone Number",
        "app_pin": "App PIN",
        "create_app_pin": "Create App PIN",
        "confirm_app_pin": "Confirm App PIN",
        "pin_warning": "Never use your Airtel Money or TNM Mpamba PIN.",
        "pin_notice_1": "Remember your App PIN carefully.",
        "pin_notice_2": "PIN recovery is not yet available in this version.",
        "invalid_phone": "Enter a valid Malawi mobile number starting with 08 or 09, exactly 10 digits.",
        "invalid_pin": "App PIN must be exactly 4 digits.",
        "weak_pin": "Choose a less obvious App PIN.",
        "pin_mismatch": "The App PINs do not match.",
        "account_created": "Account created. You are now logged in.",
        "phone_exists": "An account with this phone number already exists.",
        "login_failed": "Phone number or App PIN is incorrect.",
        "login_locked": "Too many attempts. Please wait a few minutes and try again.",
        "login_success": "Logged in successfully.",
        "logout_success": "Logged out.",
        "cloud_save_note": "When logged in, your transactions are saved to your DolaYanga account.",
        "pin_recovery_note": "If you forget your App PIN, you may lose access to your account in this version.",
        "delete_account": "Delete Account",
        "delete_account_warning": "This permanently deletes your account and all your saved transactions.",
        "confirm_delete_account": "I understand and want to delete my account",
        "account_deleted": "Account deleted.",
        "admin": "Admin",
        "admin_note": "Admin tools are only visible for approved admin phone numbers.",
        "registered_users": "Registered Users",
        "delete_user_account": "Delete Selected User Account",
        "add_transaction": "Add New Transaction",
        "date": "Date",
        "network": "Network",
        "transaction_type": "Transaction Type",
        "amount": "Amount (MWK)",
        "note": "Note (optional)",
        "save": "Save Transaction",
        "save_with_icon": "Save Transaction",
        "amount_error": "Amount must be greater than 0.",
        "saved": "Transaction saved",
        "saved_message": "Transaction saved successfully.",
        "summary": "Summary",
        "combined": "Combined",
        "by_network": "By Network",
        "today_spending": "Today's Spending",
        "this_month": "This Month's Spending",
        "total_received": "Total Received",
        "total_spent": "Total Spent",
        "balance": "Estimated Balance",
        "monthly_breakdown": "Monthly Summary Breakdown",
        "monthly_insights_expander": "✨ Generate Monthly Insights",
        "monthly_insights_description": "Get AI-generated insights from your current monthly view (coming soon).",
        "monthly_insights_min_transactions": "AI insights require at least five transactions in the current view. Adjust your filters or add more transactions.",
        "monthly_insights_generate": "Generate Insights",
        "monthly_insights_placeholder": "Monthly Insights is coming soon. This button is a placeholder for the upcoming AI feature.",
        "monthly_insights_disclaimer": "AI insights are suggestions and may be inaccurate. Always verify before making financial decisions.",
        "transactions": "Transactions",
        "from": "From",
        "to": "To",
        "network_filter": "Network Filter",
        "all_networks": "All Networks",
        "no_transactions": "No transactions yet. Add your first one above.",
        "empty_welcome": "Welcome to DolaYanga!",
        "empty_description": "Track your Airtel Money and TNM Mpamba transactions in one place.",
        "empty_get_started": "Get started by:",
        "empty_add_first": "Adding your first transaction",
        "empty_try_demo": "Trying sample data to explore the app",
        "or": "or",
        "add_first_button": "Add My First Transaction",
        "try_demo_button": "Try Demo Data",
        "add_first_help": "Use the form below to add your first transaction.",
        "demo_loaded": "Demo data loaded successfully. Explore the app and try all features.",
        "demo_guest_only": "Demo data is only available in Guest Mode.",
        "no_filtered": "No transactions found in the selected filter.",
        "export": "Export Filtered Transactions (CSV)",
        "edit_delete": "Edit or Delete Transaction",
        "select_id": "Select Transaction ID",
        "select_transaction": "Select Transaction",
        "edit": "Edit",
        "delete": "Delete",
        "deleted": "Transaction deleted.",
        "edit_transaction": "Edit Transaction",
        "type": "Type",
        "save_changes": "Save Changes",
        "changes_saved": "Changes saved.",
        "cancel_edit": "Cancel Edit",
        "danger": "Danger Zone",
        "delete_all": "Delete ALL transactions",
        "reset": "Reset Everything",
        "reset_done": "All data cleared.",
        "confirm_reset": "This removes every saved transaction in this app.",
        "about": "About",
        "privacy": "Privacy Policy",
        "terms": "Terms and Conditions",
        "contact": "Contact Us",
        "contact_name": "Name",
        "contact_email": "Email",
        "contact_phone": "Phone (optional)",
        "contact_organization": "Organization (optional)",
        "contact_message": "Message",
        "send_message": "Send Message",
        "contact_saved": "Message saved for DolaCore at dolacorehq@gmail.com.",
        "contact_error": "Please enter your name, email, and message.",
        "contact_note": "Messages are for DolaCore at dolacorehq@gmail.com.",
        "contact_direct": "For questions, feedback, or support, contact DolaCore at dolacorehq@gmail.com.",
        "footer": "DolaYanga (c) 2026 - Simple mobile money tracking for Malawi",
        "about_text": """DolaYanga is a simple and secure transaction tracker built for Airtel Money and TNM Mpamba agents and users in Malawi.

It helps you record your transactions, track daily and monthly spending, monitor your balance, and export reports. Your data is private and only visible to you.

Made in Malawi for Malawians.""",
        "privacy_text": """Last updated: May 2026

At DolaYanga, we respect your privacy.

- We only collect the transactions you enter, including date, network, type, amount, and note.
- Your data is stored securely and is only accessible to you after logging in.
- We do not sell, share, or disclose your personal data to third parties.
- You can delete your account and all your data at any time.
- This app is not affiliated with Airtel Malawi or TNM.

For any questions, contact us at: dolacorehq@gmail.com""",
        "terms_text": """Last updated: May 2026

Welcome to DolaYanga. These Terms and Conditions explain the rules for using the app. By accessing or using DolaYanga, you agree to these Terms. If you do not agree, please do not use the app.

1. Purpose of the App

DolaYanga is a personal financial tracking tool designed for users in Malawi, especially users of Airtel Money and TNM Mpamba. The app allows users to record transactions such as money received, money sent, withdrawals, airtime purchases, bill payments, and merchant payments. The app provides summaries and insights based on user-entered data.

2. No Financial Service

DolaYanga is not a bank, mobile money provider, or financial institution. We do not hold or transfer money, process mobile money transactions, provide financial advice, or guarantee financial accuracy of records. All data in the app is manually entered by the user.

3. Accuracy of Information

All calculations are estimates only. Errors in input data may affect results. We do not guarantee that summaries, balances, or reports are 100% accurate. Users are responsible for verifying their own financial records.

4. Use at Your Own Risk

To the maximum extent permitted under applicable law in Malawi, the app is provided on an "as is" and "as available" basis. We do not guarantee uninterrupted or error-free operation. We are not responsible for loss of data, device failure, incorrect calculations, financial loss, business decisions, service interruptions, or downtime. Use of the app is entirely at your own risk.

5. Data Storage

Guest transactions may be temporary and may be lost unless an account is created. When account features are used, transaction data may be stored in a cloud database so users can access their records after logging in. We are not responsible for data loss caused by user actions, forgotten App PINs, device issues, or service interruptions.

6. User Accounts

Users may create an account using a Malawi phone number and App PIN. The App PIN is only for DolaYanga account security. Never use your Airtel Money or TNM Mpamba PIN. Users are responsible for remembering their App PIN and maintaining account security.

7. Acceptable Use

Users agree not to misuse the app for illegal activities, attempt to hack or disrupt the system, reverse engineer the app, intentionally input harmful or misleading data, or use the app in a way that harms other users or services.

8. Availability of Service

We aim to keep DolaYanga available, but the app may be updated, modified, or taken offline without notice. We do not guarantee continuous availability.

9. Intellectual Property

All content, branding, and design of DolaYanga belong to the creators of the app. You may not copy or redistribute the app as your own product or reuse branding or design without permission.

10. Third-Party Services

The app may rely on third-party services such as hosting platforms, databases, analytics, or storage tools. We are not responsible for failures or issues caused by third-party services.

11. Limitation of Liability

To the fullest extent permitted by law in Malawi, we are not liable for direct or indirect financial loss, loss of business or income, loss of data, or damages arising from use or inability to use the app.

12. Changes to Terms

We may update these Terms from time to time. Continued use of the app after changes means you accept the updated Terms.

13. Governing Law

These Terms are governed by the laws of Malawi. Any disputes will be handled under applicable Malawian legal frameworks.

14. Contact

If you have questions about these Terms, contact: dolacorehq@gmail.com""",
        "money_received": "Money Received",
        "money_sent": "Money Sent",
        "withdrawal": "Withdrawal",
        "airtime": "Airtime",
        "bill_payment": "Bill Payment",
        "merchant_payment": "Merchant Payment",
        "other": "Other",
    },
    "ny": {
        "language": "Chilankhulo",
        "title": "DolaYanga",
        "subtitle": "Tsatirani ma transaction a Airtel Money ndi TNM Mpamba",
        "small_subtitle": "Chida chosavuta cha ma mobile money ku Malawi",
        "guest_warning": "Guest Mode: ma transaction amene mwalowetsa panopa ndi akanthawi ndipo angatayike ngati simupanga akaunti.",
        "account_action": "Pangani Akaunti / Lowani",
        "not_ready": "Kupanga akaunti ndi kulowa mu akaunti zidzawonjezedwa mu public version.",
        "account": "Akaunti",
        "guest_mode": "Guest Mode",
        "logged_in_as": "Mwalowa ngati",
        "create_account": "Pangani Akaunti",
        "login": "Lowani",
        "logout": "Tulukani",
        "phone_number": "Nambala ya Foni",
        "app_pin": "App PIN",
        "create_app_pin": "Pangani App PIN",
        "confirm_app_pin": "Tsimikizani App PIN",
        "pin_warning": "Musagwiritse ntchito PIN ya Airtel Money kapena TNM Mpamba.",
        "pin_notice_1": "Kumbukirani App PIN yanu bwino.",
        "pin_notice_2": "Kubwezeretsa PIN sikulipo mu version iyi.",
        "invalid_phone": "Lowetsani nambala ya Malawi yoyamba ndi 08 kapena 09, manambala 10.",
        "invalid_pin": "App PIN iyenera kukhala manambala 4.",
        "weak_pin": "Sankhani App PIN yovutirapo pang'ono.",
        "pin_mismatch": "Ma App PIN sakufanana.",
        "account_created": "Akaunti yapangidwa. Mwalowa tsopano.",
        "phone_exists": "Akaunti ya nambala iyi ilipo kale.",
        "login_failed": "Nambala ya foni kapena App PIN si yolondola.",
        "login_locked": "Mwayesa kambirimbiri. Dikirani mphindi zingapo.",
        "login_success": "Mwalowa bwino.",
        "logout_success": "Mwatuluka.",
        "cloud_save_note": "Mukalowa mu akaunti, ma transaction anu amasungidwa ku akaunti ya DolaYanga.",
        "pin_recovery_note": "Mukayiwala App PIN yanu, mungataye mwayi wolowa mu akaunti mu version iyi.",
        "delete_account": "Chotsani Akaunti",
        "delete_account_warning": "Izi zichotsa akaunti yanu ndi ma transaction onse kwamuyaya.",
        "confirm_delete_account": "Ndikumvetsa ndipo ndikufuna kuchotsa akaunti yanga",
        "account_deleted": "Akaunti yachotsedwa.",
        "admin": "Admin",
        "admin_note": "Zida za admin zimaoneka kwa ma admin ovomerezeka okha.",
        "registered_users": "Ma User Olembetsa",
        "delete_user_account": "Chotsani Akaunti ya User Wosankhidwa",
        "add_transaction": "Onjezani Transaction Yatsopano",
        "date": "Tsiku",
        "network": "Network",
        "transaction_type": "Mtundu wa Transaction",
        "amount": "Ndalama (MWK)",
        "note": "Ndemanga (ngati mukufuna)",
        "save": "Sungani Transaction",
        "save_with_icon": "Sungani Transaction",
        "amount_error": "Ndalama ziyenera kukhala zoposa 0.",
        "saved": "Transaction yasungidwa",
        "saved_message": "Transaction yasungidwa bwino.",
        "summary": "Chidule",
        "combined": "Zonse Pamodzi",
        "by_network": "Mwa Network",
        "today_spending": "Zogwiritsidwa Ntchito Lero",
        "this_month": "Zogwiritsidwa Ntchito Mwezi Uno",
        "total_received": "Zonse Zolandilidwa",
        "total_spent": "Zonse Zogwiritsidwa Ntchito",
        "balance": "Balance Yoyerekeza",
        "monthly_breakdown": "Chidule cha Miyezi",
        "monthly_insights_expander": "✨ Pangani Zozindikira za Mwezi",
        "monthly_insights_description": "Pezani zozindikira (AI) kuchokera ku ma transaction a mwezi uno (ikubwera posachedwa).",
        "monthly_insights_min_transactions": "Zozindikira za AI zimafuna ma transaction osachepera asanu (5) mu view yomwe muli nayo pano. Sinthani ma filter kapena onjezani ma transaction.",
        "monthly_insights_generate": "Pangani Zozindikira",
        "monthly_insights_placeholder": "Monthly Insights ikubwera posachedwa. Batani ili ndi placeholder ya AI yomwe ikubwera.",
        "monthly_insights_disclaimer": "Zozindikira za AI ndi malingaliro ndipo zingakhale zolakwika. Nthawi zonse tsimikizani musanapange zisankho za ndalama.",
        "transactions": "Ma Transaction",
        "from": "Kuyambira",
        "to": "Mpaka",
        "network_filter": "Sankhani Network",
        "all_networks": "Ma Network Onse",
        "no_transactions": "Palibe transaction. Onjezani yoyamba pamwamba.",
        "empty_welcome": "Takulandirani ku DolaYanga!",
        "empty_description": "Tsatirani ma Airtel Money ndi TNM Mpamba transaction anu pamalo amodzi.",
        "empty_get_started": "Yambani ndi:",
        "empty_add_first": "Kulemba transaction yanu yoyamba",
        "empty_try_demo": "Kuyesa app ndi data yachitsanzo",
        "or": "kapena",
        "add_first_button": "Lembani Transaction Yoyamba",
        "try_demo_button": "Yesani Demo Data",
        "add_first_help": "Gwiritsani ntchito fomu yomwe ili pansi apa kuti mulembetse transaction yanu yoyamba.",
        "demo_loaded": "Demo data yalowetsedwa bwino. Yesani mbali zonse za app.",
        "demo_guest_only": "Demo data imagwira ntchito mu Guest Mode yokha.",
        "no_filtered": "Palibe transaction mu chisankho chimenechi.",
        "export": "Tumizani Ma Transaction (CSV)",
        "edit_delete": "Sinthani kapena Chotsani Transaction",
        "select_id": "Sankhani Transaction ID",
        "select_transaction": "Sankhani Transaction",
        "edit": "Sinthani",
        "delete": "Chotsani",
        "deleted": "Transaction yachotsedwa.",
        "edit_transaction": "Sinthani Transaction",
        "type": "Mtundu",
        "save_changes": "Sungani Zosintha",
        "changes_saved": "Zosintha zasungidwa.",
        "cancel_edit": "Siyani Kusintha",
        "danger": "Malo Oopsa",
        "delete_all": "Chotsani ma transaction ONSE",
        "reset": "Chotsani Zonse",
        "reset_done": "Data yonse yachotsedwa.",
        "confirm_reset": "Izi zichotsa ma transaction onse osungidwa mu app iyi.",
        "about": "Za DolaYanga",
        "privacy": "Mfundo Zazinsinsi",
        "terms": "Malamulo ndi Zogwiritsidwa",
        "contact": "Titumizireni",
        "contact_name": "Dzina",
        "contact_email": "Email",
        "contact_phone": "Foni (ngati mukufuna)",
        "contact_organization": "Bungwe kapena Bizinesi (ngati mukufuna)",
        "contact_message": "Uthenga",
        "send_message": "Tumizani Uthenga",
        "contact_saved": "Uthenga wasungidwa kwa DolaCore pa dolacorehq@gmail.com.",
        "contact_error": "Lowetsani dzina, email, ndi uthenga.",
        "contact_note": "Mauthenga ndi a DolaCore pa dolacorehq@gmail.com.",
        "contact_direct": "Ngati muli ndi mafunso kapena ndemanga, lemberani DolaCore pa dolacorehq@gmail.com.",
        "footer": "DolaYanga (c) 2026 - Chida chosavuta cha ma mobile money ku Malawi",
        "about_text": """DolaYanga ndi pulogalamu yosavuta komanso yotetezeka yolembera ndi kusunga mbiri ya ma transaction, yopangidwa makamaka kwa ogwiritsa ntchito ndi ma agent a Airtel Money ndi TNM Mpamba ku Malawi.

Imakuthandizani kulemba ma transaction anu, kutsata ndalama zomwe mwagwiritsa ntchito tsiku ndi mwezi, kuyang'anira ndalama zomwe mwatsala nazo, komanso kutulutsa ma report.

Zambiri zanu zimakhala zachinsinsi ndipo inu nokha ndi amene mungathe kuziwona.

Yapangidwa ku Malawi kwa a Malawi.""",
        "privacy_text": """Yasinthidwa Komaliza: Meyi 2026

Ku DolaYanga, timasamalira kwambiri zachinsinsi zanu.

- Timangosunga ma transaction omwe mwalemba nokha, kuphatikizapo tsiku, netiweki, mtundu wa transaction, kuchuluka kwa ndalama, ndi ndemanga.
- Zambiri zanu zimasungidwa motetezeka ndipo inu nokha ndi amene mungathe kuzipeza mukalowa mu akaunti yanu.
- Sitigulitsa, kugawana, kapena kupereka zambiri zanu kwa anthu kapena mabungwe ena.
- Mungathe kufufuta akaunti yanu ndi zonse zomwe mwasunga nthawi iliyonse.
- Pulogalamuyi ilibe mgwirizano uliwonse ndi Airtel Malawi kapena TNM.

Ngati muli ndi mafunso, lemberani ku: dolacorehq@gmail.com""",
        "terms_text": """Yasinthidwa Komaliza: Meyi 2026

Takulandirani ku DolaYanga. Migwirizano ndi Malamulo awa akufotokoza malamulo ogwiritsa ntchito pulogalamuyi. Pogwiritsa ntchito kapena kulowa mu DolaYanga, mukuvomereza Migwirizano iyi. Ngati simukuvomereza, chonde musagwiritse ntchito pulogalamuyi.

1. Cholinga cha Pulogalamuyi

DolaYanga ndi chida chotsatirira ndalama zanu chomwe chapangidwira ogwiritsa ntchito ku Malawi, makamaka ogwiritsa ntchito Airtel Money ndi TNM Mpamba.

Pulogalamuyi imalola ogwiritsa ntchito kulemba ma transaction monga ndalama zolandiridwa, ndalama zotumizidwa, kutapa ndalama, kugula airtime, kulipira ma bill, komanso malipiro kwa amalonda.

Pulogalamuyi imapereka mwachidule komanso kuwunika kwa ndalama kutengera zomwe ogwiritsa ntchito alemba.

2. Si Bungwe La Zachuma

DolaYanga si banki, kampani ya mobile money, kapena bungwe la zachuma.

Sitimasunga kapena kutumiza ndalama, sitimachita ma transaction a mobile money, sitimapereka malangizo a zachuma, ndipo sitikutsimikizira kulondola kwa mbiri ya ndalama.

Zambiri zonse zomwe zili mu pulogalamuyi zimalowetsedwa ndi wogwiritsa ntchito yekha.

3. Kulondola kwa Zambiri

Mawerengedwe onse omwe pulogalamuyi imapereka ndi oyerekeza basi.

Zolakwika polowetsa deta zingakhudze zotsatira zake.

Sititsimikizira kuti ma summary, ma balance kapena ma report ndi olondola pa 100%.

Ogwiritsa ntchito ali ndi udindo wowunika ndi kutsimikizira mbiri yawo ya ndalama.

4. Kugwiritsa Ntchito pa Chiwopsezo Chanu

Malinga ndi malamulo ogwira ntchito ku Malawi, pulogalamuyi imaperekedwa momhow ilili ("as is") komanso momhow ikupezekera ("as available").

Sititsimikizira kuti pulogalamuyi izigwira ntchito nthawi zonse popanda zolakwika kapena kusokonezeka.

Sitikhala ndi udindo pa kutayika kwa deta, kulephera kwa chipangizo, mawerengedwe olakwika, kutayika kwa ndalama, zisankho zamabizinesi, kusokonezeka kwa ntchito, kapena nthawi yomwe pulogalamuyi siyikupezeka.

Kugwiritsa ntchito pulogalamuyi ndi pa chiwopsezo chanu nokha.

5. Kusungidwa kwa Deta

Ma transaction a alendo (Guest Mode) akhoza kukhala akanthawi ndipo angatayike ngati akaunti sinalengedwe.

Mukagwiritsa ntchito akaunti, deta ya ma transaction ikhoza kusungidwa pa cloud database kuti muthe kupeza mbiri yanu mukalowanso.

Sitili ndi udindo pa kutayika kwa deta komwe kwachitika chifukwa cha zochita za wogwiritsa ntchito, kuyiwala App PIN, mavuto a chipangizo, kapena kusokonezeka kwa ntchito.

6. Ma Akaunti a Ogwiritsa Ntchito

Ogwiritsa ntchito akhoza kupanga akaunti pogwiritsa ntchito nambala ya foni ya ku Malawi ndi App PIN.

App PIN imagwiritsidwa ntchito poteteza akaunti ya DolaYanga yokha.

Musagwiritse ntchito PIN yanu ya Airtel Money kapena TNM Mpamba.

Ogwiritsa ntchito ali ndi udindo wokumbukira App PIN yawo komanso kusunga chitetezo cha akaunti yawo.

7. Kugwiritsa Ntchito Moyenera

Ogwiritsa ntchito amavomereza kuti sadzagwiritsa ntchito pulogalamuyi pa ntchito zosaloledwa ndi malamulo, kuyesa kuthyolako kapena kusokoneza dongosolo, kusanthula kapena kukopera momhow pulogalamuyi imagwirira ntchito (reverse engineering), kulowetsa deta yabodza kapena yowononga mwadala, kapena kugwiritsa ntchito pulogalamuyi m'njira yomwe ingawononge ogwiritsa ntchito ena kapena ntchito zina.

8. Kupezeka kwa Ntchito

Timayesetsa kuti DolaYanga ikhale yopezeka nthawi zonse, koma pulogalamuyi ikhoza kusinthidwa, kukonzedwa, kapena kuyimitsidwa nthawi iliyonse popanda chenjezo.

Sititsimikizira kuti idzapezeka nthawi zonse.

9. Umwini wa Zinthu za Pulogalamuyi

Zonse zomwe zili mu DolaYanga, kuphatikizapo dzina, chizindikiro (branding), ndi kapangidwe ka pulogalamuyi, ndi za eni ake a pulogalamuyi.

Simuloledwa kukopera, kugawira ena, kapena kugwiritsa ntchito dzina kapena kapangidwe ka pulogalamuyi popanda chilolezo.

10. Ntchito za Mabungwe Ena

Pulogalamuyi ikhoza kudalira ntchito za mabungwe ena monga ma hosting platform, ma database, ma analytics service, kapena zida zosungira deta.

Sitikhala ndi udindo pa mavuto kapena kulephera komwe kwabwera chifukwa cha ntchito za mabungwe amenewa.

11. Malire a Udindo

Malinga ndi malamulo a ku Malawi, sitili ndi udindo pa kutayika kwa ndalama mwachindunji kapena mosalunjika, kutayika kwa bizinesi kapena ndalama zolowa, kutayika kwa deta, kapena kuwonongeka kulikonse komwe kwabwera chifukwa chogwiritsa ntchito kapena kulephera kugwiritsa ntchito pulogalamuyi.

12. Kusintha kwa Migwirizano

Tingasinthe Migwirizano iyi nthawi ndi nthawi.

Kupitiliza kugwiritsa ntchito pulogalamuyi pambuyo pa kusintha kumatanthauza kuti mukuvomereza Migwirizano yatsopano.

13. Lamulo Loyang'anira

Migwirizano iyi imayang'aniridwa ndi malamulo a dziko la Malawi.

Mikangano iliyonse idzathetsedwa motsatira malamulo ogwira ntchito ku Malawi.

14. Kulumikizana Nafe

Ngati muli ndi mafunso okhudza Migwirizano iyi, lemberani ku:

dolacorehq@gmail.com""",
        "money_received": "Ndalama Zolandilidwa",
        "money_sent": "Ndalama Zotumizidwa",
        "withdrawal": "Kuchotsa Ndalama",
        "airtime": "Airtime",
        "bill_payment": "Kulipira Bilu",
        "merchant_payment": "Kulipira ku Bizinesi",
        "other": "Zina",
    },
}

TYPE_TRANSLATION_KEYS = {
    "Money Received": "money_received",
    "Money Sent": "money_sent",
    "Withdrawal": "withdrawal",
    "Airtime": "airtime",
    "Bill Payment": "bill_payment",
    "Merchant Payment": "merchant_payment",
    "Other": "other",
}

st.set_page_config(
    page_title="DolaYanga",
    page_icon="MWK",
    layout="centered",
)

logo_path = Path(__file__).parent / "Dola Yanga logo.png"
if logo_path.exists():
    st.logo(str(logo_path), size="large")   

# Hide Streamlit footer and menu
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

def get_required_secret(key):
    value = st.secrets.get(key, "")
    if not value:
        raise RuntimeError(f"Missing {key} in .streamlit/secrets.toml.")

    return value

SUPABASE_REST_URL = get_required_secret("SUPABASE_REST_URL").rstrip("/")
SUPABASE_FUNCTION_URL = get_required_secret("SUPABASE_FUNCTION_URL").rstrip("/")
SUPABASE_ANON_KEY = get_required_secret("SUPABASE_ANON_KEY")
SUPABASE_FUNCTION_SECRET = get_required_secret("SUPABASE_FUNCTION_SECRET")

def t(key):
    return TRANSLATIONS[st.session_state.language][key]

def type_label(transaction_type):
    return t(TYPE_TRANSLATION_KEYS[transaction_type])

def normalize_phone(phone_number):
    return re.sub(r"\D", "", phone_number.strip())

def is_valid_malawi_phone(phone_number):
    return bool(re.fullmatch(r"0[89]\d{8}", normalize_phone(phone_number)))

def is_valid_pin(pin):
    return bool(re.fullmatch(r"\d{4}", pin.strip()))

def hash_pin(pin, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()

    hashed_pin = hashlib.pbkdf2_hmac(
        "sha256",
        pin.encode("utf-8"),
        bytes.fromhex(salt),
        PIN_HASH_ITERATIONS,
    ).hex()

    return salt, hashed_pin

def verify_pin(pin, salt, expected_hash):
    _, actual_hash = hash_pin(pin, salt)
    return hmac.compare_digest(actual_hash, expected_hash)

def parse_supabase_time(value):
    if not value:
        return None

    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def supabase_headers(extra_headers=None):
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
    }

    if extra_headers:
        headers.update(extra_headers)

    return headers

def supabase_request(table, method="GET", params=None, payload=None):
    query = f"?{urllib.parse.urlencode(params)}" if params else ""
    url = f"{SUPABASE_REST_URL.rstrip('/')}/{table}{query}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = supabase_headers({"Prefer": "return=representation"})
    request = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else []
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8")
        raise RuntimeError(f"Supabase error {error.code}: {details}") from error

def record_event(event_name, user=None):
    supabase_request(
        "events",
        method="POST",
        payload={
            "event_name": event_name,
            "app_user_id": user["id"] if user else None,
            "phone_number": user["phone_number"] if user else None,
        },
    )

def get_table_count(table, params=None):
    query = f"?{urllib.parse.urlencode(params)}" if params else ""
    url = f"{SUPABASE_REST_URL.rstrip('/')}/{table}{query}"
    request = urllib.request.Request(
        url,
        headers=supabase_headers({
            "Prefer": "count=exact",
            "Range": "0-0",
        }),
        method="GET",
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        content_range = response.headers.get("Content-Range", "0-0/0")
        return int(content_range.split("/")[-1])

def load_admin_analytics():
    return {
        "total_users": get_table_count("app_users", {"select": "id"}),
        "total_transactions": get_table_count("transactions", {"select": "id"}),
        "total_logins": get_table_count("events", {
            "select": "id",
            "event_name": "eq.login_success",
        }),
        "total_events": get_table_count("events", {"select": "id"}),
    }

def get_function_secret():
    return SUPABASE_FUNCTION_SECRET

def call_delete_account_function(user):
    payload = {
        "user_id": user["id"],
        "phone_number": user["phone_number"],
        "confirmation": "DELETE_ACCOUNT",
    }
    data = json.dumps(payload).encode("utf-8")
    secret = get_function_secret()
    headers = {
        "Content-Type": "application/json",
        "apikey": secret,
        "apiKey": secret,
        "Authorization": f"Bearer {secret}",
    }
    request = urllib.request.Request(
        SUPABASE_FUNCTION_URL,
        data=data,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8")
        raise RuntimeError(f"Account deletion failed: {details}") from error

def get_user_by_phone(phone_number):
    users = supabase_request(
        "app_users",
        params={
            "select": "*",
            "phone_number": f"eq.{phone_number}",
            "limit": "1",
        },
    )
    return users[0] if users else None

def get_user_by_id(user_id):
    users = supabase_request(
        "app_users",
        params={
            "select": "*",
            "id": f"eq.{user_id}",
            "limit": "1",
        },
    )
    return users[0] if users else None

def update_user(user_id, values):
    return supabase_request(
        "app_users",
        method="PATCH",
        params={"id": f"eq.{user_id}"},
        payload=values,
    )

def create_user(phone_number, pin):
    salt, pin_hash = hash_pin(pin)
    created_users = supabase_request(
        "app_users",
        method="POST",
        payload={
            "phone_number": phone_number,
            "pin_salt": salt,
            "pin_hash": pin_hash,
            "is_admin": phone_number in ADMIN_PHONE_NUMBERS,
        },
    )
    user = created_users[0]
    record_event("account_created", user)
    return user

def login_user(phone_number, pin):
    user = get_user_by_phone(phone_number)

    if not user:
        time.sleep(0.5)
        return False, t("login_failed"), None

    locked_until = parse_supabase_time(user.get("locked_until"))
    if locked_until and locked_until > datetime.now(timezone.utc):
        return False, t("login_locked"), None

    if verify_pin(pin, user["pin_salt"], user["pin_hash"]):
        now = datetime.now(timezone.utc).isoformat()
        update_user(user["id"], {
            "failed_attempts": 0,
            "locked_until": None,
            "last_login": now,
            "updated_at": now,
        })
        user["failed_attempts"] = 0
        user["locked_until"] = None
        user["last_login"] = now
        record_event("login_success", user)
        return True, t("login_success"), user

    failed_attempts = int(user.get("failed_attempts") or 0) + 1
    lock_value = None
    if failed_attempts >= MAX_LOGIN_ATTEMPTS:
        lock_value = (datetime.now(timezone.utc) + timedelta(minutes=LOCK_MINUTES)).isoformat()

    update_user(user["id"], {
        "failed_attempts": failed_attempts,
        "locked_until": lock_value,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })
    return False, t("login_failed"), None

def cloud_transactions_to_df(rows):
    records = []
    for row in rows:
        records.append({
            "id": row["id"],
            "date": row["transaction_date"],
            "network": row["network"],
            "transaction_type": row["transaction_type"],
            "amount": row["amount"],
            "note": row.get("note") or "",
            "created_at": row.get("created_at"),
        })

    return pd.DataFrame(records, columns=["id", "date", "network", "transaction_type", "amount", "note", "created_at"])

def load_cloud_transactions(user):
    rows = supabase_request(
        "transactions",
        params={
            "select": "*",
            "app_user_id": f"eq.{user['id']}",
            "order": "transaction_date.desc,created_at.desc",
        },
    )

    df = cloud_transactions_to_df(rows)

    if not df.empty:
        df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
        )
        
        df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
        )

        df = df.sort_values(
            ["date", "created_at"],
            ascending=[False, False]
        ).reset_index(drop=True)
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    return df

def insert_cloud_transaction(user, transaction):
    rows = supabase_request(
        "transactions",
        method="POST",
        payload={
            "app_user_id": user["id"],
            "phone_number": user["phone_number"],
            "transaction_date": transaction["date"],
            "network": transaction["network"],
            "transaction_type": transaction["transaction_type"],
            "amount": transaction["amount"],
            "note": transaction["note"],
        },
    )
    return rows[0]

def update_cloud_transaction(user, transaction_id, values):
    return supabase_request(
        "transactions",
        method="PATCH",
        params={
            "id": f"eq.{transaction_id}",
            "app_user_id": f"eq.{user['id']}",
        },
        payload={
            "transaction_date": values["date"],
            "network": values["network"],
            "transaction_type": values["transaction_type"],
            "amount": values["amount"],
            "note": values["note"],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

def delete_cloud_transaction(user, transaction_id):
    return supabase_request(
        "transactions",
        method="DELETE",
        params={
            "id": f"eq.{transaction_id}",
            "app_user_id": f"eq.{user['id']}",
        },
    )

def delete_account_and_transactions(user):
    if not user:
        raise ValueError("User record not found.")

    if "phone_number" not in user:
        full_user = get_user_by_id(user["id"])

        if not full_user:
            raise ValueError("Unable to load user details.")

        user = full_user

    record_event("account_deleted", user)
    call_delete_account_function(user)

def load_registered_users():
    return supabase_request(
        "app_users",
        params={
            "select": "id,phone_number,created_at,last_login,is_admin",
            "order": "created_at.desc",
        },
    )

def load_transactions():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["id", "date", "network", "transaction_type", "amount", "note"])

    expected_columns = ["id", "date", "network", "transaction_type", "amount", "note"]
    for column in expected_columns:
        if column not in df.columns:
            df[column] = ""

    df = df[expected_columns]

    if not df.empty:
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
        df = df.dropna(subset=["id"]).copy()
        df["id"] = df["id"].astype(int)
        
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["date"] = df["date"].fillna(pd.Timestamp(date.today()))
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        
        df["network"] = df["network"].where(df["network"].isin(NETWORKS), NETWORKS[0])
        df["transaction_type"] = df["transaction_type"].where(
            df["transaction_type"].isin(TRANSACTION_TYPES), "Other"
        )
        df["note"] = df["note"].fillna("")
        
        df = df.sort_values(["date", "id"], ascending=[False, False]).reset_index(drop=True)
        
    else:
        df = empty_transactions_df()

    return df.reset_index(drop=True)

def save_transactions(df):
    df.to_csv(DATA_FILE, index=False)

def save_contact_message(name, email, phone, organization, message):
    new_message = pd.DataFrame([{
        "date": date.today().isoformat(),
        "recipient_email": "dolacorehq@gmail.com",
        "name": name.strip(),
        "email": email.strip(),
        "phone": phone.strip(),
        "organization": organization.strip(),
        "message": message.strip(),
    }])

    if CONTACT_FILE.exists():
        contact_messages = pd.read_csv(CONTACT_FILE)
        contact_messages = pd.concat([contact_messages, new_message], ignore_index=True)
    else:
        contact_messages = new_message

    contact_messages.to_csv(CONTACT_FILE, index=False)

def empty_transactions_df():
    return pd.DataFrame(columns=["id", "date", "network", "transaction_type", "amount", "note"])

def generate_demo_transactions():
    today = date.today()
    demo_rows = [
        (1, today - timedelta(days=1), "Airtel Money", "Money Received", 120000, "Salary"),
        (2, today - timedelta(days=1), "Airtel Money", "Airtime", 2500, "Airtime bundle"),
        (3, today - timedelta(days=2), "TNM Mpamba", "Merchant Payment", 15000, "Market purchase"),
        (4, today - timedelta(days=3), "Airtel Money", "Money Sent", 20000, "Transfer to family"),
        (5, today - timedelta(days=4), "TNM Mpamba", "Bill Payment", 10000, "Electricity token"),
        (6, today - timedelta(days=5), "Airtel Money", "Withdrawal", 50000, "Cash withdrawal"),
        (7, today - timedelta(days=6), "TNM Mpamba", "Money Received", 75000, "Business payment"),
        (8, today - timedelta(days=8), "Airtel Money", "Merchant Payment", 5000, "Fuel"),
        (9, today - timedelta(days=10), "TNM Mpamba", "Airtime", 1000, "Internet bundle"),
        (10, today - timedelta(days=12), "Airtel Money", "Money Sent", 15000, "School fees"),
        (11, today - timedelta(days=14), "TNM Mpamba", "Merchant Payment", 20000, "Farm supplies"),
        (12, today - timedelta(days=16), "Airtel Money", "Money Received", 50000, "Business payment"),
        (13, today - timedelta(days=18), "TNM Mpamba", "Withdrawal", 20000, "Cash withdrawal"),
        (14, today - timedelta(days=20), "Airtel Money", "Bill Payment", 10000, "Electricity token"),
        (15, today - timedelta(days=22), "TNM Mpamba", "Money Sent", 5000, "Transfer to family"),
        (16, today - timedelta(days=24), "Airtel Money", "Merchant Payment", 2500, "Market purchase"),
        (17, today - timedelta(days=26), "TNM Mpamba", "Money Received", 75000, "Business payment"),
        (18, today - timedelta(days=29), "Airtel Money", "Airtime", 1000, "Airtime bundle"),
    ]

    return pd.DataFrame(
        [{
            "id": row_id,
            "date": row_date.isoformat(),
            "network": network,
            "transaction_type": transaction_type,
            "amount": amount,
            "note": note,
        } for row_id, row_date, network, transaction_type, amount, note in demo_rows],
        columns=["id", "date", "network", "transaction_type", "amount", "note"],
    )

def format_money(value):
    return f"{float(value):,.0f}"

def format_display_amount(row):
    amount = format_money(row["amount"])
    if row["transaction_type"] == "Money Received":
        return f"🟢 +MWK {amount}"

    return f"🔴 -MWK {amount}"

def add_display_numbers(df):
    display_df = df.copy().reset_index(drop=True)
    display_df.insert(0, "display_id", range(1, len(display_df) + 1))
    return display_df

# NEW SAFE HELPER FUNCTION - improved
def safe_id(val):
    """Safely handle any ID type (int, str, UUID, NaN, etc.)"""
    if pd.isna(val) or val is None or val == "" or str(val).strip() == "":
        return "?"
    return str(val)

def calculate_summary(df):
    if df.empty:
        return 0, 0, 0, 0, 0

    data = df.copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    today = pd.Timestamp(date.today())
    spending_mask = data["transaction_type"].isin(SPENDING_TYPES)

    today_spending = data[
        (data["date"].dt.date == today.date()) & spending_mask
    ]["amount"].sum()

    month_spending = data[
        (data["date"].dt.month == today.month)
        & (data["date"].dt.year == today.year)
        & spending_mask
    ]["amount"].sum()

    total_received = data[data["transaction_type"] == "Money Received"]["amount"].sum()
    total_spent = data[spending_mask]["amount"].sum()
    balance = total_received - total_spent

    return today_spending, month_spending, total_received, total_spent, balance

def show_summary_metrics(df):
    today_spending, month_spending, total_received, total_spent, balance = calculate_summary(df)

    def summary_card(label, value, color, background):
        st.markdown(
            f"""
            <div style="
                border-left: 5px solid {color};
                background: {background};
                padding: 0.85rem 0.95rem;
                border-radius: 8px;
                margin-bottom: 0.7rem;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            ">
                <div style="font-size: 0.82rem; color: #4b5563; margin-bottom: 0.25rem;">{label}</div>
                <div style="font-size: 1.35rem; font-weight: 700; color: {color}; line-height: 1.2;">
                    MWK {format_money(value)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    balance_color = "#15803d" if balance >= 0 else "#b91c1c"
    balance_background = "#f0fdf4" if balance >= 0 else "#fef2f2"

    col1, col2 = st.columns(2)
    with col1:
        summary_card(t("today_spending"), today_spending, "#b45309", "#fffbeb")
        summary_card(t("total_received"), total_received, "#15803d", "#f0fdf4")
    with col2:
        summary_card(t("this_month"), month_spending, "#1d4ed8", "#eff6ff")
        summary_card(t("balance"), balance, balance_color, balance_background)

    st.markdown(
        f"""
        <div style="font-size: 0.95rem; color: #b91c1c; font-weight: 600; margin: 0.15rem 0 0.8rem 0;">
            {t('total_spent')}: MWK {format_money(total_spent)}
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_empty_state_onboarding():
    with st.container(border=True):
        st.subheader(f"👋 {t('empty_welcome')}")
        st.write(t("empty_description"))
        st.write(t("empty_get_started"))
        st.write(f"✅ {t('empty_add_first')}")
        st.write(t("or"))
        st.write(f"✅ {t('empty_try_demo')}")

        empty_col1, empty_col2 = st.columns(2)
        if empty_col1.button(t("add_first_button"), use_container_width=True):
            st.info(t("add_first_help"))

        if empty_col2.button(t("try_demo_button"), use_container_width=True):
            if st.session_state.current_user:
                st.toast(t("demo_guest_only"))
            else:
                st.session_state.transactions = generate_demo_transactions()
                st.session_state.demo_mode = True
                st.session_state.save_message = t("demo_loaded")
                st.rerun()

if "language" not in st.session_state:
    st.session_state.language = "en"

if "last_network" not in st.session_state:
    st.session_state.last_network = NETWORKS[0]

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
    st.session_state.edit_id = None

if "save_message" not in st.session_state:
    st.session_state.save_message = ""

if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "transactions" not in st.session_state:
    st.session_state.transactions = empty_transactions_df()

# Initialize filter state with stable, language-agnostic values.
# This prevents translated labels (e.g., "All Networks") from being stored as filter values and breaking filtering on reruns.
if "start_date" not in st.session_state:
    st.session_state.start_date = date.today().replace(day=1)

if "end_date" not in st.session_state:
    st.session_state.end_date = date.today()

if "network_filter_value" not in st.session_state:
    st.session_state.network_filter_value = "__all__"

transactions = st.session_state.transactions

language_spacer_col, language_button_col = st.columns([6, 1])

with language_button_col:
    next_language = "ny" if st.session_state.language == "en" else "en"
    language_label = "NY" if st.session_state.language == "en" else "EN"

    if st.button(f"🌐 {language_label}"):
        st.session_state.language = next_language
        st.rerun()

header_logo_col, header_title_col = st.columns([1, 4])

with header_logo_col:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)
    else:
        st.markdown("### MWK")

with header_title_col:
    st.markdown(
        f"""
        <h1 style="margin: 0 0 2px 0; color: #006400; line-height: 1.05;">{t("title")}</h1>
        <p style="margin: 0; color: #374151; font-size: 1.08rem; line-height: 1.25;">{t("subtitle")}</p>
        <p style="margin: 2px 0 0 0; color: #6b7280; font-size: 0.95rem; line-height: 1.2;">{t("small_subtitle")}</p>
        """,
        unsafe_allow_html=True,
    )

if st.session_state.current_user:
    st.success(f"{t('logged_in_as')}: {st.session_state.current_user['phone_number']}")
    st.caption(t("cloud_save_note"))
else:
    st.warning(t("guest_warning"))

with st.expander(t("account"), expanded=False):
    st.warning(t("pin_warning"))

    if st.session_state.current_user:
        if st.button(t("logout"), use_container_width=True):
            st.session_state.current_user = None
            st.session_state.transactions = empty_transactions_df()
            st.session_state.demo_mode = False
            st.session_state.edit_mode = False
            st.session_state.edit_id = None
            st.session_state.save_message = t("logout_success")
            st.rerun()

        st.subheader(t("delete_account"))
        st.warning(t("delete_account_warning"))
        if st.checkbox(t("confirm_delete_account")):
            if st.button(t("delete_account"), use_container_width=True):
                try:
                    delete_account_and_transactions(st.session_state.current_user)
                    st.session_state.current_user = None
                    st.session_state.transactions = empty_transactions_df()
                    st.session_state.demo_mode = False
                    st.session_state.save_message = t("account_deleted")
                    st.rerun()
                except Exception as error:
                    st.error(str(error))

        if st.session_state.current_user.get("is_admin"):
            st.subheader(t("admin"))
            st.caption(t("admin_note"))
            try:
                analytics = load_admin_analytics()
                admin_col1, admin_col2 = st.columns(2)
                admin_col1.metric("Total users", analytics["total_users"])
                admin_col2.metric("Total transactions", analytics["total_transactions"])
                admin_col1.metric("Total logins", analytics["total_logins"])
                admin_col2.metric("Total events", analytics["total_events"])

                users = load_registered_users()
                if users:
                    users_df = pd.DataFrame(users)
                    users_df = users_df[["phone_number", "created_at", "last_login", "is_admin", "id"]]
                    st.dataframe(users_df, use_container_width=True, hide_index=True)
                    selected_user_id = st.selectbox(
                        t("registered_users"),
                        users_df["id"].tolist(),
                    )
                    if st.button(t("delete_user_account"), use_container_width=True):
                        selected_user = get_user_by_id(selected_user_id)

                        if selected_user:
                            delete_account_and_transactions(selected_user)
                            st.session_state.save_message = t("account_deleted")
                            st.rerun()
                        else:
                            st.error("User not found.")
                else:
                    st.info(t("no_filtered"))
            except Exception as error:
                st.error(str(error))
    else:
        login_tab, signup_tab = st.tabs([t("login"), t("create_account")])

        with login_tab:
            st.caption(t("pin_recovery_note"))
            with st.form("login_form"):
                login_phone = st.text_input(t("phone_number"), key="login_phone")
                login_pin = st.text_input(t("app_pin"), type="password", key="login_pin")

                if st.form_submit_button(t("login"), use_container_width=True):
                    phone_number = normalize_phone(login_phone)
                    if not is_valid_malawi_phone(phone_number):
                        st.error(t("invalid_phone"))
                    elif not is_valid_pin(login_pin):
                        st.error(t("invalid_pin"))
                    else:
                        try:
                            ok, message, user = login_user(phone_number, login_pin.strip())
                            if ok:
                                st.session_state.current_user = user
                                st.session_state.transactions = load_cloud_transactions(user)
                                st.session_state.demo_mode = False
                                st.session_state.save_message = message
                                st.rerun()
                            else:
                                st.error(message)
                        except Exception as error:
                            st.error(str(error))

        with signup_tab:
            st.caption(t("pin_notice_1"))
            st.caption(t("pin_notice_2"))
            st.warning(t("pin_warning"))

            with st.form("signup_form"):
                signup_phone = st.text_input(t("phone_number"), key="signup_phone")
                signup_pin = st.text_input(t("create_app_pin"), type="password", key="signup_pin")
                confirm_pin = st.text_input(t("confirm_app_pin"), type="password", key="confirm_pin")

                if st.form_submit_button(t("create_account"), use_container_width=True):
                    phone_number = normalize_phone(signup_phone)
                    pin = signup_pin.strip()

                    if not is_valid_malawi_phone(phone_number):
                        st.error(t("invalid_phone"))
                    elif not is_valid_pin(pin):
                        st.error(t("invalid_pin"))
                    elif pin in WEAK_PINS:
                        st.error(t("weak_pin"))
                    elif pin != confirm_pin.strip():
                        st.error(t("pin_mismatch"))
                    else:
                        try:
                            if get_user_by_phone(phone_number):
                                st.error(t("phone_exists"))
                            else:
                                user = create_user(phone_number, pin)
                                st.session_state.current_user = user
                                st.session_state.transactions = load_cloud_transactions(user)
                                st.session_state.demo_mode = False
                                st.session_state.save_message = t("account_created")
                                st.rerun()
                        except Exception as error:
                            st.error(str(error))

if st.session_state.save_message:
    st.toast(st.session_state.save_message, icon="✅")
    st.session_state.save_message = ""

if transactions.empty:
    render_empty_state_onboarding()

st.header(t("add_transaction"))

with st.form("transaction_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        transaction_date = st.date_input(
            t("date"),
            value=date.today(),
            max_value=date.today(),
            format=DATE_INPUT_FORMAT,
        )
        network = st.selectbox(
            t("network"),
            NETWORKS,
            index=NETWORKS.index(st.session_state.last_network),
        )

    with col2:
        type_options = TRANSACTION_TYPES
        selected_type_label = st.selectbox(
            t("transaction_type"),
            [type_label(item) for item in type_options],
        )
        transaction_type = type_options[[type_label(item) for item in type_options].index(selected_type_label)]
        amount = st.number_input(
            t("amount"),
            min_value=0.0,
            step=100.0,
            value=1000.0,
        )

    note = st.text_input(t("note"))

    if st.form_submit_button(f"💾 {t('save_with_icon')}", type="primary"):
        if amount <= 0:
            st.error(t("amount_error"))
        else:
            next_id = None
            if not st.session_state.current_user:
                if transactions.empty:
                    next_id = 1
                else:
                    next_id = int(transactions["id"].max()) + 1

            new_transaction = {
                "id": next_id,
                "date": transaction_date.isoformat(),
                "network": network,
                "transaction_type": transaction_type,
                "amount": float(amount),
                "note": note.strip(),
            }

            try:
                if st.session_state.current_user:
                    insert_cloud_transaction(st.session_state.current_user, new_transaction)
                    record_event("transaction_added", st.session_state.current_user)
                    updated_transactions = load_cloud_transactions(st.session_state.current_user)
                else:
                    updated_transactions = pd.concat(
                        [transactions, pd.DataFrame([new_transaction])],
                        ignore_index=True,
                    )
                    updated_transactions["date"] = pd.to_datetime(updated_transactions["date"])
                    updated_transactions = updated_transactions.sort_values(
                        ["date", "id"],
                        ascending=[False, False],
                    ).reset_index(drop=True)
                    updated_transactions["date"] = updated_transactions["date"].dt.strftime("%Y-%m-%d")

                st.session_state.transactions = updated_transactions
                st.session_state.last_network = network
                st.session_state.save_message = t("saved_message")
                st.rerun()
            except Exception as error:
                st.error(str(error))

if transactions.empty:
    df_display = pd.DataFrame(columns=["id", "date", "network", "transaction_type", "amount", "note"])
else:
    st.header(t("summary"))
    df_display = transactions.copy()
    df_display["date"] = pd.to_datetime(
        df_display["date"],
        errors="coerce"
    )

    if "created_at" in df_display.columns:
        df_display["created_at"] = pd.to_datetime(
            df_display["created_at"],
            errors="coerce"
        )

        df_display = df_display.sort_values(
            ["date", "created_at"],
            ascending=[False, False]
        ).reset_index(drop=True)
    else:
        df_display = df_display.sort_values(
            ["date", "id"],
            ascending=[False, False]
        ).reset_index(drop=True)
    
    st.subheader(t("combined"))
    show_summary_metrics(df_display)

    st.subheader(t("by_network"))
    for network_name in NETWORKS:
        with st.expander(network_name, expanded=True):
            network_df = df_display[df_display["network"] == network_name]
            if network_df.empty:
                st.info(t("no_filtered"))
            else:
                show_summary_metrics(network_df)

    with st.expander(t("monthly_breakdown"), expanded=False):
        monthly_df = df_display.copy()
        monthly_df["month_key"] = monthly_df["date"].dt.to_period("M").astype(str)
        monthly_df["Month"] = monthly_df["date"].dt.strftime("%B %Y")
        monthly_rows = []
        for _, group in monthly_df.sort_values("month_key").groupby("month_key", sort=False):
            _, _, received, spent, balance = calculate_summary(group)
            monthly_rows.append({
                "Month": group["Month"].iloc[0],
                t("total_received"): format_money(received),
                t("total_spent"): format_money(spent),
                t("balance"): format_money(balance),
            })

        if monthly_rows:
            st.dataframe(pd.DataFrame(monthly_rows), use_container_width=True, hide_index=True)
        else:
            st.info(t("no_filtered"))

with st.expander(t("monthly_insights_expander"), expanded=False):
    st.caption(t("monthly_insights_description"))

    visible_df = df_display.copy()
    if not visible_df.empty:
        selected_network = st.session_state.get("network_filter_value", "__all__")
        if selected_network != "__all__":
            visible_df = visible_df[visible_df["network"] == selected_network]

        start_date_value = st.session_state.get("start_date", date.today().replace(day=1))
        end_date_value = st.session_state.get("end_date", date.today())
        visible_df = visible_df[
            (visible_df["date"].dt.date >= start_date_value)
            & (visible_df["date"].dt.date <= end_date_value)
        ]

    if len(visible_df) < 5:
        st.info(t("monthly_insights_min_transactions"))
    else:
        if st.button(t("monthly_insights_generate"), type="primary", use_container_width=True):
            st.info(t("monthly_insights_placeholder"))
            st.caption(t("monthly_insights_disclaimer"))

st.header(t("transactions"))

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    start_date = st.date_input(
        t("from"),
        value=date.today().replace(day=1),
        key="start_date",
        format=DATE_INPUT_FORMAT,
    )
with filter_col2:
    end_date = st.date_input(
        t("to"),
        value=date.today(),
        key="end_date",
        format=DATE_INPUT_FORMAT,
    )

network_filter_value = st.selectbox(
    t("network_filter"),
    ["__all__"] + NETWORKS,
    key="network_filter_value",
    format_func=lambda value: t("all_networks") if value == "__all__" else value,
)

filtered = df_display.copy()
if not filtered.empty:
    if network_filter_value != "__all__":
        filtered = filtered[filtered["network"] == network_filter_value]

    filtered = filtered[
        (filtered["date"].dt.date >= start_date)
        & (filtered["date"].dt.date <= end_date)
    ]

if not filtered.empty:
    display_df = add_display_numbers(filtered)
    display_df["date"] = display_df["date"].dt.strftime(DISPLAY_DATE_FORMAT)
    display_df["amount"] = display_df.apply(format_display_amount, axis=1)
    display_df["transaction_type"] = display_df["transaction_type"].map(type_label)
    display_df = display_df.drop(columns=["id"])
    display_df = display_df.rename(columns={
        "display_id": "#",
        "date": t("date"),
        "network": t("network"),
        "transaction_type": t("type"),
        "amount": t("amount"),
        "note": t("note"),
    })

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    export_df = add_display_numbers(filtered)
    export_df["date"] = export_df["date"].dt.strftime(DISPLAY_DATE_FORMAT)
    export_df["transaction_type"] = export_df["transaction_type"].map(type_label)
    export_df["amount"] = export_df["amount"].map(format_money)
    export_df = export_df.drop(columns=["id"])
    export_df = export_df.rename(columns={
        "display_id": "ID",
        "date": t("date"),
        "network": t("network"),
        "transaction_type": t("type"),
        "amount": t("amount"),
        "note": t("note"),
    })
    csv = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=t("export"),
        data=csv,
        file_name=f"Transactions_{date.today().strftime('%d-%m-%Y')}.csv",
        mime="text/csv",
    )
else:
    st.info(t("no_filtered"))

st.subheader(t("edit_delete"))

if not filtered.empty:
    transaction_options = {}

    for display_num, (_, row) in enumerate(filtered.iterrows(), start=1):
        # ROBUST ID HANDLING - Fixed for both guest + cloud (UUID/string/int)
                
        try:
            disp_date = pd.to_datetime(row['date']).strftime('%d/%m/%Y')
        except:
            disp_date = "??/??/????"

        label = (
            f"#{display_num} | {disp_date} | "
            f"{row.get('network', 'Unknown')} | "
            f"{row.get('transaction_type', 'Other')} | "
            f"MWK {format_money(row.get('amount', 0))}"
        )

        transaction_options[label] = row["id"]

    if transaction_options:
        selected_label = st.selectbox(
            t("select_transaction"),
            list(transaction_options.keys())
        )

        edit_id = transaction_options[selected_label]

        # Ensure proper type for local mode
        if not st.session_state.current_user:
            try:
                edit_id = int(edit_id) if str(edit_id).isdigit() else edit_id
            except:
                pass

        edit_col1, edit_col2 = st.columns(2)
        if edit_col1.button(t("edit"), use_container_width=True):
            st.session_state.edit_mode = True
            st.session_state.edit_id = edit_id
            st.rerun()

        if edit_col2.button(t("delete"), use_container_width=True):
            try:
                if st.session_state.current_user:
                    delete_cloud_transaction(st.session_state.current_user, edit_id)
                    record_event("transaction_deleted", st.session_state.current_user)
                    updated_transactions = load_cloud_transactions(st.session_state.current_user)
                else:
                    updated_transactions = transactions[transactions["id"] != edit_id].reset_index(drop=True)

                st.session_state.transactions = updated_transactions
                st.session_state.save_message = t("deleted")
                st.rerun()
            except Exception as error:
                st.error(str(error))

if st.session_state.edit_mode:
    # More robust lookup
    if st.session_state.current_user:
        edit_rows = transactions[transactions["id"] == st.session_state.edit_id]
    else:
        edit_rows = transactions[transactions["id"].astype(str) == str(st.session_state.edit_id)]

    if edit_rows.empty:
        st.session_state.edit_mode = False
        st.session_state.edit_id = None
        st.rerun()

    trans = edit_rows.iloc[0]
    st.subheader(t("edit_transaction"))

    with st.form("edit_form"):
        new_date = st.date_input(
            t("date"),
            value=pd.to_datetime(trans["date"]).date(),
            key="edit_date",
            format=DATE_INPUT_FORMAT,
        )

        current_network = trans["network"] if trans["network"] in NETWORKS else NETWORKS[0]
        new_network = st.selectbox(
            t("network"),
            NETWORKS,
            index=NETWORKS.index(current_network),
            key="edit_network",
        )

        current_type = trans["transaction_type"] if trans["transaction_type"] in TRANSACTION_TYPES else "Other"
        edit_type_labels = [type_label(item) for item in TRANSACTION_TYPES]
        new_type_label = st.selectbox(
            t("type"),
            edit_type_labels,
            index=TRANSACTION_TYPES.index(current_type),
            key="edit_type",
        )
        new_type = TRANSACTION_TYPES[edit_type_labels.index(new_type_label)]

        new_amount = st.number_input(
            t("amount"),
            min_value=0.0,
            value=float(trans["amount"]),
            step=100.0,
            key="edit_amount",
        )
        new_note = st.text_input(t("note"), value=str(trans.get("note", "")), key="edit_note")

        save_col, cancel_col = st.columns(2)
        save_clicked = save_col.form_submit_button(t("save_changes"))
        cancel_clicked = cancel_col.form_submit_button(t("cancel_edit"))

        if save_clicked:
            if new_amount <= 0:
                st.error(t("amount_error"))
            else:
                updated_values = {
                    "date": new_date.isoformat(),
                    "network": new_network,
                    "transaction_type": new_type,
                    "amount": float(new_amount),
                    "note": new_note.strip(),
                }

                try:
                    if st.session_state.current_user:
                        update_cloud_transaction(
                            st.session_state.current_user,
                            st.session_state.edit_id,
                            updated_values,
                        )
                        updated_transactions = load_cloud_transactions(st.session_state.current_user)
                    else:
                        updated_transactions = transactions.copy()
                        mask = updated_transactions["id"].astype(str) == str(st.session_state.edit_id)
                        updated_transactions.loc[
                            mask,
                            ["date", "network", "transaction_type", "amount", "note"],
                        ] = [
                            updated_values["date"],
                            updated_values["network"],
                            updated_values["transaction_type"],
                            updated_values["amount"],
                            updated_values["note"],
                        ]
                        updated_transactions["date"] = pd.to_datetime(updated_transactions["date"])
                        updated_transactions = updated_transactions.sort_values(
                            ["date", "id"],
                            ascending=[False, False],
                        ).reset_index(drop=True)
                        updated_transactions["date"] = updated_transactions["date"].dt.strftime("%Y-%m-%d")

                    st.session_state.transactions = updated_transactions
                    st.session_state.edit_mode = False
                    st.session_state.edit_id = None
                    st.session_state.save_message = t("changes_saved")
                    st.rerun()
                except Exception as error:
                    st.error(str(error))

        if cancel_clicked:
            st.session_state.edit_mode = False
            st.session_state.edit_id = None
            st.rerun()

st.subheader(t("danger"))
st.warning(t("confirm_reset"))
delete_all_checked = st.checkbox(t("delete_all"), key="delete_all_checkbox")
if delete_all_checked:
    if st.button(t("reset")):
        try:
            if st.session_state.current_user:
                supabase_request(
                    "transactions",
                    method="DELETE",
                    params={"app_user_id": f"eq.{st.session_state.current_user['id']}"},
                )

            st.session_state.transactions = empty_transactions_df()
            st.session_state.save_message = t("reset_done")
            st.rerun()
        except Exception as error:
            st.error(str(error))
            
st.markdown("---")
st.caption(t("footer"))

with st.expander(f"{t('about')} / {t('privacy')} / {t('terms')}"):
    st.subheader(t("about"))
    st.markdown(t("about_text"))

    st.subheader(t("privacy"))
    st.markdown(t("privacy_text"))

    st.subheader(t("terms"))
    st.markdown(t("terms_text"))

with st.expander(t("contact")):
    st.write(t("contact_direct"))
