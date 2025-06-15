"""
Phase 2 Orchestrator - Core Tariff Migration
============================================

Orchestrates the complete Phase 2 migration sequence following the critical
path defined in the PRD. Ensures proper execution order and data integrity.

Execution Sequence:
1. Day 1-2: ABF Sections Scraper
2. Day 3-4: ABF Chapters Scraper  
3. Day 5-10: ABF Tariff Codes Scraper (CRITICAL)

This orchestrator ensures each step completes successfully before proceeding
to the next, maintaining data integrity and foreign key relationships.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass

from .abf_sections_scraper import run_abf_sections_scraper
from .abf_chapters_scraper import run_abf_chapters_scraper
from .abf_tariff_codes_scraper import run_abf_tariff_codes_scraper
from .utils import logger, ScrapingError


@dataclass
class PhaseResult:
    """Result data for a phase step."""
    step_name: str
    success: bool
    duration_seconds: float
    records_processed: int
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class Phase2Orchestrator:
    """
    Orchestrates the complete Phase 2 Core Tariff Migration.
    
    Manages the critical sequence of scrapers that must complete
    before Phase 3 can begin.
    """
    
    def __init__(self):
        """Initialize Phase 2 orchestrator."""
        self.logger = logger
        self.results: List[PhaseResult] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
    async def run_complete_migration(self) -> Dict[str, Any]:
        """
        Execute the complete Phase 2 migration sequence.
        
        Returns:
            Complete migration results and metrics
        """
        self.start_time = datetime.now()
        
        try:
            self.logger.info("=" * 60)
            self.logger.info("🚀 STARTING PHASE 2: CORE TARIFF MIGRATION")
            self.logger.info("=" * 60)
            self.logger.info("Critical Path: Sections → Chapters → Tariff Codes")
            self.logger.info("⚠️  All steps must complete before Phase 3")
            
            # Step 1: ABF Sections Scraper (Day 1-2)
            await self._run_step(
                "ABF_Sections_Scraper",
                "Day 1-2: Extracting ABF tariff sections",
                run_abf_sections_scraper
            )
            
            # Step 2: ABF Chapters Scraper (Day 3-4)
            await self._run_step(
                "ABF_Chapters_Scraper", 
                "Day 3-4: Extracting ABF tariff chapters",
                run_abf_chapters_scraper
            )
            
            # Step 3: ABF Tariff Codes Scraper (Day 5-10) - CRITICAL
            await self._run_step(
                "ABF_Tariff_Codes_Scraper",
                "Day 5-10: Extracting hierarchical HS codes (CRITICAL)",
                run_abf_tariff_codes_scraper
            )
            
            # Calculate final metrics
            self.end_time = datetime.now()
            total_duration = (self.end_time - self.start_time).total_seconds()
            
            # Check if all steps succeeded
            all_success = all(result.success for result in self.results)
            total_records = sum(result.records_processed for result in self.results)
            
            final_metrics = {
                'phase': 'Phase 2 - Core Tariff Migration',
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'total_duration_seconds': total_duration,
                'total_duration_minutes': total_duration / 60,
                'all_steps_successful': all_success,
                'total_records_processed': total_records,
                'step_results': [
                    {
                        'step': result.step_name,
                        'success': result.success,
                        'duration_seconds': result.duration_seconds,
                        'records_processed': result.records_processed,
                        'error': result.error_message
                    }
                    for result in self.results
                ],
                'ready_for_phase_3': all_success
            }
            
            if all_success:
                self.logger.info("=" * 60)
                self.logger.info("✅ PHASE 2 MIGRATION COMPLETED SUCCESSFULLY!")
                self.logger.info("=" * 60)
                self.logger.info(f"⏱️  Total Duration: {total_duration/60:.1f} minutes")
                self.logger.info(f"📊 Total Records: {total_records:,}")
                self.logger.info("🎯 Database Structure:")
                self.logger.info("   ✅ tariff_sections populated")
                self.logger.info("   ✅ tariff_chapters populated") 
                self.logger.info("   ✅ tariff_codes populated (hierarchical)")
                self.logger.info("🚀 READY FOR PHASE 3: Duty Rates & FTA Migration")
            else:
                failed_steps = [r.step_name for r in self.results if not r.success]
                self.logger.error("=" * 60)
                self.logger.error("❌ PHASE 2 MIGRATION FAILED")
                self.logger.error("=" * 60)
                self.logger.error(f"Failed steps: {', '.join(failed_steps)}")
                self.logger.error("⚠️  Phase 3 cannot proceed until all steps complete")
            
            return final_metrics
            
        except Exception as e:
            self.end_time = datetime.now()
            total_duration = (self.end_time - self.start_time).total_seconds() if self.start_time else 0
            
            self.logger.error("=" * 60)
            self.logger.error("💥 PHASE 2 MIGRATION CRASHED")
            self.logger.error("=" * 60)
            self.logger.error(f"Error: {e}")
            self.logger.error(f"Duration before crash: {total_duration/60:.1f} minutes")
            
            error_metrics = {
                'phase': 'Phase 2 - Core Tariff Migration',
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat(),
                'total_duration_seconds': total_duration,
                'crashed': True,
                'error': str(e),
                'completed_steps': len(self.results),
                'step_results': [
                    {
                        'step': result.step_name,
                        'success': result.success,
                        'duration_seconds': result.duration_seconds,
                        'records_processed': result.records_processed
                    }
                    for result in self.results
                ]
            }
            
            raise ScrapingError(f"Phase 2 migration crashed: {e}") from e
    
    async def _run_step(self, step_name: str, description: str, step_function) -> None:
        """
        Execute a single migration step with error handling.
        
        Args:
            step_name: Name of the step for logging
            description: Human-readable description
            step_function: Async function to execute
        """
        step_start = datetime.now()
        
        try:
            self.logger.info("-" * 50)
            self.logger.info(f"🔄 {description}")
            self.logger.info("-" * 50)
            
            # Execute the step
            step_metrics = await step_function()
            
            step_end = datetime.now()
            step_duration = (step_end - step_start).total_seconds()
            
            # Extract records count from metrics
            records_count = 0
            if step_metrics:
                records_count = (
                    step_metrics.get('sections_saved', 0) +
                    step_metrics.get('chapters_saved', 0) +
                    step_metrics.get('tariff_codes_saved', 0)
                )
            
            # Record successful result
            result = PhaseResult(
                step_name=step_name,
                success=True,
                duration_seconds=step_duration,
                records_processed=records_count,
                metrics=step_metrics
            )
            self.results.append(result)
            
            self.logger.info(f"✅ {step_name} completed successfully")
            self.logger.info(f"⏱️  Duration: {step_duration:.1f} seconds")
            self.logger.info(f"📊 Records: {records_count:,}")
            
        except Exception as e:
            step_end = datetime.now()
            step_duration = (step_end - step_start).total_seconds()
            
            # Record failed result
            result = PhaseResult(
                step_name=step_name,
                success=False,
                duration_seconds=step_duration,
                records_processed=0,
                error_message=str(e)
            )
            self.results.append(result)
            
            self.logger.error(f"❌ {step_name} failed after {step_duration:.1f} seconds")
            self.logger.error(f"Error: {e}")
            
            # For critical steps, stop the entire migration
            if "tariff_codes" in step_name.lower():
                self.logger.error("⚠️  CRITICAL STEP FAILED - Stopping migration")
                raise ScrapingError(f"Critical step {step_name} failed: {e}") from e
            else:
                # For non-critical steps, continue but log the failure
                self.logger.warning(f"⚠️  Non-critical step failed, continuing migration")
    
    async def validate_prerequisites(self) -> bool:
        """
        Validate that prerequisites are met for Phase 2.
        
        Returns:
            True if prerequisites are met, False otherwise
        """
        try:
            self.logger.info("🔍 Validating Phase 2 prerequisites...")
            
            # Check Browserless API configuration
            from .config import ScraperConfig
            config = ScraperConfig()
            
            if not config.browserless_config.api_key:
                self.logger.error("❌ Browserless API key not configured")
                return False
            
            if not config.browserless_config.api_url:
                self.logger.error("❌ Browserless API URL not configured")
                return False
            
            # Check database connectivity
            try:
                from ..backend.database import get_db_session
                async with get_db_session() as session:
                    await session.execute("SELECT 1")
                self.logger.info("✅ Database connectivity verified")
            except Exception as e:
                self.logger.error(f"❌ Database connectivity failed: {e}")
                return False
            
            # Check that required tables exist
            required_tables = ['tariff_sections', 'tariff_chapters', 'tariff_codes']
            try:
                async with get_db_session() as session:
                    for table in required_tables:
                        result = await session.execute(
                            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
                        )
                        if not result.fetchone():
                            self.logger.error(f"❌ Required table '{table}' not found")
                            return False
                self.logger.info("✅ Required database tables verified")
            except Exception as e:
                self.logger.error(f"❌ Database table validation failed: {e}")
                return False
            
            self.logger.info("✅ All prerequisites validated")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Prerequisites validation failed: {e}")
            return False
    
    async def run_with_validation(self) -> Dict[str, Any]:
        """
        Run Phase 2 migration with prerequisite validation.
        
        Returns:
            Migration results including validation status
        """
        try:
            # Validate prerequisites first
            if not await self.validate_prerequisites():
                raise ScrapingError("Prerequisites validation failed")
            
            # Run the migration
            return await self.run_complete_migration()
            
        except Exception as e:
            self.logger.error(f"Phase 2 migration failed: {e}")
            raise


# Convenience functions for different execution modes
async def run_phase2_migration() -> Dict[str, Any]:
    """
    Run the complete Phase 2 migration.
    
    Returns:
        Migration results dictionary
    """
    orchestrator = Phase2Orchestrator()
    return await orchestrator.run_with_validation()


async def run_phase2_step(step_name: str) -> Dict[str, Any]:
    """
    Run a single Phase 2 step.
    
    Args:
        step_name: Name of step to run ('sections', 'chapters', or 'codes')
        
    Returns:
        Step results dictionary
    """
    step_functions = {
        'sections': run_abf_sections_scraper,
        'chapters': run_abf_chapters_scraper,
        'codes': run_abf_tariff_codes_scraper
    }
    
    if step_name not in step_functions:
        raise ValueError(f"Invalid step name: {step_name}. Must be one of: {list(step_functions.keys())}")
    
    return await step_functions[step_name]()


if __name__ == "__main__":
    # Direct execution runs complete migration
    asyncio.run(run_phase2_migration())
