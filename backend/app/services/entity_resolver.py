"""Entity Resolution & Aggregation Engine.

Normalizes diverse textual entity mentions (companies, cities, technologies, job roles)
into canonical entities deterministically, maintaining traceability to underlying evidence.
"""
from __future__ import annotations

import re
import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.schemas.evidence import NormalizedEvidence


class ResolvedEntity(BaseModel):
    """Normalized entity with aggregated evidence metrics."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_id: str
    name: str  # Original detected mention
    normalized_name: str  # Canonical resolved entity name
    type: str  # company | city | technology | job_role
    mention_count: int = 0
    evidence_score: float = 0.0
    by_source_type: dict[str, int] = Field(default_factory=lambda: {
        "job": 0, "news": 0, "web": 0, "trend": 0, "local": 0
    })
    evidence_ids: list[str] = Field(default_factory=list)


class EntityResolver:
    """Deterministic entity normalization and evidence aggregation engine."""

    # Canonical City Aliases (canonical -> aliases)
    CITY_ALIASES: dict[str, set[str]] = {
        "Bengaluru": {"bangalore", "bengaluru", "blr"},
        "Hyderabad": {"hyderabad", "hyd", "cyberabad"},
        "Pune": {"pune", "poona"},
        "Chennai": {"chennai", "madras"},
        "Mumbai": {"mumbai", "bombay"},
        "Gurugram": {"gurgaon", "gurugram"},
        "Noida": {"noida", "greater noida"},
        "Delhi NCR": {"delhi", "new delhi", "delhi ncr"},
    }

    # Canonical Technology Aliases
    TECH_ALIASES: dict[str, set[str]] = {
        "AI/ML": {"ai/ml", "ai & ml", "aiml", "ai and ml", "artificial intelligence and machine learning"},
        "Generative AI": {"generative ai", "genai", "gen ai", "generative artificial intelligence"},
        "LLMs": {"llm", "llms", "large language model", "large language models"},
        "PyTorch": {"pytorch", "torch"},
        "TensorFlow": {"tensorflow", "tf"},
        "LangChain": {"langchain"},
        "Computer Vision": {"computer vision", "cv"},
        "Natural Language Processing": {"natural language processing", "nlp"},
    }

    # Canonical Company Aliases
    COMPANY_ALIASES: dict[str, set[str]] = {
        "Microsoft": {"microsoft", "msft"},
        "Google": {"google", "alphabet"},
        "Amazon": {"amazon", "aws", "amazon web services"},
        "TCS": {"tcs", "tata consultancy services"},
        "Infosys": {"infosys", "infy"},
        "Wipro": {"wipro"},
        "NVIDIA": {"nvidia", "nvda"},
        "Accenture": {"accenture"},
        "IBM": {"ibm", "international business machines"},
    }

    # Canonical Job Role Aliases
    ROLE_ALIASES: dict[str, set[str]] = {
        "AI/ML Engineer": {"ai/ml engineer", "ai engineer", "artificial intelligence engineer"},
        "Machine Learning Engineer": {"machine learning engineer", "ml engineer"},
        "Data Scientist": {"data scientist", "ds"},
        "Deep Learning Engineer": {"deep learning engineer", "dl engineer"},
        "AI Research Scientist": {"ai researcher", "ai research scientist", "research scientist"},
    }

    # Legal company suffixes to strip
    LEGAL_SUFFIXES_REGEX = re.compile(
        r"\b(?:india\s+pvt\.?\s*ltd\.?|private\s+limited|pvt\.?\s*ltd\.?|pvt\s+ltd|"
        r"corporation|corp\.?|inc\.?|llc|limited|ltd\.?|technologies|services|solutions|"
        r"india|technologies\s+india|labs|technologies\s+private\s+limited)\b",
        re.IGNORECASE,
    )

    @classmethod
    def normalize_company(cls, raw_name: Optional[str]) -> Optional[str]:
        """Normalize company name by stripping legal suffixes and resolving aliases."""
        if not raw_name or not raw_name.strip():
            return None

        clean = raw_name.strip()
        lowered = clean.lower()

        # Check explicit alias dictionary first
        for canonical, aliases in cls.COMPANY_ALIASES.items():
            if lowered == canonical.lower() or lowered in aliases:
                return canonical

        # Strip legal company suffixes
        stripped = cls.LEGAL_SUFFIXES_REGEX.sub("", clean).strip()
        # Clean trailing commas, hyphens, periods
        stripped = re.sub(r"[\s,\-\.]+$", "", stripped).strip()

        if not stripped:
            return clean.title()

        # Check alias again after stripping
        stripped_low = stripped.lower()
        for canonical, aliases in cls.COMPANY_ALIASES.items():
            if stripped_low == canonical.lower() or stripped_low in aliases:
                return canonical

        # Return standardized title case
        return stripped.title()

    @classmethod
    def normalize_city(cls, raw_city: Optional[str]) -> Optional[str]:
        """Normalize city name to standard spelling (e.g. Bangalore -> Bengaluru)."""
        if not raw_city or not raw_city.strip():
            return None

        low = raw_city.lower().strip()
        for canonical, aliases in cls.CITY_ALIASES.items():
            if low == canonical.lower() or low in aliases:
                return canonical
            # Substring match if part of composite address like "Bengaluru, Karnataka"
            for alias in aliases:
                if re.search(rf"\b{re.escape(alias)}\b", low):
                    return canonical

        return raw_city.strip().title()

    @classmethod
    def normalize_technology(cls, raw_tech: Optional[str]) -> Optional[str]:
        """Normalize technology name to standard canonical form."""
        if not raw_tech or not raw_tech.strip():
            return None

        low = raw_tech.lower().strip()
        for canonical, aliases in cls.TECH_ALIASES.items():
            if low == canonical.lower() or low in aliases:
                return canonical
            for alias in aliases:
                if re.search(rf"\b{re.escape(alias)}\b", low):
                    return canonical

        return raw_tech.strip()

    @classmethod
    def normalize_job_role(cls, raw_role: Optional[str]) -> Optional[str]:
        """Normalize job role to standard designation."""
        if not raw_role or not raw_role.strip():
            return None

        low = raw_role.lower().strip()
        for canonical, aliases in cls.ROLE_ALIASES.items():
            if low == canonical.lower() or low in aliases:
                return canonical

        return raw_role.strip().title()

    @classmethod
    def resolve_entity(cls, name: str, entity_type: str) -> str:
        """Resolve any entity name to canonical form based on type."""
        etype = entity_type.lower()
        if etype == "company":
            return cls.normalize_company(name) or name
        elif etype == "city":
            return cls.normalize_city(name) or name
        elif etype == "technology":
            return cls.normalize_technology(name) or name
        elif etype == "job_role":
            return cls.normalize_job_role(name) or name
        return name.strip().title()

    @classmethod
    def aggregate_evidence_by_entity(
        cls,
        evidence_items: list[NormalizedEvidence],
        analysis_id: str,
        entity_type: str = "city",
        target_entities: Optional[list[str]] = None,
    ) -> list[ResolvedEntity]:
        """Group and aggregate evidence items across all channels by resolved canonical entity."""
        entities_map: dict[str, ResolvedEntity] = {}

        # Pre-seed target entities if specified
        if target_entities:
            for tent in target_entities:
                canonical = cls.resolve_entity(tent, entity_type)
                entities_map[canonical] = ResolvedEntity(
                    analysis_id=analysis_id,
                    name=tent,
                    normalized_name=canonical,
                    type=entity_type,
                )

        for ev in evidence_items:
            # Detect which entity this evidence relates to
            detected_raw: Optional[str] = None
            if entity_type == "city":
                detected_raw = ev.location or ev.entity
                # If not in location/entity, search text for known cities
                if not detected_raw or not cls.normalize_city(detected_raw):
                    text = f"{ev.title or ''} {ev.snippet or ''}".lower()
                    for canonical, aliases in cls.CITY_ALIASES.items():
                        if any(re.search(rf"\b{re.escape(a)}\b", text) for a in aliases):
                            detected_raw = canonical
                            break
            elif entity_type == "company":
                detected_raw = ev.entity
                if not detected_raw and ev.source_type == "job":
                    # Try title extraction
                    pass
            elif entity_type == "technology":
                detected_raw = ev.entity or ev.title

            if not detected_raw:
                continue

            canonical = cls.resolve_entity(detected_raw, entity_type)
            if not canonical:
                continue

            # If target list is provided, only aggregate matching entities
            if target_entities and canonical not in entities_map:
                continue

            if canonical not in entities_map:
                entities_map[canonical] = ResolvedEntity(
                    analysis_id=analysis_id,
                    name=detected_raw,
                    normalized_name=canonical,
                    type=entity_type,
                )

            entity_record = entities_map[canonical]
            entity_record.mention_count += 1
            src_type = ev.source_type
            if src_type in entity_record.by_source_type:
                entity_record.by_source_type[src_type] += 1
            if ev.id:
                entity_record.evidence_ids.append(ev.id)

            # Update rolling evidence strength
            curr_score = entity_record.evidence_score
            ev_strength = ev.evidence_strength or 70.0
            entity_record.evidence_score = round(
                ((curr_score * (entity_record.mention_count - 1)) + ev_strength) / entity_record.mention_count,
                1,
            )

        return list(entities_map.values())
