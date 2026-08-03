from typing import List, Optional
from pydantic import BaseModel, Field


class ReportItem(BaseModel):
    title: str = Field(description="Clean, concise title summarizing the post or announcement")
    artist: str = Field(description="Artist name or Group name involved (e.g., TWICE, Stray Kids, IU, etc.)")
    summary: str = Field(description="A 1 to 2 sentence informative summary highlighting key details")
    post_url: str = Field(description="URL to the Reddit post or direct source link")
    upvotes: int = Field(default=0, description="Upvote count on Reddit")
    flair: Optional[str] = Field(default="", description="Original Reddit post flair if available")


class KpopDailyReport(BaseModel):
    comebacks_and_releases: List[ReportItem] = Field(
        default_factory=list,
        description="Music Videos, Teasers, Tracklists, Concept Photos, Album Releases"
    )
    tours_and_concerts: List[ReportItem] = Field(
        default_factory=list,
        description="Tour announcements, concert dates, ticketing, fan meetings"
    )
    industry_news: List[ReportItem] = Field(
        default_factory=list,
        description="Contracts, agency updates, achievements, chart records, official statements"
    )
    highlights_and_discussion: List[ReportItem] = Field(
        default_factory=list,
        description="Popular discussions, variety show clips, dance challenges, milestones"
    )
