"""
News and intelligence API routes for the Customs Broker Portal.
Provides endpoints for dashboard news feeds, statistics, and recent rulings.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload

from database import get_async_session
from models.tariff import TariffCode
from models.dumping import DumpingDuty
from models.tco import Tco
from models.fta import FtaRate, TradeAgreement

router = APIRouter(prefix="/api/news", tags=["news"])

# Response models
class NewsItem(BaseModel):
    id: int
    title: str
    summary: str
    content: str
    source: str
    category: str
    impact_score: int
    related_hs_codes: List[str]
    published_date: datetime
    url: Optional[str] = None
    tags: List[str] = []

class WeeklyStatistics(BaseModel):
    tco_publications: int
    dumping_investigations: int
    fta_rate_changes: int
    legislative_amendments: int
    period_start: datetime
    period_end: datetime
    total_news_items: int
    critical_alerts: int

class TradeSummary(BaseModel):
    total_active_tcos: int
    total_dumping_measures: int
    total_fta_agreements: int
    recent_changes: int
    week_over_week_change: float

class AlertSummary(BaseModel):
    alert_type: str
    count: int
    severity: str
    latest_date: datetime
    affected_codes: List[str]

class NewsAnalytics(BaseModel):
    category_breakdown: Dict[str, int]
    source_breakdown: Dict[str, int]
    impact_distribution: Dict[str, int]
    trending_topics: List[str]
    most_affected_sectors: List[Dict[str, Any]]

@router.get("/dashboard-feed", response_model=List[NewsItem])
async def get_dashboard_feed(
    limit: int = Query(50, ge=1, le=100),
    category: str = Query("all"),
    since: Optional[datetime] = None,
    impact_threshold: int = Query(1, ge=1, le=5),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get news feed for dashboard with filtering options.
    Categories: all, critical, regulatory, tco, dumping, fta, legislative
    """
    try:
        # Generate news from recent database changes
        news_items = []
        
        # Get recent TCO publications
        if category in ["all", "tco", "regulatory"]:
            tco_news = await get_tco_news(db, limit // 4, since)
            news_items.extend(tco_news)
        
        # Get recent dumping duty updates
        if category in ["all", "dumping", "regulatory"]:
            dumping_news = await get_dumping_news(db, limit // 4, since)
            news_items.extend(dumping_news)
        
        # Get FTA rate changes
        if category in ["all", "fta", "regulatory"]:
            fta_news = await get_fta_news(db, limit // 4, since)
            news_items.extend(fta_news)
        
        # Add mock critical alerts and legislative updates
        if category in ["all", "critical", "legislative"]:
            critical_news = get_mock_critical_news(limit // 4, since)
            news_items.extend(critical_news)
        
        # Filter by impact threshold
        filtered_news = [item for item in news_items if item.impact_score >= impact_threshold]
        
        # Sort by publication date and impact score
        sorted_news = sorted(filtered_news, key=lambda x: (x.published_date, x.impact_score), reverse=True)
        
        return sorted_news[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news feed: {str(e)}")

@router.get("/statistics/weekly-summary", response_model=WeeklyStatistics)
async def get_weekly_summary(db: AsyncSession = Depends(get_async_session)):
    """Get weekly trade statistics summary for dashboard."""
    try:
        week_ago = datetime.now() - timedelta(days=7)
        
        # Count recent TCO publications
        tco_count_result = await db.execute(
            select(func.count(Tco.id))
            .where(Tco.gazetted_date >= week_ago)
        )
        tco_count = tco_count_result.scalar() or 0
        
        # Count recent dumping investigations
        dumping_count_result = await db.execute(
            select(func.count(DumpingDuty.id))
            .where(DumpingDuty.effective_date >= week_ago)
        )
        dumping_count = dumping_count_result.scalar() or 0
        
        # Count recent FTA rate changes (approximate)
        fta_count_result = await db.execute(
            select(func.count(FtaRate.id))
            .where(FtaRate.effective_date >= week_ago)
        )
        fta_count = fta_count_result.scalar() or 0
        
        # Mock legislative amendments count
        legislative_count = 3
        
        # Total news items generated
        total_news = tco_count + dumping_count + fta_count + legislative_count
        
        # Critical alerts (high impact items)
        critical_alerts = max(1, total_news // 10)
        
        return WeeklyStatistics(
            tco_publications=tco_count,
            dumping_investigations=dumping_count,
            fta_rate_changes=fta_count,
            legislative_amendments=legislative_count,
            period_start=week_ago,
            period_end=datetime.now(),
            total_news_items=total_news,
            critical_alerts=critical_alerts
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weekly summary: {str(e)}")

@router.get("/trade-summary", response_model=TradeSummary)
async def get_trade_summary(db: AsyncSession = Depends(get_async_session)):
    """Get overall trade measures summary."""
    try:
        # Count active TCOs
        active_tcos_result = await db.execute(
            select(func.count(Tco.id))
            .where(
                and_(
                    Tco.is_current == True,
                    or_(Tco.expiry_date.is_(None), Tco.expiry_date > datetime.now())
                )
            )
        )
        active_tcos = active_tcos_result.scalar() or 0
        
        # Count active dumping measures
        active_dumping_result = await db.execute(
            select(func.count(DumpingDuty.id))
            .where(
                and_(
                    DumpingDuty.is_active == True,
                    or_(DumpingDuty.expiry_date.is_(None), DumpingDuty.expiry_date > datetime.now())
                )
            )
        )
        active_dumping = active_dumping_result.scalar() or 0
        
        # Count FTA agreements
        fta_agreements_result = await db.execute(
            select(func.count(func.distinct(TradeAgreement.id)))
        )
        fta_agreements = fta_agreements_result.scalar() or 0
        
        # Recent changes (last 30 days)
        month_ago = datetime.now() - timedelta(days=30)
        recent_changes_result = await db.execute(
            select(func.count(Tco.id))
            .where(Tco.gazetted_date >= month_ago)
        )
        recent_changes = recent_changes_result.scalar() or 0
        
        # Week over week change calculation
        week_ago = datetime.now() - timedelta(days=7)
        two_weeks_ago = datetime.now() - timedelta(days=14)
        
        this_week_result = await db.execute(
            select(func.count(Tco.id))
            .where(Tco.gazetted_date >= week_ago)
        )
        this_week = this_week_result.scalar() or 0
        
        last_week_result = await db.execute(
            select(func.count(Tco.id))
            .where(
                and_(
                    Tco.gazetted_date >= two_weeks_ago,
                    Tco.gazetted_date < week_ago
                )
            )
        )
        last_week = last_week_result.scalar() or 1  # Avoid division by zero
        
        week_over_week = ((this_week - last_week) / last_week) * 100
        
        return TradeSummary(
            total_active_tcos=active_tcos,
            total_dumping_measures=active_dumping,
            total_fta_agreements=fta_agreements,
            recent_changes=recent_changes,
            week_over_week_change=round(week_over_week, 1)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trade summary: {str(e)}")

@router.get("/alerts", response_model=List[AlertSummary])
async def get_system_alerts(db: AsyncSession = Depends(get_async_session)):
    """Get system alerts and notifications."""
    try:
        alerts = []
        
        # TCO expiry alerts
        thirty_days = datetime.now() + timedelta(days=30)
        expiring_tcos_result = await db.execute(
            select(Tco.hs_code, func.count(Tco.id))
            .where(
                and_(
                    Tco.expiry_date.between(datetime.now(), thirty_days),
                    Tco.is_current == True
                )
            )
            .group_by(Tco.hs_code)
        )
        expiring_tcos = expiring_tcos_result.all()
        
        if expiring_tcos:
            alerts.append(AlertSummary(
                alert_type="TCO Expiry",
                count=len(expiring_tcos),
                severity="warning",
                latest_date=thirty_days,
                affected_codes=[code for code, _ in expiring_tcos[:5]]
            ))
        
        # New dumping investigations
        week_ago = datetime.now() - timedelta(days=7)
        new_dumping_result = await db.execute(
            select(DumpingDuty.hs_code, func.count(DumpingDuty.id))
            .where(DumpingDuty.effective_date >= week_ago)
            .group_by(DumpingDuty.hs_code)
        )
        new_dumping = new_dumping_result.all()
        
        if new_dumping:
            alerts.append(AlertSummary(
                alert_type="New Dumping Measures",
                count=len(new_dumping),
                severity="high",
                latest_date=datetime.now(),
                affected_codes=[code for code, _ in new_dumping[:5]]
            ))
        
        # Rate changes
        recent_fta_result = await db.execute(
            select(FtaRate.hs_code, func.count(FtaRate.id))
            .where(FtaRate.effective_date >= week_ago)
            .group_by(FtaRate.hs_code)
        )
        recent_fta = recent_fta_result.all()
        
        if recent_fta:
            alerts.append(AlertSummary(
                alert_type="FTA Rate Changes",
                count=len(recent_fta),
                severity="medium",
                latest_date=datetime.now(),
                affected_codes=[code for code, _ in recent_fta[:5]]
            ))
        
        return alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")

@router.get("/analytics", response_model=NewsAnalytics)
async def get_news_analytics(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_async_session)
):
    """Get news analytics and trends."""
    try:
        since_date = datetime.now() - timedelta(days=days)
        
        # Category breakdown based on database activity
        tco_count_result = await db.execute(
            select(func.count(Tco.id))
            .where(Tco.gazetted_date >= since_date)
        )
        tco_count = tco_count_result.scalar() or 0
        
        dumping_count_result = await db.execute(
            select(func.count(DumpingDuty.id))
            .where(DumpingDuty.effective_date >= since_date)
        )
        dumping_count = dumping_count_result.scalar() or 0
        
        fta_count_result = await db.execute(
            select(func.count(FtaRate.id))
            .where(FtaRate.effective_date >= since_date)
        )
        fta_count = fta_count_result.scalar() or 0
        
        category_breakdown = {
            "TCO": tco_count,
            "Anti-Dumping": dumping_count,
            "FTA": fta_count,
            "Legislative": max(1, (tco_count + dumping_count + fta_count) // 10),
            "Regulatory": max(2, (tco_count + dumping_count + fta_count) // 5)
        }
        
        source_breakdown = {
            "ABF": tco_count + dumping_count,
            "DFAT": fta_count,
            "Treasury": max(1, fta_count // 3),
            "ACBPS": dumping_count,
            "Industry": max(1, tco_count // 5)
        }
        
        impact_distribution = {
            "Critical (5)": max(1, (tco_count + dumping_count) // 10),
            "High (4)": max(2, (tco_count + dumping_count) // 5),
            "Medium (3)": max(3, (tco_count + dumping_count + fta_count) // 3),
            "Low (2)": max(5, (tco_count + fta_count) // 2),
            "Info (1)": max(10, tco_count + fta_count)
        }
        
        # Get most affected sectors
        sector_analysis_result = await db.execute(
            select(
                func.substr(Tco.hs_code, 1, 2).label('chapter'),
                func.count(Tco.id).label('count')
            )
            .where(Tco.gazetted_date >= since_date)
            .group_by(func.substr(Tco.hs_code, 1, 2))
            .order_by(desc('count'))
            .limit(5)
        )
        sector_data = sector_analysis_result.all()
        
        most_affected_sectors = []
        for chapter, count in sector_data:
            # Get chapter description
            chapter_result = await db.execute(
                select(TariffCode.description)
                .where(TariffCode.hs_code.like(f"{chapter}%"))
                .limit(1)
            )
            description = chapter_result.scalar()
            
            most_affected_sectors.append({
                "chapter": chapter,
                "description": description or f"Chapter {chapter}",
                "activity_count": count,
                "impact_level": "high" if count > 5 else "medium" if count > 2 else "low"
            })
        
        trending_topics = [
            "TCO Applications",
            "Anti-Dumping Reviews",
            "FTA Implementation",
            "Regulatory Changes",
            "Trade Compliance"
        ]
        
        return NewsAnalytics(
            category_breakdown=category_breakdown,
            source_breakdown=source_breakdown,
            impact_distribution=impact_distribution,
            trending_topics=trending_topics,
            most_affected_sectors=most_affected_sectors
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news analytics: {str(e)}")

@router.get("/recent", response_model=List[NewsItem])
async def get_recent_news(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_async_session)
):
    """Get most recent news items."""
    try:
        # Combine recent updates from all sources
        news_items = []
        
        # Recent TCO news
        tco_news = await get_tco_news(db, limit // 3)
        news_items.extend(tco_news)
        
        # Recent dumping news
        dumping_news = await get_dumping_news(db, limit // 3)
        news_items.extend(dumping_news)
        
        # Recent FTA news
        fta_news = await get_fta_news(db, limit // 3)
        news_items.extend(fta_news)
        
        # Sort by date and return most recent
        sorted_news = sorted(news_items, key=lambda x: x.published_date, reverse=True)
        return sorted_news[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent news: {str(e)}")

@router.get("/{news_id}", response_model=NewsItem)
async def get_news_item(news_id: int, db: AsyncSession = Depends(get_async_session)):
    """Get specific news item by ID."""
    try:
        # Try to find the news item from our generated feeds
        # Get recent news from all sources
        all_news = []
        
        # Get TCO news
        tco_news = await get_tco_news(db, 50)
        all_news.extend(tco_news)
        
        # Get dumping news
        dumping_news = await get_dumping_news(db, 50)
        all_news.extend(dumping_news)
        
        # Get FTA news
        fta_news = await get_fta_news(db, 50)
        all_news.extend(fta_news)
        
        # Get mock critical news
        critical_news = get_mock_critical_news(50)
        all_news.extend(critical_news)
        
        # Find the specific news item by ID
        for item in all_news:
            if item.id == news_id:
                return item
        
        raise HTTPException(status_code=404, detail="News item not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news item: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check for the news service."""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "news-api",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# Helper functions
async def get_tco_news(db: AsyncSession, limit: int, since: Optional[datetime] = None) -> List[NewsItem]:
    """Generate news items from recent TCO publications."""
    try:
        query = select(Tco).order_by(desc(Tco.gazetted_date)).limit(limit)
        if since:
            query = query.where(Tco.gazetted_date >= since)
            
        result = await db.execute(query)
        tcos = result.scalars().all()
        
        news_items = []
        for i, tco in enumerate(tcos):
            news_items.append(NewsItem(
                id=1000 + i,  # Offset to avoid conflicts
                title=f"New TCO Published: {tco.tco_number}",
                summary=f"Tariff Concession Order for {tco.description[:100]}...",
                content=f"A new Tariff Concession Order ({tco.tco_number}) has been published for HS code {tco.hs_code}. "
                       f"Goods description: {tco.description}. "
                       f"Status: {'CURRENT' if tco.is_current else 'INACTIVE'}. Gazetted: {tco.gazette_date.strftime('%d %B %Y') if tco.gazette_date else 'Not available'}.",
                source="ABF",
                category="tco",
                impact_score=3 if tco.is_current else 2,
                related_hs_codes=[tco.hs_code],
                published_date=tco.gazette_date,
                tags=["TCO", "Tariff Concession", "Import Relief"]
            ))
        
        return news_items
        
    except Exception:
        return []

async def get_dumping_news(db: AsyncSession, limit: int, since: Optional[datetime] = None) -> List[NewsItem]:
    """Generate news items from recent dumping duty updates."""
    try:
        query = select(DumpingDuty).order_by(desc(DumpingDuty.effective_date)).limit(limit)
        if since:
            query = query.where(DumpingDuty.effective_date >= since)
            
        result = await db.execute(query)
        duties = result.scalars().all()
        
        news_items = []
        for i, duty in enumerate(duties):
            impact = 5 if duty.is_active else 3
            news_items.append(NewsItem(
                id=2000 + i,  # Offset to avoid conflicts
                title=f"Anti-Dumping Update: {duty.goods_description[:50]}...",
                summary=f"Anti-dumping measure updated for goods from {duty.country_of_origin}",
                content=f"Anti-dumping duty measure has been updated for {duty.goods_description} "
                       f"from {duty.country_of_origin}. HS Code: {duty.hs_code}. "
                       f"Duty rate: {duty.duty_rate}%. Status: {'Active' if duty.is_active else 'Inactive'}. "
                       f"Effective: {duty.effective_date.strftime('%d %B %Y')}.",
                source="ACBPS",
                category="dumping",
                impact_score=impact,
                related_hs_codes=[duty.hs_code],
                published_date=duty.effective_date,
                tags=["Anti-Dumping", "Trade Defense", "Import Duty"]
            ))
        
        return news_items
        
    except Exception:
        return []

async def get_fta_news(db: AsyncSession, limit: int, since: Optional[datetime] = None) -> List[NewsItem]:
    """Generate news items from recent FTA rate changes."""
    try:
        query = (select(FtaRate)
                .join(TradeAgreement)
                .order_by(desc(FtaRate.effective_date))
                .limit(limit))
        if since:
            query = query.where(FtaRate.effective_date >= since)
            
        result = await db.execute(query)
        fta_rates = result.scalars().all()
        
        news_items = []
        for i, rate in enumerate(fta_rates):
            news_items.append(NewsItem(
                id=3000 + i,  # Offset to avoid conflicts
                title=f"FTA Rate Update: {rate.hs_code}",
                summary=f"Free Trade Agreement rate updated for HS code {rate.hs_code}",
                content=f"FTA preferential rate has been updated for HS code {rate.hs_code}. "
                       f"New rate: {rate.preferential_rate}%. "
                       f"Effective: {rate.effective_date.strftime('%d %B %Y')}.",
                source="DFAT",
                category="fta",
                impact_score=2,
                related_hs_codes=[rate.hs_code],
                published_date=rate.effective_date,
                tags=["FTA", "Preferential Rate", "Trade Agreement"]
            ))
        
        return news_items
        
    except Exception:
        return []

def get_mock_critical_news(limit: int, since: Optional[datetime] = None) -> List[NewsItem]:
    """Generate mock critical news and legislative updates."""
    base_date = since or (datetime.now() - timedelta(days=7))
    
    mock_news = [
        NewsItem(
            id=4001,
            title="Critical: New Import Restrictions on Steel Products",
            summary="Emergency restrictions imposed on steel imports effective immediately",
            content="The Australian Border Force has announced emergency import restrictions on certain steel products following a surge in dumped imports. All importers must obtain additional permits for HS codes 7208-7216.",
            source="ABF",
            category="critical",
            impact_score=5,
            related_hs_codes=["7208.10.00", "7210.12.00", "7216.10.00"],
            published_date=base_date + timedelta(hours=2),
            tags=["Critical", "Import Restrictions", "Steel", "Emergency"]
        ),
        NewsItem(
            id=4002,
            title="Legislative Update: Customs Amendment Bill 2024",
            summary="Significant changes to customs procedures and penalties",
            content="The Customs Amendment Bill 2024 introduces new compliance requirements for customs brokers, including enhanced record-keeping obligations and increased penalties for non-compliance.",
            source="Treasury",
            category="legislative",
            impact_score=4,
            related_hs_codes=[],
            published_date=base_date + timedelta(hours=6),
            tags=["Legislative", "Compliance", "Customs Amendment", "Penalties"]
        ),
        NewsItem(
            id=4003,
            title="System Alert: Integrated Cargo System Maintenance",
            summary="Scheduled maintenance affecting customs declarations",
            content="The Integrated Cargo System will undergo scheduled maintenance this weekend. All customs declarations must be submitted before Friday 5 PM to avoid delays.",
            source="ABF",
            category="critical",
            impact_score=3,
            related_hs_codes=[],
            published_date=base_date + timedelta(hours=12),
            tags=["System Alert", "ICS", "Maintenance", "Declarations"]
        )
    ]
    
    # Filter by date if since is provided
    if since:
        mock_news = [item for item in mock_news if item.published_date >= since]
    
    return mock_news[:limit]
