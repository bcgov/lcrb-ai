# Liquor Primary Application Schema, ids taken from the Angular form controls in ApplicationComponent

FIELD_SCHEMA = [
    # {
    #     "id": "centralSecuritiesRegister",
    #     "label": "CSR",
    #     "type": "file",
    #     "required": False
    # },
    # {
    #     "id": "supportingBusinessForms",
    #     "label": "Supporting Forms",
    #     "type": "file",
    #     "required": False
    # },
    # {
    #     "id": "noticeOfArticles",
    #     "label": "NOA",
    #     "type": "file",
    #     "required": False
    # },
    # {
    #     "id": "personalHistorySummary",
    #     "label": "PHS",
    #     "type": "file",
    #     "required": False
    # },
    # {
    #     "id": "listOfShareholders",
    #     "label": "NV Shareholders",
    #     "type": "file",
    #     "required": False
    # },
    {
        "id": "establishmentName",
        "label": "Proposed Establishment Name",
        "type": "string",
        "required": True
    },
    {
        "id": "establishmentAddressStreet",
        "label": "Address",
        "type": "string",
        "required": True
    },
    {
        "id": "establishmentAddressCity",
        "label": "City",
        "type": "string",
        "required": True
    },
    {
        "id": "establishmentAddressProvince",
        "label": "Province",
        "type": "string",
        "required": False,
        "default": "British Columbia"
    },
    {
        "id": "establishmentAddressPostalCode",
        "label": "Postal Code",
        "type": "string",
        "required": True
    },
    {
        "id": "establishmentAddressCountry",
        "label": "Country",
        "type": "string",
        "required": False,
        "default": "Canada"
    },

    # Land / zoning
    {
        "id": "isOnINLand",
        "label": "Is the proposed establishment on Treaty First Nation Land?",
        "type": "boolean",
        "required": False
    },
    {
        "id": "isPermittedInZoning",
        "label": "Affirm Zoning Declaration",
        "type": "boolean",
        "required": False
    },
    # {
    #     "id": "letterOfIntent",
    #     "label": "LOI",
    #     "type": "file",
    #     "required": False
    # },
    
    # LG / Police (store IDs if known; accept plain text labels too)
    {
        "id": "indigenousNation",
        "label": "Local Government / Indigenous Nation",
        "type": "string",
        "required": False
    },
    {
        "id": "policeJurisdiction",
        "label": "Police Jurisdiction",
        "type": "string",
        "required": False
    },
        # Contacts (establishment)
    {
        "id": "establishmentEmail",
        "label": "Establishment Contact Email",
        "type": "string",
        "required": False
    },
    {
        "id": "establishmentPhone",
        "label": "Establishment Contact Phone",
        "type": "string",
        "required": False
    },

    # Patio (ignore sub-fields for demo)
    {
        "id": "isHasPatio",
        "label": "Will the establishment have a patio?",
        "type": "boolean",
        "required": False
    },

    # Establishment Type (Angular note: LP uses description1 for Establishment Type)
    {
        "id": "establishmentType",
        "label": "Establishment Type",
        "type": "string",
        "required": True
    },
        # Occupant Load
    {
        "id": "totalOccupantLoad",
        "label": "Total Occupant Load",
        "type": "number",
        "required": True
    },
    # {
    #     "id": "signageDocuments",
    #     "label": "Signage",
    #     "type": "file",
    #     "required": False,
    # },

    # {
    #     "id": "floorPlan",
    #     "label": "Floor Plan",
    #     "type": "file",
    #     "required": True,
    # },

    # {
    #     "id": "sitePlan",
    #     "label": "Site Plan",
    #     "type": "file",
    #     "required": False,
    # },

    # Service hours (keep 7-day open/close; optional in demo)
    {
        "id": "serviceHoursSundayOpen",
        "label": "Sunday Open",
        "type": "string",
        "required": False
    },
    {
        "id": "serviceHoursSundayClose",
        "label": "Sunday Close",
        "type": "string",
        "required": False
    },
    {
        "id": "serviceHoursMondayOpen",
        "label": "Monday Open",
        "type": "string",
        "required": False
    },
    {
        "id": "serviceHoursMondayClose",
        "label": "Monday Close",
        "type": "string",
        "required": False
    },
    {
        "id": "serviceHoursTuesdayOpen",
        "label": "Tuesday Open",
        "type": "string",
        "required": False
    },
    {
        "id": "serviceHoursTuesdayClose",
        "label": "Tuesday Close",
        "type": "string",
        "required": False
    },
    {
        "id": "serviceHoursWednesdayOpen",
        "label": "Wednesday Open",
        "type": "string",
        "required": False
    },
    {
        "id": "serviceHoursWednesdayClose",
        "label": "Wednesday Close",
        "type": "string",
        "required": False
    },
    {
        "id": "serviceHoursThursdayOpen",
        "label": "Thursday Open",
        "type": "string",
        "required": False
    },
    {
        "id": "serviceHoursThursdayClose",
        "label": "Thursday Close",
        "type": "string",
        "required": False
    },
    {
        "id": "serviceHoursFridayOpen",
        "label": "Friday Open",
        "type": "string",
        "required": False
    },
    {
        "id": "serviceHoursFridayClose",
        "label": "Friday Close",
        "type": "string",
        "required": False
    },
    {
        "id": "serviceHoursSaturdayOpen",
        "label": "Saturday Open",
        "type": "string",
        "required": False
    },
    {
        "id": "serviceHoursSaturdayClose",
        "label": "Saturday Close",
        "type": "string",
        "required": False
    },

    # Application contact (required)
    {
        "id": "contactPersonFirstName",
        "label": "Application Contact First Name",
        "type": "string",
        "required": True
    },
    {
        "id": "contactPersonLastName",
        "label": "Application Contact Last Name",
        "type": "string",
        "required": True
    },
    {
        "id": "contactPersonRole",
        "label": "Title/Position",
        "type": "string",
        "required": False
    },
    {
        "id": "contactPersonPhone",
        "label": "Application Contact Phone",
        "type": "string",
        "required": True
    },
    {
        "id": "contactPersonEmail",
        "label": "Application Contact Email",
        "type": "string",
        "required": True
    },

    # Declarations
    {
        "id": "authorizedToSubmit",
        "label": "Affirm authorization to submit",
        "type": "boolean",
        "required": True
    },
    {
        "id": "isOwner",
        "label": "Affirm ownership details",
        "type": "boolean",
        "required": True
    }

]