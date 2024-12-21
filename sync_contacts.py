import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
FUB_API_KEY = os.getenv("FUB_API_KEY")

# HubSpot API Endpoint
HUBSPOT_CONTACTS_URL = "https://api.hubapi.com/crm/v3/objects/contacts"

# Follow Up Boss API Endpoint
FUB_CONTACTS_URL = "https://api.followupboss.com/v1/people"

# Fetch Contacts from HubSpot
def fetch_hubspot_contacts():
    headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
    params = {"limit": 100}
    response = requests.get(HUBSPOT_CONTACTS_URL, headers=headers, params=params)

    if response.status_code == 200:
        print("Successfully fetched contacts from HubSpot.")
        return response.json().get("results", [])
    else:
        print(f"Error fetching contacts from HubSpot: {response.text}")
        return []

# Fetch Contacts from Follow Up Boss
def fetch_fub_contacts():
    headers = {"authorization": "Basic ZmthXzB2NkJFS2tEbHVURllmVGIwRTZZdDNiU1BSNURrVjJJcms6"}
    response = requests.get(FUB_CONTACTS_URL, headers=headers)

    if response.status_code == 200:
        print("Successfully fetched contacts from Follow Up Boss.")
        return response.json().get("people", [])
    else:
        print(f"Error fetching contacts from Follow Up Boss: {response.text}")
        return []

# Sync Contacts to Follow Up Boss (Review Sync Function)
def sync_to_fub(hubspot_contacts, fub_contacts):
    fub_contacts_dict = {contact["emails"][0]["value"]: contact for contact in fub_contacts if "emails" in contact}

    headers = {"Authorization": f"Basic {FUB_API_KEY}", "Content-Type": "application/json"}

    for contact in hubspot_contacts:
        email = contact.get("properties", {}).get("email")
        if not email:
            continue  # Skip if no email exists

        data = {
            "firstName": contact.get("properties", {}).get("firstname"),
            "lastName": contact.get("properties", {}).get("lastname"),
            "emails": [{"value": email}],
            "phones": [{"value": contact.get("properties", {}).get("phone")}],
        }

        if email in fub_contacts_dict:
            # Update existing contact in FUB
            fub_contact_id = fub_contacts_dict[email]["id"]
            url = f"{FUB_CONTACTS_URL}/{fub_contact_id}"
            response = requests.put(url, headers=headers, json=data)
            print(f"Updated contact {email} in FUB: {response.status_code}")
        else:
            # Create new contact in FUB
            response = requests.post(FUB_CONTACTS_URL, headers=headers, json=data)
            print(f"Created contact {email} in FUB: {response.status_code}")

# Main Function
def main():
    hubspot_contacts = fetch_hubspot_contacts()
    fub_contacts = fetch_fub_contacts()
    sync_to_fub(hubspot_contacts, fub_contacts)

if __name__ == "__main__":
    main()
