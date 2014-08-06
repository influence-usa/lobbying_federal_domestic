from ref import sopr

sopr_general_issue_codes = sopr.general_issue_codes.keys()

transformed_ld1_schema = {
    "type": "object",
    "properties": {
        "document_id": {
            "type": "string",
            "format": "uuid_hex",
        },
        "affiliated_organizations_url": {
            "type": ["null", "string"],
            "format": "url_http"
        },
        "signature": {
            "type": "string",
            "blank": False
        },
        "datetimes": {
            "type": "object",
            "properties": {
                "signature_date": {
                    "type": "string",
                    "format": "date-time"
                },
                "effective_date": {
                    "type": "string",
                    "format": "date-time"
                }
            }
        },
        "registration_type": {
            "type": "object",
            "properties": {
                "new_client_for_existing_registrant": {
                    "type": "boolean"
                },
                "new_registrant": {
                    "type": "boolean"
                },
                "is_amendment": {
                    "type": "boolean"
                }
            }
        },
        "registrant": {
            "type": [
                {
                    "title": "Individual Registrant",
                    "type": "object",
                    "properties": {
                        "organization_or_lobbying_firm": {
                            "type": "boolean",
                            "enum": [False, ]
                        },
                        "self_employed_individual": {
                            "type": "boolean",
                            "enum": [True, ]
                        },
                        "registrant_org_name": {
                            "type": "null"
                        },
                        "registrant_individual_prefix": {
                            "type": "string"
                        },
                        "registrant_individual_firstname": {
                            "type": "string"
                        },
                        "registrant_individual_lastname": {
                            "type": "string"
                        },
                        "registrant_address_one": {
                            "type": "string",
                        },
                        "registrant_address_two": {
                            "type": "string",
                            "blank": True
                        },
                        "registrant_city": {
                            "type": "string"
                        },
                        "registrant_state": {
                            "type": "string",
                            "pattern": "[A-Z]{2}"
                        },
                        "registrant_zip": {
                            "type": "string",
                            "pattern": "^\d{5}(?:[-\s]\d{4})?$"
                        },
                        "registrant_country": {
                            "type": "string"
                        },
                        "registrant_ppb_city": {
                            "type": "string",
                            "blank": True
                        },
                        "registrant_ppb_state": {
                            "type": "string",
                            "blank": True
                        },
                        "registrant_ppb_zip": {
                            "type": "string",
                            "blank": True
                        },
                        "registrant_ppb_country": {
                            "type": "string",
                            "blank": True
                        },
                        "registrant_international_phone": {
                            "type": "boolean"
                        },
                        "registrant_contact_name": {
                            "type": "string"
                        },
                        "registrant_contact_phone": {
                            "type": "string"
                        },
                        "registrant_contact_email": {
                            "type": "string",
                            "format": "email"
                        },
                        "registrant_general_description": {
                            "type": "string",
                        },
                        "registrant_house_id": {
                            "type": "string",
                            "pattern": "\d+"
                        },
                        "registrant_senate_id": {
                            "type": "string",
                            "pattern": "\d+"
                        }
                    }
                },
                {
                    "title": "Organizational Registrant",
                    "type": "object",
                    "properties": {
                        "organization_or_lobbying_firm": {
                            "type": "boolean",
                            "enum": [True, ]
                        },
                        "self_employed_individual": {
                            "type": "boolean",
                            "enum": [False, ]
                        },
                        "registrant_org_name": {
                            "type": "string"
                        },
                        "registrant_individual_prefix": {
                            "type": "null"
                        },
                        "registrant_individual_firstname": {
                            "type": "null"
                        },
                        "registrant_individual_lastname": {
                            "type": "null"
                        },
                        "registrant_address_one": {
                            "type": "string",
                        },
                        "registrant_address_two": {
                            "type": "string",
                            "blank": True
                        },
                        "registrant_city": {
                            "type": "string"
                        },
                        "registrant_state": {
                            "type": "string",
                            "pattern": "[A-Z]{2}"
                        },
                        "registrant_zip": {
                            "type": "string",
                            "pattern": "^\d{5}(?:[-\s]\d{4})?$"
                        },
                        "registrant_country": {
                            "type": "string"
                        },
                        "registrant_ppb_city": {
                            "type": "string",
                            "blank": True
                        },
                        "registrant_ppb_state": {
                            "type": "string",
                            "blank": True
                        },
                        "registrant_ppb_zip": {
                            "type": "string",
                            "blank": True
                        },
                        "registrant_ppb_country": {
                            "type": "string",
                            "blank": True
                        },
                        "registrant_international_phone": {
                            "type": "boolean"
                        },
                        "registrant_contact_name": {
                            "type": "string"
                        },
                        "registrant_contact_phone": {
                            "type": "string"
                        },
                        "registrant_contact_email": {
                            "type": "string",
                            "format": "email"
                        },
                        "registrant_general_description": {
                            "type": "string",
                        },
                        "registrant_house_id": {
                            "type": "string",
                            "pattern": "\d+"
                        },
                        "registrant_senate_id": {
                            "type": "string",
                            "pattern": "\d+"
                        }
                    }
                },
            ]
        },
        "client": {
            "type": [
                {
                    "title": "Client who is also the registrant",
                    "type": "object",
                    "properties": {
                        "client_self": {
                            "type": "boolean",
                            "enum": [True, ]
                        },
                        "client_name": {
                            "type": "string"
                        },
                        "client_general_description": {
                            "type": "string",
                            "blank": True
                        },
                        "client_address": {
                            "type": "string",
                            "blank": True
                        },
                        "client_city": {
                            "type": "string",
                            "blank": True
                        },
                        "client_state": {
                            "type": "string",
                            "blank": True
                        },
                        "client_zip": {
                            "type": "string",
                            "blank": True
                        },
                        "client_country": {
                            "type": "string",
                            "blank": True
                        },
                        "client_ppb_city": {
                            "type": "string",
                            "blank": True
                        },
                        "client_ppb_state": {
                            "type": "string",
                            "blank": True
                        },
                        "client_ppb_zip": {
                            "type": "string",
                            "blank": True
                        },
                        "client_ppb_country": {
                            "type": "string",
                            "blank": True
                        }
                    }
                },
                {
                    "title": "Client who is not the registrant",
                    "type": "object",
                    "properties": {
                        "client_self": {
                            "type": "boolean",
                            "enum": [False, ]
                        },
                        "client_name": {
                            "type": "string"
                        },
                        "client_general_description": {
                            "type": "string"
                        },
                        "client_address": {
                            "type": "string"
                        },
                        "client_city": {
                            "type": "string"
                        },
                        "client_zip": {
                            "type": "string"
                        },
                        "client_state": {
                            "type": "string"
                        },
                        "client_country": {
                            "type": "string"
                        },
                        "client_ppb_city": {
                            "type": "string",
                            "blank": True
                        },
                        "client_ppb_state": {
                            "type": "string",
                            "blank": True
                        },
                        "client_ppb_zip": {
                            "type": "string",
                            "blank": True
                        },
                        "client_ppb_country": {
                            "type": "string",
                            "blank": True
                        }
                    }
                }
            ]
        },
        "lobbying_issues": {
            "items": {
                "type": "object",
                "properties": {
                    "general_issue_area": {
                        "type": "string",
                        "enum": sopr_general_issue_codes
                    }
                }
            }
        },
        "affiliated_organizations": {
            "items": {
                "type": "object",
                "properties": {
                    "affiliated_organization_name": {
                        "type": "string"
                    },
                    "affiliated_organization_address": {
                        "type": "string"
                    },
                    "affiliated_organization_city": {
                        "type": "string"
                    },
                    "affiliated_organization_state": {
                        "type": "string"
                    },
                    "affiliated_organization_zip": {
                        "type": "string"
                    },
                    "affiliated_organization_country": {
                        "type": "string"
                    },
                    "affiliated_organization_ppb_state": {
                        "type": "string",
                        "blank": True
                    },
                    "affiliated_organization_ppb_city": {
                        "type": "string",
                        "blank": True
                    },
                    "affiliated_organization_ppb_country": {
                        "type": "string",
                        "blank": True
                    }
                }
            }
        },
        "lobbying_issues_detail": {
            "type": "string"
        },
        "foreign_entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "foreign_entity_name": {
                        "type": "string"
                    },
                    "foreign_entity_address": {
                        "type": "string"
                    },
                    "foreign_entity_city": {
                        "type": "string"
                    },
                    "foreign_entity_state": {
                        "type": "string"
                    },
                    "foreign_entity_country": {
                        "type": "string"
                    },
                    "foreign_entity_ppb_state": {
                        "type": "string"
                    },
                    "foreign_entity_ppb_country": {
                        "type": "string"
                    },
                    "foreign_entity_amount": {
                        "type": "number"
                    },
                    "foreign_entity_ownership_percentage": {
                        "type": "number"
                    }
                }
            }
        },
        "lobbyists": {
            "items": {
                "type": "object",
                "properties": {
                    "lobbyist_suffix": {
                        "type": "string",
                        "blank": True
                    },
                    "lobbyist_first_name": {
                        "type": "string"
                    },
                    "lobbyist_last_name": {
                        "type": "string"
                    },
                    "lobbyist_covered_official_position": {
                        "type": "string",
                        "blank": True
                    }
                }
            }
        }
    }
}

