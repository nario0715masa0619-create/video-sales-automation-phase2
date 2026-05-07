class MasterLeadsColumns:
    lead_id = "lead_id"
    record_status = "record_status"
    lead_stage = "lead_stage"
    canonical_company_name = "canonical_company_name"
    official_url = "official_url"
    official_domain = "official_domain"
    official_email = "official_email"
    
    @classmethod
    def all_columns(cls):
        return [cls.lead_id, cls.record_status, cls.lead_stage, cls.canonical_company_name,
                cls.official_url, cls.official_domain, cls.official_email]
