"""Add reports and analytics tables

Revision ID: 003
Revises: 002
Create Date: 2025-01-06 15:33:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '003'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create reports table
    op.create_table('reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('report_type', sa.Enum('TRADE_SUMMARY', 'COMPLIANCE', 'DUTY_ANALYSIS', 'CLASSIFICATION_ACCURACY', 'CUSTOM', name='reporttype'), nullable=False),
        sa.Column('status', sa.Enum('GENERATING', 'COMPLETED', 'FAILED', 'CANCELLED', name='reportstatus'), nullable=False),
        sa.Column('format', sa.Enum('JSON', 'CSV', 'PDF', 'XLSX', name='reportformat'), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_created_at'), 'reports', ['created_at'], unique=False)
    op.create_index(op.f('ix_reports_created_by'), 'reports', ['created_by'], unique=False)
    op.create_index(op.f('ix_reports_report_type'), 'reports', ['report_type'], unique=False)
    op.create_index(op.f('ix_reports_status'), 'reports', ['status'], unique=False)

    # Create report_templates table
    op.create_table('report_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('report_type', sa.Enum('TRADE_SUMMARY', 'COMPLIANCE', 'DUTY_ANALYSIS', 'CLASSIFICATION_ACCURACY', 'CUSTOM', name='reporttype'), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('default_parameters', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_report_templates_category'), 'report_templates', ['category'], unique=False)
    op.create_index(op.f('ix_report_templates_name'), 'report_templates', ['name'], unique=False)
    op.create_index(op.f('ix_report_templates_report_type'), 'report_templates', ['report_type'], unique=False)

    # Create report_schedules table
    op.create_table('report_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('report_type', sa.Enum('TRADE_SUMMARY', 'COMPLIANCE', 'DUTY_ANALYSIS', 'CLASSIFICATION_ACCURACY', 'CUSTOM', name='reporttype'), nullable=False),
        sa.Column('frequency', sa.Enum('DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY', name='schedulefrequency'), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('recipients', sa.JSON(), nullable=True),
        sa.Column('format', sa.Enum('JSON', 'CSV', 'PDF', 'XLSX', name='reportformat'), nullable=False),
        sa.Column('next_run', sa.DateTime(), nullable=False),
        sa.Column('last_run', sa.DateTime(), nullable=True),
        sa.Column('run_count', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_report_schedules_frequency'), 'report_schedules', ['frequency'], unique=False)
    op.create_index(op.f('ix_report_schedules_next_run'), 'report_schedules', ['next_run'], unique=False)
    op.create_index(op.f('ix_report_schedules_report_type'), 'report_schedules', ['report_type'], unique=False)

    # Create analytics_metrics table
    op.create_table('analytics_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('metric_type', sa.Enum('COUNT', 'SUM', 'AVERAGE', 'PERCENTAGE', 'RATIO', name='metrictype'), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analytics_metrics_metric_type'), 'analytics_metrics', ['metric_type'], unique=False)
    op.create_index(op.f('ix_analytics_metrics_name'), 'analytics_metrics', ['name'], unique=False)
    op.create_index(op.f('ix_analytics_metrics_period_end'), 'analytics_metrics', ['period_end'], unique=False)
    op.create_index(op.f('ix_analytics_metrics_period_start'), 'analytics_metrics', ['period_start'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_analytics_metrics_period_start'), table_name='analytics_metrics')
    op.drop_index(op.f('ix_analytics_metrics_period_end'), table_name='analytics_metrics')
    op.drop_index(op.f('ix_analytics_metrics_name'), table_name='analytics_metrics')
    op.drop_index(op.f('ix_analytics_metrics_metric_type'), table_name='analytics_metrics')
    op.drop_table('analytics_metrics')
    
    op.drop_index(op.f('ix_report_schedules_report_type'), table_name='report_schedules')
    op.drop_index(op.f('ix_report_schedules_next_run'), table_name='report_schedules')
    op.drop_index(op.f('ix_report_schedules_frequency'), table_name='report_schedules')
    op.drop_table('report_schedules')
    
    op.drop_index(op.f('ix_report_templates_report_type'), table_name='report_templates')
    op.drop_index(op.f('ix_report_templates_name'), table_name='report_templates')
    op.drop_index(op.f('ix_report_templates_category'), table_name='report_templates')
    op.drop_table('report_templates')
    
    op.drop_index(op.f('ix_reports_status'), table_name='reports')
    op.drop_index(op.f('ix_reports_report_type'), table_name='reports')
    op.drop_index(op.f('ix_reports_created_by'), table_name='reports')
    op.drop_index(op.f('ix_reports_created_at'), table_name='reports')
    op.drop_table('reports')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS metrictype')
    op.execute('DROP TYPE IF EXISTS schedulefrequency')
    op.execute('DROP TYPE IF EXISTS reportformat')
    op.execute('DROP TYPE IF EXISTS reportstatus')
    op.execute('DROP TYPE IF EXISTS reporttype')