transformed_ld2_schema = {
    "type": "object",
    "properties": {
        "document_id": {
            "type": "string",
            "format": "uuid_hex",
        },
        "client_registrant_senate_id": {
            "type": "string",
            "pattern": "[0-9]+-[0-9]"
        },
        "client_registrant_house_id": {
            "type": "string",
            "pattern": "[0-9]+"
        },
        "report_type": {
            "type": "object",
            "properties": {
                "year": {
                    "type": "string",
                    "pattern": "\d{4}"
                },
                "quarter": {
                    "type": "string",
                    "pattern": "Q[1-4]"
                },
                "is_amendment": {
                    "type": "boolean"
                },
                "is_termination": {
                    "type": "boolean"
                },
                "no_activity": {
                    "type": "boolean"
                }
            }
        },
        "signature": {
            "type": "string"
        },
        "income_less_than_five_thousand": {
            "type": ["null", "boolean"]
        },
        "income_amount": {
            "type": ["null", "number"],
            "exclusiveMinimum": 5000
        },
        "expense_less_than_five_thousand": {
            "type": ["null", "boolean"]
        },
        "expense_reporting_method": {
            "type": ["string", "null"],
            "enum": ["a", "b", "c"]
        },
        "expense_amount": {
            "type": ["null", "number"],
            "exclusiveMinimum": 5000
        },
        "datetimes": {
            "type": "object",
            "properties": {
                "signature_date": {
                    "type": "string",
                    "format": "date-time"
                },
                "termination_date": {
                    "type": ["null", "string"],
                    "format": "date-time"
                }
            }
        },
        "registrant": {
            "type": "object",
            "properties": {
                "organization_or_lobbying_firm": {
                    "type": "boolean"
                },
                "self_employed_individual": {
                    "type": "boolean"
                },
                "registrant_name": {
                    "type": "string"
                },
                "registrant_address_one": {
                    "type": "string",
                },
                "registrant_address_two": {
                    "type": "string",
                    "blank": True
                },
                "registrant_city": {
                    "type": "string"
                },
                "registrant_state": {
                    "type": "string",
                    "pattern": "[A-Z]{2}"
                },
                "registrant_zip": {
                    "type": "string",
                    "pattern": "^\d{5}(?:[-\s]\d{4})?$"
                },
                "registrant_country": {
                    "type": "string"
                },
                "registrant_ppb_city": {
                    "type": "string",
                    "blank": True
                },
                "registrant_ppb_state": {
                    "type": "string",
                    "blank": True
                },
                "registrant_ppb_zip": {
                    "type": "string",
                    "blank": True
                },
                "registrant_ppb_country": {
                    "type": "string",
                    "blank": True
                },
                "registrant_contact_name": {
                    "type": "string"
                },
                "registrant_contact_name_prefix": {
                    "type": "string"
                },
                "registrant_contact_phone": {
                    "type": "string"
                },
                "registrant_contact_email": {
                    "type": "string",
                    "format": "email"
                }
            }
        },
        "client": {
            "client_name": {
                "type": "string"
            },
            "client_self": {
                "type": "boolean"
            },
            "client_state_or_local_government": {
                "type": "boolean"
            }
        },
        "lobbying_activities": {
            "items": {
                "type": "object",
                "properties": {
                    "general_issue_area": {
                        "type": "string",
                        "enum": sopr_general_issue_codes
                    },
                    "houses_and_agencies_none": {
                        "type": "boolean"
                    },
                    "specific_issues": {
                        "type": "string",
                        "blank": True
                    },
                    "houses_and_agencies": {
                        "type": "string",
                        "blank": True
                    },
                    "foreign_entity_interest_none": {
                        "type": "boolean"
                    },
                    "foreign_entity_interest": {
                        "type": "string",
                        "blank": True
                    },
                    "lobbyists": {
                        "items": {
                            "type": "object",
                            "properties": {
                                "lobbyist_covered_official_position": {
                                    "type": "string",
                                    "blank": True
                                },
                                "lobbyist_is_new": {
                                    "type": "boolean"
                                },
                                "lobbyist_first_name": {
                                    "type": "string",
                                },
                                "lobbyist_last_name": {
                                    "type": "string",
                                },
                                "lobbyist_suffix": {
                                    "type": "string",
                                    "blank": True
                                }
                            }
                        }
                    }
                }
            }
        },
        "registration_update": {
            "type": "object",
            "properties": {
                "client_address": {
                    "type": "string",
                    "blank": True
                },
                "client_city": {
                    "type": "string",
                    "blank": True
                },
                "client_state": {
                    "type": "string",
                    "blank": True
                },
                "client_zip": {
                    "type": "string",
                    "blank": True
                },
                "client_country": {
                    "type": "string",
                    "blank": True
                },
                "client_ppb_city": {
                    "type": "string",
                    "blank": True
                },
                "client_ppb_state": {
                    "type": "string",
                    "blank": True
                },
                "client_ppb_zip": {
                    "type": "string",
                    "blank": True
                },
                "client_ppb_country": {
                    "type": "string",
                    "blank": True
                },
                "client_general_description": {
                    "type": "string",
                    "blank": True
                },
                "removed_lobbyists": {
                    "items": {
                        "type": "object",
                        "properties": {
                            "lobbyist_first_name": {
                                "type": "string"
                            },
                            "lobbyist_last_name": {
                                "type": "string"
                            }
                        }
                    }
                },
                "removed_lobbying_issues": {
                    "items": {
                        "type": "object",
                        "properties": {
                            "general_issue_area": {
                                "type": "string",
                                "enum": sopr_general_issue_codes
                            }
                        }
                    }
                },
                "removed_foreign_entities": {
                    "items": {
                        "type": "object",
                        "properties": {
                            "foreign_entity_name": {
                                "type": "string"
                            }
                        }
                    }
                },
                "removed_affiliated_organizations":  {
                    "items": {
                        "type": "object",
                        "properties": {
                            "affiliated_organization_name": {
                                "type": "string"
                            }
                        }
                    }
                },
                "added_affiliated_organizations": {
                    "items": {
                        "type": "object",
                        "properties": {
                            "affiliated_organization_name": {
                                "type": "string",
                                "blank": True
                            },
                            "affiliated_organization_address": {
                                "type": "string",
                                "blank": True
                            },
                            "affiliated_organization_city": {
                                "type": "string",
                                "blank": True
                            },
                            "affiliated_organization_state": {
                                "type": "string",
                                "blank": True
                            },
                            "affiliated_organization_zip": {
                                "type": "string",
                                "blank": True
                            },
                            "affiliated_organization_country": {
                                "type": "string",
                                "blank": True
                            },
                            "affiliated_organization_ppb_state": {
                                "type": "string",
                                "blank": True
                            },
                            "affiliated_organization_ppb_city": {
                                "type": "string",
                                "blank": True
                            },
                            "affiliated_organization_ppb_country": {
                                "type": "string",
                                "blank": True
                            }
                        }
                    }
                },
                "added_foreign_entities": {
                    "items": {
                        "type": "object",
                        "properties": {
                            "foreign_entity_name": {
                                "type": "string",
                                "blank": True
                            },
                            "foreign_entity_address": {
                                "type": "string",
                                "blank": True
                            },
                            "foreign_entity_city": {
                                "type": "string",
                                "blank": True
                            },
                            "foreign_entity_state": {
                                "type": "string",
                                "blank": True
                            },
                            "foreign_entity_country": {
                                "type": "string",
                                "blank": True
                            },
                            "foreign_entity_ppb_state": {
                                "type": "string",
                                "blank": True
                            },
                            "foreign_entity_ppb_country": {
                                "type": "string",
                                "blank": True
                            },
                            "foreign_entity_amount": {
                                "type": "number",
                                "blank": True
                            },
                            "foreign_entity_ownership_percentage": {
                                "type": "number",
                                "blank": True
                            }
                        }
                    }
                }
            }
        }
    }
}
