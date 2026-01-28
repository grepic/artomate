"""Add production-ready tables

Revision ID: prod_ready_001
Revises: 
Create Date: 2025-12-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'prod_ready_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add production-ready tables."""
    
    # Dead Letter Queue table
    op.create_table(
        'dead_letter_queue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('error_type', sa.String(length=255), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=False),
        sa.Column('error_context', sa.JSON(), nullable=True),
        sa.Column('retry_count', sa.Integer(), default=0),
        sa.Column('failed_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('job_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_dlq_job_id', 'dead_letter_queue', ['job_id'])
    
    # Webhook Events table
    op.create_table(
        'webhook_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=255), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('target_url', sa.String(length=1024), nullable=False),
        sa.Column('status', sa.String(length=50), default='pending'),
        sa.Column('attempts', sa.Integer(), default=0),
        sa.Column('last_attempt_at', sa.DateTime(), nullable=True),
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_webhook_event_type', 'webhook_events', ['event_type'])
    
    # Cost Records table
    op.create_table(
        'cost_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=True),
        sa.Column('cost_type', sa.String(length=50), nullable=False),
        sa.Column('service', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), default='USD'),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cost_job_id', 'cost_records', ['job_id'])
    op.create_index('ix_cost_created_at', 'cost_records', ['created_at'])


def downgrade():
    """Remove production-ready tables."""
    op.drop_index('ix_cost_created_at', 'cost_records')
    op.drop_index('ix_cost_job_id', 'cost_records')
    op.drop_table('cost_records')
    
    op.drop_index('ix_webhook_event_type', 'webhook_events')
    op.drop_table('webhook_events')
    
    op.drop_index('ix_dlq_job_id', 'dead_letter_queue')
    op.drop_table('dead_letter_queue')
