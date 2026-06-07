"""Benchmark model - represents industry/company benchmarks."""
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Index, UniqueConstraint
from api.db.database import Base


class Benchmark(Base):
    """CAQI benchmarks for comparison."""

    __tablename__ = "benchmarks"

    id = Column(String(36), primary_key=True)
    benchmark_type = Column(String(50), nullable=False)  # industry, peer_group, company

    # Dimension
    dimension = Column(String(50), nullable=False)  # security, complexity, etc.

    # Percentile values
    percentile_10 = Column(Float)
    percentile_25 = Column(Float)
    percentile_50 = Column(Float)  # Median
    percentile_75 = Column(Float)
    percentile_90 = Column(Float)

    # Metadata
    sample_size = Column(Integer)
    calculated_at = Column(DateTime)

    # Constraints
    __table_args__ = (
        UniqueConstraint('benchmark_type', 'dimension', name='unique_benchmark'),
        Index('idx_benchmarks_type', 'benchmark_type'),
    )

    def __repr__(self):
        return f"<Benchmark {self.benchmark_type}:{self.dimension} p50={self.percentile_50:.0f}>"
