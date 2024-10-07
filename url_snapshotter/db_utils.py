# url_snapshotter/db_utils.py

# This module provides the functionality to interact with the database.

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session
import os
from datetime import datetime

import structlog

# Base class for declarative class definitions
Base = declarative_base()

logger = structlog.get_logger()


class Snapshot(Base):
    """
    Represents a snapshot entity in the database.

    Attributes:
        snapshot_id (int): The primary key for the snapshot.
        name (str): The name of the snapshot. Cannot be null.
        created_at (datetime): The timestamp when the snapshot was created. Defaults to the current UTC time.
        url_snapshots (relationship): A relationship to the URLSnapshot model.
            - back_populates: "snapshot" - Indicates the attribute on the URLSnapshot model that relates back to this model.
            - cascade: "all, delete-orphan" - Specifies the cascade behavior for related URLSnapshot objects.
            - passive_deletes: True - Indicates that SQLAlchemy should not emit SQL to delete related objects when the parent is deleted.
    """

    __tablename__ = "snapshots"

    snapshot_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    url_snapshots = relationship(
        "URLSnapshot",
        back_populates="snapshot",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class URLSnapshot(Base):
    """
    URLSnapshot is a SQLAlchemy model representing a snapshot of a URL.

    Attributes:
        id (int): Primary key for the URL snapshot.
        snapshot_id (int): Foreign key referencing the snapshot this URL belongs to.
        url (str): The URL being snapshotted.
        http_code (int): The HTTP status code returned when the URL was accessed.
        content_hash (str): A hash of the content at the URL.
        full_content (str): The full content retrieved from the URL.
        created_at (datetime): The timestamp when the snapshot was created.
        snapshot (Snapshot): Relationship to the Snapshot model, back_populated by "url_snapshots".
    """

    __tablename__ = "url_snapshots"

    id = Column(Integer, primary_key=True)
    snapshot_id = Column(
        Integer, ForeignKey("snapshots.snapshot_id", ondelete="CASCADE"), nullable=False
    )
    url = Column(Text, nullable=False)
    http_code = Column(Integer)
    content_hash = Column(String, nullable=False)
    full_content = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    snapshot = relationship("Snapshot", back_populates="url_snapshots")


class DatabaseManager:
    """
    DatabaseManager is a class responsible for managing database operations, including
    initializing the database, saving snapshots, and retrieving snapshot data.

    Attributes:
        use_in_memory_db (bool): Indicates whether to use an in-memory database.
        db_url (str): The URL of the database.
        engine (Engine): SQLAlchemy engine for database connection.
        Session (scoped_session): SQLAlchemy session factory.

    Methods:
        __init__(timeout: int = 30):
            Initializes the DatabaseManager with a specified timeout for database connections.

        _use_in_memory_db() -> bool:
            Checks an environment variable to decide whether to use an in-memory database.

        _get_db_url() -> str:
            Returns the database URL based on the environment.

        _initialize_db():
            Initializes the database tables.

        get_session():
            Provides a session for database operations.

        save_snapshot(name: str, urls: list[dict[str, any]]):
            Saves snapshot details into the database.

        get_snapshots() -> list[Snapshot]:
            Retrieves all snapshots from the database.

        get_snapshot_data(snapshot_id: int) -> list[dict[str, any]]:
            Retrieves snapshot data for a specific snapshot ID.
    """

    def __init__(self, timeout: int = 30):
        """
        Initializes the database utility class.

        Args:
            timeout (int, optional): The timeout duration for the database connection in seconds. Defaults to 30.

        Attributes:
            use_in_memory_db (bool): Indicates whether to use an in-memory database.
            db_url (str): The database URL.
            engine (Engine): The SQLAlchemy engine connected to the database.
            Session (scoped_session): The scoped session factory for creating new sessions.
        """

        self.use_in_memory_db = self._use_in_memory_db()
        self.db_url = self._get_db_url()
        logger.debug(
            f"Initializing DatabaseManager with db_url: {self.db_url}, timeout: {timeout}"
        )
        self.engine = create_engine(
            self.db_url, connect_args={"timeout": timeout}, future=True
        )
        self.Session = scoped_session(
            sessionmaker(bind=self.engine, expire_on_commit=False)
        )
        self._initialize_db()

    def _use_in_memory_db(self) -> bool:
        """
        Determine whether to use an in-memory database.

        This method checks the environment variable 'USE_IN_MEMORY_DB' to decide
        whether to use an in-memory database. If the environment variable is set
        to 'true' (case insensitive), it returns True. Otherwise, it returns False.

        Returns:
            bool: True if 'USE_IN_MEMORY_DB' is set to 'true', False otherwise.
        """

        use_in_memory = os.getenv("USE_IN_MEMORY_DB", "false").lower() == "true"
        logger.debug(f"USE_IN_MEMORY_DB set to {use_in_memory}")
        return use_in_memory

    def _get_db_url(self) -> str:
        """
        Return the database URL based on the environment.

        Returns:
            str: The database URL. If `use_in_memory_db` is True, returns an in-memory SQLite URL.
                 Otherwise, returns a file-based SQLite URL pointing to 'snapshots.db'.
        """

        db_url = (
            "sqlite:///:memory:" if self.use_in_memory_db else "sqlite:///snapshots.db"
        )
        logger.debug(f"Database URL is set to {db_url}")
        return db_url

    def _initialize_db(self):
        """
        Initializes the database tables.

        This method sets up the database schema by creating all tables defined in the
        SQLAlchemy Base metadata. It uses the engine associated with the current instance
        to execute the table creation commands.
        """

        logger.debug("Initializing database tables.")
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """
        Creates and returns a new database session.

        Returns:
            Session: A new database session object.
        """

        logger.debug("Creating new database session.")
        return self.Session()

    def save_snapshot(self, name: str, urls: list[dict[str, any]]):
        """
        Saves a snapshot of URLs to the database.

        Args:
            name (str): The name of the snapshot.
            urls (list[dict[str, any]]): A list of dictionaries containing URL data. Each dictionary should have the keys:
                - "url" (str): The URL to be saved.
                - "http_code" (optional, int): The HTTP status code of the URL.
                - "content_hash" (str): The hash of the URL content.
                - "full_content" (optional, str): The full content of the URL.

        Raises:
            Exception: If there is an error during the database operation.
        """

        logger.debug(f"Saving snapshot '{name}' with {len(urls)} URLs.")
        session = self.get_session()
        try:
            snapshot = Snapshot(name=name.strip(), created_at=datetime.utcnow())
            session.add(snapshot)
            session.flush()  # Flush to assign snapshot_id without committing
            logger.debug(
                f"Assigned snapshot_id: {snapshot.snapshot_id} to snapshot '{name}'"
            )

            # Add URL snapshots
            for url_entry in urls:
                try:
                    url = url_entry["url"]
                    http_code = url_entry.get("http_code")
                    content_hash = url_entry["content_hash"]
                    full_content = url_entry.get("full_content", "")
                except KeyError as ke:
                    logger.error(f"Missing key {ke} in url_entry: {url_entry}")
                    continue

                url_snapshot = URLSnapshot(
                    snapshot_id=snapshot.snapshot_id,
                    url=url,
                    http_code=http_code,
                    content_hash=content_hash,
                    full_content=full_content,
                    created_at=datetime.utcnow(),
                )
                session.add(url_snapshot)
                logger.debug(f"Added URLSnapshot for URL: {url}")

            session.commit()
            logger.debug(f"Snapshot '{name}' saved successfully.")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save snapshot '{name}': {e}")
            raise
        finally:
            session.close()
            logger.debug("Database session closed.")

    def get_snapshots(self) -> list[Snapshot]:
        """
        Retrieves all snapshots from the database.

        This method queries the database for all Snapshot records, orders them by
        snapshot_id, and returns them as a list.

        Returns:
            list[Snapshot]: A list of Snapshot objects retrieved from the database.

        Raises:
            Exception: If there is an error while fetching snapshots from the database.
        """

        logger.debug("Retrieving all snapshots from the database.")
        session = self.get_session()
        try:
            snapshots = session.query(Snapshot).order_by(Snapshot.snapshot_id).all()
            logger.debug(f"Retrieved {len(snapshots)} snapshots.")
            return snapshots
        except Exception as e:
            logger.error(f"Failed to fetch snapshots from DB: {e}")
            raise
        finally:
            session.close()
            logger.debug("Database session closed.")

    def get_snapshot_data(self, snapshot_id: int) -> list[dict[str, any]]:
        """
        Retrieve snapshot data for a given snapshot ID.

        Args:
            snapshot_id (int): The ID of the snapshot to retrieve data for.

        Returns:
            list[dict[str, any]]: A list of dictionaries containing snapshot data. Each dictionary includes:
            - url (str): The URL of the snapshot.
            - http_code (int): The HTTP status code of the snapshot.
            - content_hash (str): The hash of the snapshot content.
            - full_content (str): The full content of the snapshot.

        Raises:
            Exception: If an error occurs while fetching the snapshot data.
        """

        logger.debug(f"Retrieving data for snapshot_id: {snapshot_id}")
        session = self.get_session()
        try:
            snapshot = (
                session.query(Snapshot).filter_by(snapshot_id=snapshot_id).one_or_none()
            )
            if not snapshot:
                logger.debug(f"No snapshot found with snapshot_id: {snapshot_id}")
                return []
            snapshot_data = [
                {
                    "url": url_snapshot.url,
                    "http_code": url_snapshot.http_code,
                    "content_hash": url_snapshot.content_hash,
                    "full_content": url_snapshot.full_content,
                }
                for url_snapshot in snapshot.url_snapshots
            ]
            logger.debug(
                f"Retrieved data for snapshot_id: {snapshot_id} with {len(snapshot_data)} URL snapshots."
            )
            return snapshot_data
        except Exception as e:
            logger.error(
                f"Failed to fetch snapshot data for snapshot_id {snapshot_id}: {e}"
            )
            raise
        finally:
            session.close()
            logger.debug("Database session closed.")
