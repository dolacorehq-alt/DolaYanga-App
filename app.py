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
    "Money Received", "Money Sent", "Withdrawal", "Airtime",
    "Bill Payment", "Merchant Payment", "Other",
]
SPENDING_TYPES = [
    "Money Sent", "Withdrawal", "Airtime", "Bill Payment",
    "Merchant Payment", "Other",
]

# ... (TRANSLATIONS dict remains exactly the same - omitted here for brevity) ...
# Keep your full TRANSLATIONS dictionary unchanged

TYPE_TRANSLATION_KEYS = {
    "Money Received": "money_received",
    "Money Sent": "money_sent",
    "Withdrawal": "withdrawal",
    "Airtime": "airtime",
    "Bill Payment": "bill_payment",
    "Merchant Payment": "merchant_payment",
    "Other": "other",
}

st.set_page_config(page_title="DolaYanga", page_icon="MWK", layout="centered")

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

# ... (All your helper functions: get_required_secret, t(), type_label(), normalize_phone(), etc. remain unchanged) ...
# Keep everything up to load_transactions() as-is, except the sorting parts below.

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
        
        df["network"] = df["network"].where(df["network"].isin(NETWORKS), NETWORKS[0])
        df["transaction_type"] = df["transaction_type"].where(
            df["transaction_type"].isin(TRANSACTION_TYPES), "Other"
        )
        df["note"] = df["note"].fillna("")

        # CRITICAL FIX: Always sort by date DESC + id DESC (newest first)
        df = df.sort_values(["date", "id"], ascending=[False, False]).reset_index(drop=True)
        
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        
    else:
        df = empty_transactions_df()

    return df.reset_index(drop=True)


def save_transactions(df):
    df.to_csv(DATA_FILE, index=False)


def empty_transactions_df():
    return pd.DataFrame(columns=["id", "date", "network", "transaction_type", "amount", "note"])


def generate_demo_transactions():
    # ... (unchanged) ...
    today = date.today()
    demo_rows = [ ... ]  # keep your existing demo data
    return pd.DataFrame([...], columns=["id", "date", "network", "transaction_type", "amount", "note"])


def format_money(value):
    return f"{float(value):,.0f}"


def format_display_amount(row):
    amount = format_money(row["amount"])
    if row["transaction_type"] == "Money Received":
        return f"🟢 +MWK {amount}"
    return f"🔴 -MWK {amount}"


def add_display_numbers(df):
    """Add nice sequential display numbers (1, 2, 3...) for UI only"""
    display_df = df.copy().reset_index(drop=True)
    display_df.insert(0, "display_id", range(1, len(display_df) + 1))
    return display_df


def safe_id(val):
    if pd.isna(val) or val is None or val == "" or str(val).strip() == "":
        return "?"
    return str(val)


# ... (keep calculate_summary, show_summary_metrics, render_empty_state_onboarding unchanged) ...

