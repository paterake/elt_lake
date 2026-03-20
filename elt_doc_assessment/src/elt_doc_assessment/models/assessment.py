"""Data models for website assessment."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class Category(str, Enum):
    """URL category."""
    ASSESS = "assess"
    INFORMATION = "information"
    REQUIREMENT = "requirement"


class Severity(str, Enum):
    """Finding severity."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(str, Enum):
    """Assessment status."""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    NOT_CHECKED = "not_checked"


@dataclass
class Requirement:
    """A requirement from the specification documents."""
    section: str
    subsection: str
    description: str
    sequence: int
    category: str = "requirement"


@dataclass
class Website:
    """Website to assess."""
    url: str
    name: str
    category: str


@dataclass
class Credential:
    """Login credentials."""
    username: str
    password: str


@dataclass
class Finding:
    """A finding from the assessment."""
    section: str
    subsection: str
    description: str
    severity: Severity
    status: Status = Status.NOT_CHECKED
    evidence: str = ""
    url: str = ""


@dataclass
class Recommendation:
    """A recommendation for improvement."""
    section: str
    subsection: str
    description: str
    priority: str = "medium"  # low, medium, high
    effort: str = "medium"  # low, medium, high


@dataclass
class SectionResult:
    """Results for a section of the assessment."""
    name: str
    findings: list[Finding] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    screenshots: list[Path] = field(default_factory=list)


@dataclass
class AssessmentResult:
    """Complete assessment results."""
    website_url: str
    website_name: str
    sections: dict[str, SectionResult] = field(default_factory=dict)
    overall_score: float = 0.0
    summary: str = ""


@dataclass
class AssessmentConfig:
    """Configuration for the assessment."""
    name: str
    description: str
    websites: list[Website]
    information_urls: list[Website]
    requirements: list[Requirement]
    credentials: Optional[Credential]
    output_path: Path
