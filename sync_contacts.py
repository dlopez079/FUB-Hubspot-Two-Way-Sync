import os
import requests
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY") # Keys tested from env are good. 

FUB_API_KEY = os.getenv("FUB_API_KEY") # Keys tested from env are good. 

# HubSpot API endpoints
HUBSPOT_BASE_URL = "https://api.hubapi.com"
HUBSPOT_CONTACTS_URL = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts"

# Follow Up Boss API endpoints
FUB_BASE_URL = "https://api.followupboss.com/v1"
FUB_CONTACTS_URL = f"{FUB_BASE_URL}/people"

# FETCHING HUBSPOT CONTACTS - Use the HubSpot API to fetch contacts.
def fetch_hubspot_contacts():
    headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
    params = {"limit": 100}
    response = requests.get(HUBSPOT_CONTACTS_URL, headers=headers, params=params)

    if response.status_code == 200:
        print("Successfully fetched contacts from hubspot.") # Test
        return response.json().get("results", [])
    else:
        print(f"Error fetching contacts from HubSpot: {response.text}")
        return []

# FETCHING FUB CONTACTS - Fetch existing contacts from Follow Up Boss.
def fetch_fub_contacts():
    headers = {"Authorization": f"Bearer {FUB_API_KEY}"}
    response = requests.get(FUB_CONTACTS_URL, headers=headers)

    if response.status_code == 200:
        print("Successfully fetched contacts from FUB.") # Test
        return response.json().get("people", [])
    else:
        print(f"Error fetching contacts from Follow Up Boss: {response.text}")
        return []

# SYNCING - Compare and sync contacts between platforms.
def sync_contacts():
    hubspot_contacts = fetch_hubspot_contacts()
    fub_contacts = fetch_fub_contacts()

    # Create a dictionary of Follow Up Boss contacts for quick lookup
    fub_contacts_dict = {contact['emails'][0]['value']: contact for contact in fub_contacts if contact.get('emails')}

    for contact in hubspot_contacts:
        email = contact.get("properties", {}).get("email")
        if not email:
            continue

        if email in fub_contacts_dict:
            # Update existing contact in Follow Up Boss
            update_fub_contact(contact, fub_contacts_dict[email])
        else:
            # Create new contact in Follow Up Boss
            create_fub_contact(contact)

# CREATE
def create_fub_contact(contact):
    headers = {
        "Authorization": f"Bearer {FUB_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "firstName": contact.get("properties", {}).get("firstname"),
        "lastName": contact.get("properties", {}).get("lastname"),
        "emails": [{"value": contact.get("properties", {}).get("email")}],
        "phones": [{"value": contact.get("properties", {}).get("phone")}],
    }
    print(f"Creating contact in FUB: {data}") # Test
    response = requests.post(FUB_CONTACTS_URL, headers=headers, json=data)

    if response.status_code in [200, 201]:
        print(f"Created contact: {contact.get('properties', {}).get('email')}")
    else:
        print(f"Error creating contact in Follow Up Boss: {response.text}")

# UPDATE 
def update_fub_contact(hubspot_contact, fub_contact):
    headers = {
        "Authorization": f"Bearer {FUB_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "firstName": hubspot_contact.get("properties", {}).get("firstname"),
        "lastName": hubspot_contact.get("properties", {}).get("lastname"),
        "phones": [{"value": hubspot_contact.get("properties", {}).get("phone")}],
    }
    contact_id = fub_contact["id"]
    print(f"Updating FUB contact ID {contact_id} with data: {data}") # TEST

    response = requests.put(f"{FUB_CONTACTS_URL}/{contact_id}", headers=headers, json=data)

    if response.status_code in [200, 204]:
        print(f"Updated contact: {hubspot_contact.get('properties', {}).get('email')}")
    else:
        print(f"Error updating contact in Follow Up Boss: {response.text}")
