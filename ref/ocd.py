# GLOBALS

SENATE_ID = 'ocd-organization/2fb1726e-a8c3-11e4-b6bf-3c970e91567b'
HOUSE_ID = 'ocd-organization/47ac47e0-a8c3-11e4-b6bf-3c970e91567b'

SENATE = {
    'id': SENATE_ID,
    'name': "United States Senate",
    'classification': 'legislature',
}

SOPR =   {
    'id': "ocd-organization/13dfdd58-a8b6-11e4-b6bf-3c970e91567b",
    'name': "Office of Public Record, US Senate",
    'classification': 'disclosure-authority',
    'parent_id': SENATE_ID,
     "contact_details": [
         {
           "type": "voice",
           "label": "",
           "value": "202-224-0322",
           "note": ""
         }
     ],
     "links": [
         {
             "url": "http://www.senate.gov/pagelayout/legislative/one_item_and_teasers/opr.htm",
             "note": "Profile page"
         },
         {
             "url": "http://www.senate.gov/pagelayout/legislative/g_three_sections_with_teasers/lobbyingdisc.htm#lobbyingdisc=lda",
             "note": "Disclosure Home"
         },
         {
             "url": "http://soprweb.senate.gov/index.cfm?event=selectfields",
             "note": "Disclosure Search Portal"
         },
         {
             "url": "http://soprweb.senate.gov/",
             "note": "Disclosure Electronic Filing System"
         }
     ]
}

HOUSE = {
    'id': HOUSE_ID,
    'name': "United States House of Representatives",
    'classification': 'legislature',
}

HOUSE_CLERK = {
    'id': 'ocd-organization/4fcc1aa2-a8b6-11e4-b6bf-3c970e91567b',
    'name': "Office of The Clerk, US House",
    'classification': 'disclosure-authority',
    'parent_id': HOUSE_ID,
    "contact_details": [
        {
          "type": "address",
          "label": "contact address",
          "value": "U.S. Capitol, Room H154, Washington, DC 20515-6601",
          "note": ""
        },
        {
            "type": "email",
            "label": "general inquiries",
            "value": "info.clerkweb@mail.house.gov",
            "note": ""
        },
        {
            "type": "email",
            "label": "general technical support",
            "value": "techsupport.clerkweb@mail.house.gov",
            "note": ""
        },
        {
            "type": "email",
            "label": "HouseLive support",
            "value": "houselive@mail.house.gov",
            "note": ""
        }
    ],
    "links": [
        {
            "url": "http://lobbyingdisclosure.house.gov/",
            "note": "Lobbying Disclosure"
        },
        {
            "url": "http://clerk.house.gov/",
            "note": "Home"
        },
        {
            "url": "http://disclosures.house.gov/ld/ldsearch.aspx",
            "note": "Lobbying Disclosure Search"
        }
    ]
}

# TEMPLATES

OCD_REPORTING_PERIOD = {
    "id": "",
    "description": "",
    "authorities": [
        SOPR,
        HOUSE_CLERK
    ],
    "period_type": "",
    "start_date": "",
    "end_date": ""
}

OCD_ORGANIZATION = {
    "id": "",
    "name": "",
    "other_names": [],
    "identifiers": [],
    "jurisdiction": "",
    "jurisdiction_id": "",
    "classification": "",
    "parent_id": "",
    "founding_date": "",
    "dissolution_date": "",
    "image": "",
    "contact_details": [],
    "memberships": [],
    "links": [],
    "extras": {
        "contact_details_structured": []
    }
}

OCD_MEMBERSHIP = {
    "organization": {
        "id": "",
        "classification": "",
        "name": "",
    },
    "post": {
        "id": "",
        "role": "",
        "start_date": "",
    }
}

OCD_PERSON = {
    "id": "",
    "name": "",
    "other_names": [],
    "identifiers": [],
    "gender": "",
    "birth_date": "",
    "death_date": "",
    "image": "",
    "summary": "",
    "biography": "",
    "national_identity": "",
    "contact_details": [],
    "links": [],
    "memberships": [
    ],
    "extras": {}
}


OCD_DOCUMENT = {
    "note": "",
    "date": "",
    "links": []
}

OCD_PARTICIPANT = {
    "entity_type": "",
    "id": "",
    "name": "",
    "note": ""
},

OCD_AGENDA_ITEM = {
    "description": "lobbying issues covered",
    "subjects": [],
    "media": None,
    "notes": [],
    "related_entities": []
}

OCD_DISCLOSED_EVENT = {
    "id": "",
    "classification": "registration",
    "name": "",
    "start_time": "",
    "timezone": "America/New_York",
    "all_day": False,
    "end_time": None,
    "status": "",
    "description": "",
    "location": None,
    "media": None,
    "documents": [], # OCD_DOCUMENT
    "links": "",
    "participants": [], # OCD_PARTICIPANT
    "agenda": [] # OCD_AGENDA_ITEM
}

SOPR_LD1_EXTRAS = {
    'registrant': {
        "self_employed_individual": False,
        "general_description": "",
        "signature": {}
    },
    "client": {
        "same_as_registrant": False,
        "general_description": "",
    },
    "registration_type": {
        "is_amendment": False,
        "new_registrant": False,
        "new_client_for_existing_registrant": False
    }
}

OCD_DISCLOSURE = {
    "id": "",
    "registrant": "",
    "registrant_id": "",
    "authority": "",
    "authority_id": "",
    "reporting_period": "",
    "related_entities": [],
    "identifiers": [],
    "effective_date": "",
    "created_at": "",
    "updated_at": "",
    "documents": [],
    "disclosed_events": [], # OCD_DISCLOSED_EVENT
    "extras": {}
}

def get_sopr_reporting_periods():
    pass
    #TODO
