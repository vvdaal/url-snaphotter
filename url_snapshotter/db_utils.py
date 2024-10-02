# url_snapshotter/db_utils.py

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session
import os
from datetime import datetime

from url_snapshotter.logger_utils import setup_logger

Base = declarative_base()
logger = setup_logger()

class Snapshot(Base):
    __tablename__ = 'snapshots'

    snapshot_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    url_snapshots = relationship(
        "URLSnapshot",
        back_populates="snapshot",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class URLSnapshot(Base):
    __tablename__ = 'url_snapshots'

    id = Column(Integer, primary_key=True)
    snapshot_id = Column(Integer, ForeignKey('snapshots.snapshot_id', ondelete="CASCADE"), nullable=False)
    url = Column(Text, nullable=False)
    http_code = Column(Integer)
    content_hash = Column(String, nullable=False)
    full_content = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    snapshot = relationship("Snapshot", back_populates="url_snapshots")


class DatabaseManager:
    def __init__(self, timeout: int = 30):
        self.use_in_memory_db = self._use_in_memory_db()
        self.db_url = self._get_db_url()
        self.engine = create_engine(self.db_url, connect_args={"timeout": timeout}, future=True)
        self.Session = scoped_session(sessionmaker(bind=self.engine, expire_on_commit=False))
        self._initialize_db()

    def _use_in_memory_db(self) -> bool:
        """Check environment variable to decide database type."""
        return os.getenv('USE_IN_MEMORY_DB', 'false').lower() == 'true'

    def _get_db_url(self) -> str:
        """Return database URL based on the environment."""
        return 'sqlite:///:memory:' if self.use_in_memory_db else 'sqlite:///snapshots.db'

    def _initialize_db(self):
        """Initialize database tables."""
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """Provide a session for database operations."""
        return self.Session()

    def save_snapshot(self, name: str, urls: list[dict[str, any]]):
        """Save snapshot details into the database."""
        session = self.get_session()
        try:
            snapshot = Snapshot(name=name.strip(), created_at=datetime.utcnow())
            session.add(snapshot)
            session.flush()  # Flush to assign snapshot_id without committing

            # Add URL snapshots
            for url_entry in urls:
                url_snapshot = URLSnapshot(
                    snapshot_id=snapshot.snapshot_id,
                    url=url_entry['url'],
                    http_code=url_entry['http_code'],
                    content_hash=url_entry['content_hash'],
                    full_content=url_entry['full_content'],
                    created_at=datetime.utcnow()
                )
                session.add(url_snapshot)

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save snapshot: {e}")
            raise
        finally:
            session.close()

    def get_snapshots(self) -> list[Snapshot]:
        """Retrieve all snapshots from the database."""
        session = self.get_session()
        try:
            return session.query(Snapshot).order_by(Snapshot.snapshot_id).all()
        except Exception as e:
            logger.error(f"Failed to fetch snapshots from DB: {e}")
            raise
        finally:
            session.close()

    def get_snapshot_data(self, snapshot_id: int) -> list[dict[str, any]]:
        """Retrieve snapshot data for a specific snapshot ID."""
        session = self.get_session()
        try:
            snapshot = session.query(Snapshot).filter_by(snapshot_id=snapshot_id).one_or_none()
            if not snapshot:
                return []
            return [
                {
                    'url': url_snapshot.url,
                    'http_code': url_snapshot.http_code,
                    'content_hash': url_snapshot.content_hash,
                    'full_content': url_snapshot.full_content
                }
                for url_snapshot in snapshot.url_snapshots
            ]
        except Exception as e:
            logger.error(f"Failed to fetch snapshot data: {e}")
            raise
        finally:
            session.close()
