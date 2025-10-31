# Liquor Primary Application Schema, ids taken from the Angular form controls in ApplicationComponent

FIELD_SCHEMA = [
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
        "label": "Treaty First Nation Land?",
        "type": "boolean",
        "required": False
    },
    {
        "id": "isPermittedInZoning",
        "label": "Zoning Declaration",
        "type": "boolean",
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

    # LG / Police (store IDs if known; accept plain text labels too)
    {
        "id": "indigenousNationId",
        "label": "Local Government / Indigenous Nation (ID)",
        "type": "string",
        "required": False
    },
    {
        "id": "indigenousNationName",
        "label": "Local Government / Indigenous Nation (Name)",
        "type": "string",
        "required": False
    },
    {
        "id": "policeJurisdictionId",
        "label": "Police Jurisdiction (ID)",
        "type": "string",
        "required": False
    },
    {
        "id": "policeJurisdictionName",
        "label": "Police Jurisdiction (Name)",
        "type": "string",
        "required": False
    },

    # Patio (ignore sub-fields for demo)
    {
        "id": "isHasPatio",
        "label": "Will have patio?",
        "type": "boolean",
        "required": False
    },

    # Establishment Type (Angular note: LP uses description1 for Establishment Type)
    {
        "id": "description1",
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
    {
        "id": "requestOutsideServiceHours",
        "label": "Request Outside Service Hours",
        "type": "boolean",
        "required": False
    },

    # Ownership details (required booleans)
    {
        "id": "isOwner",
        "label": "Ownership: I am the owner",
        "type": "boolean",
        "required": True
    },
    {
        "id": "hasValidInterest",
        "label": "Has valid interest",
        "type": "boolean",
        "required": True
    },
    {
        "id": "willHaveValidInterest",
        "label": "Will have valid interest",
        "type": "boolean",
        "required": True
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
        "label": "Authorized to submit",
        "type": "boolean",
        "required": True
    },
    {
        "id": "signatureAgreement",
        "label": "Declarations",
        "type": "boolean",
        "required": True
    }

]