# Session state initialization
for key, default in [
    ("language", "en"),
    ("last_network", NETWORKS[0]),
    ("edit_mode", False),
    ("edit_id", None),
    ("save_message", ""),
    ("demo_mode", False),
    ("current_user", None),
    ("auth_mode", "login"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

if "transactions" not in st.session_state:
    st.session_state.transactions = empty_transactions_df()

transactions = st.session_state.transactions

# ... (Language button, header, logo, login/signup section - unchanged) ...

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
            t("date"), value=date.today(), max_value=date.today(), format=DATE_INPUT_FORMAT
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
        amount = st.number_input(t("amount"), min_value=0.0, step=100.0, value=1000.0)

    note = st.text_input(t("note"))

    if st.form_submit_button(f"💾 {t('save_with_icon')}", type="primary"):
        if amount <= 0:
            st.error(t("amount_error"))
        else:
            if not st.session_state.current_user:
                next_id = 1 if transactions.empty else int(transactions["id"].max()) + 1
            else:
                next_id = None  # Supabase will generate UUID

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
                        [transactions, pd.DataFrame([new_transaction])], ignore_index=True
                    )
                    # Re-sort immediately
                    updated_transactions["date"] = pd.to_datetime(updated_transactions["date"])
                    updated_transactions = updated_transactions.sort_values(
                        ["date", "id"], ascending=[False, False]
                    ).reset_index(drop=True)
                    updated_transactions["date"] = updated_transactions["date"].dt.strftime("%Y-%m-%d")

                st.session_state.transactions = updated_transactions
                st.session_state.last_network = network
                st.session_state.save_message = t("saved_message")
                st.rerun()
            except Exception as e:
                st.error(str(e))

# Summary section (unchanged except using the already-sorted df)
if not transactions.empty:
    st.header(t("summary"))
    df_display = transactions.copy()
    df_display["date"] = pd.to_datetime(df_display["date"], errors="coerce")
    # Already sorted from load/save, but ensure again
    df_display = df_display.sort_values(["date", "id"], ascending=[False, False]).reset_index(drop=True)

    # ... rest of summary code unchanged ...

st.header(t("transactions"))

# Filter section (unchanged) ...

filtered = df_display.copy()
# ... filtering logic unchanged ...

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

    # Export (unchanged) ...

else:
    st.info(t("no_filtered"))

st.subheader(t("edit_delete"))

if not filtered.empty:
    transaction_options = {}

    for _, row in filtered.iterrows():
        disp_id = safe_id(row.get('id'))
        try:
            disp_date = pd.to_datetime(row['date']).strftime('%d/%m/%Y')
        except:
            disp_date = "??/??/????"

        # FIXED: Show nice sequential number instead of UUID
        label = (
            f"#{row.get('display_id', disp_id)} | {disp_date} | "
            f"{row.get('network', 'Unknown')} | "
            f"{row.get('transaction_type', 'Other')} | "
            f"MWK {format_money(row.get('amount', 0))}"
        )
        transaction_options[label] = row["id"]

    if transaction_options:
        selected_label = st.selectbox(
            t("select_transaction"), list(transaction_options.keys())
        )
        edit_id = transaction_options[selected_label]

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
                    # Re-sort after delete
                    if not updated_transactions.empty:
                        updated_transactions["date"] = pd.to_datetime(updated_transactions["date"])
                        updated_transactions = updated_transactions.sort_values(
                            ["date", "id"], ascending=[False, False]
                        ).reset_index(drop=True)
                        updated_transactions["date"] = updated_transactions["date"].dt.strftime("%Y-%m-%d")

                st.session_state.transactions = updated_transactions
                st.session_state.save_message = t("deleted")
                st.rerun()
            except Exception as e:
                st.error(str(e))

# Edit form (unchanged except sorting after edit)
if st.session_state.edit_mode:
    # ... existing edit form logic ...
    if save_clicked:
        # ... after updating ...
        if not st.session_state.current_user:
            updated_transactions["date"] = pd.to_datetime(updated_transactions["date"])
            updated_transactions = updated_transactions.sort_values(
                ["date", "id"], ascending=[False, False]
            ).reset_index(drop=True)
            updated_transactions["date"] = updated_transactions["date"].dt.strftime("%Y-%m-%d")
        st.session_state.transactions = updated_transactions
        st.session_state.edit_mode = False
        st.session_state.edit_id = None
        st.session_state.save_message = t("changes_saved")
        st.rerun()

# ==================== RESET FIX ====================
st.subheader(t("danger"))
st.warning(t("confirm_reset"))

# Use a key that we control carefully
if "reset_confirmed" not in st.session_state:
    st.session_state.reset_confirmed = False

reset_checked = st.checkbox(t("delete_all"), key="reset_checkbox")

if reset_checked and st.button(t("reset")):
    try:
        if st.session_state.current_user:
            supabase_request(
                "transactions",
                method="DELETE",
                params={"app_user_id": f"eq.{st.session_state.current_user['id']}"},
            )
        st.session_state.transactions = empty_transactions_df()
        st.session_state.save_message = t("reset_done")
        st.session_state.reset_confirmed = False
        # Clear the checkbox by forcing rerun
        st.rerun()
    except Exception as e:
        st.error(str(e))

st.markdown("---")
st.caption(t("footer"))

# ... rest of about/privacy/contact unchanged ...