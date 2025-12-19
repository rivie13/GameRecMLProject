# Database Guide: SQLAlchemy & Alembic

**Last Updated**: December 18, 2025  
**Status**: Phase 3 Backend step 1 Setup Complete ✅

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [SQLAlchemy Basics](#sqlalchemy-basics)
3. [Alembic Commands](#alembic-commands)
4. [Common Operations](#common-operations)
5. [Query Examples](#query-examples)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### Tech Stack
- **Database**: PostgreSQL 15+ (`steam_rec_db`)
- **ORM**: SQLAlchemy 2.0+ (with psycopg3 driver)
- **Migrations**: Alembic 1.13+
- **Connection**: `postgresql+psycopg://postgres:password@localhost:5432/steam_rec_db`

### File Structure
```
backend/
├── models.py          # SQLAlchemy ORM models (database tables)
├── database.py        # Database connection and session management
├── schemas.py         # Pydantic models (API request/response validation)
├── alembic.ini        # Alembic configuration
└── alembic/
    ├── env.py         # Alembic environment configuration
    └── versions/      # Migration files (auto-generated)
```

---

## SQLAlchemy Basics

### What is SQLAlchemy?
SQLAlchemy is a Python ORM (Object-Relational Mapping) library that lets you interact with databases using Python classes instead of raw SQL.

### Models vs Schemas
**Models (`models.py`)** - SQLAlchemy ORM classes representing database tables:
```python
class User(Base):
    __tablename__ = "users"
    steam_id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=False)
```

**Schemas (`schemas.py`)** - Pydantic classes for API validation:
```python
class UserCreate(BaseModel):
    steam_id: int
    username: str
```

**Key Difference**: Models = Database structure, Schemas = API data validation

---

### Database Session Management

**Get a database session** (use in API routes):
```python
from database import get_db
from sqlalchemy.orm import Session

@app.get("/users/{steam_id}")
def get_user(steam_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.steam_id == steam_id).first()
    return user
```

**Session best practices**:
- Always use `Depends(get_db)` in FastAPI routes
- Session is automatically closed after the request
- Don't create sessions manually unless you know what you're doing

---

### CRUD Operations (Create, Read, Update, Delete)

#### Create (INSERT)
```python
# Create a new user
new_user = User(
    steam_id=76561197960287930,
    username="GabeNewell",
    profile_url="https://steamcommunity.com/id/gabelogannewell"
)
db.add(new_user)
db.commit()
db.refresh(new_user)  # Get the created object with defaults
```

#### Read (SELECT)
```python
# Get one user by primary key
user = db.query(User).filter(User.steam_id == 76561197960287930).first()

# Get all users
users = db.query(User).all()

# Get with filters
active_users = db.query(User).filter(User.last_sync != None).all()

# Count
user_count = db.query(User).count()
```

#### Update
```python
# Update a user
user = db.query(User).filter(User.steam_id == 76561197960287930).first()
user.username = "Updated Name"
user.last_sync = datetime.now()
db.commit()
```

#### Delete
```python
# Delete a user (cascades to related records)
user = db.query(User).filter(User.steam_id == 76561197960287930).first()
db.delete(user)
db.commit()
```

---

### Relationships

#### One-to-Many (User has many UserGames)
```python
# In models.py
class User(Base):
    games = relationship("UserGame", back_populates="user", cascade="all, delete-orphan")

class UserGame(Base):
    user = relationship("User", back_populates="games")

# Query with relationships
user = db.query(User).filter(User.steam_id == 123).first()
games = user.games  # Access related games
print(f"{user.username} owns {len(games)} games")
```

---

## Alembic Commands

### What is Alembic?
Alembic is a database migration tool that tracks changes to your database schema over time. Think of it as "Git for your database structure."

### Essential Commands

#### 1. Check Current Migration Status
```powershell
alembic current
```
**Output**: Shows which migration version the database is currently at.

---

#### 2. Create a New Migration (Auto-generate)
```powershell
alembic revision --autogenerate -m "Description of changes"
```
**What it does**:
- Compares `models.py` to the actual database
- Auto-generates a migration file in `alembic/versions/`
- Names the file with a revision ID + your description

**Example**:
```powershell
alembic revision --autogenerate -m "Add user preferences column"
```

**When to use**:
- After adding/modifying models in `models.py`
- Before running the migration, review the generated file!

---

#### 3. Apply Migrations (Upgrade Database)
```powershell
alembic upgrade head
```
**What it does**:
- Applies all pending migrations to bring database up to date
- `head` means "latest version"

**Other options**:
```powershell
alembic upgrade +1           # Upgrade by 1 migration
alembic upgrade <revision>   # Upgrade to specific revision
```

---

#### 4. Rollback Migrations (Downgrade Database)
```powershell
alembic downgrade -1         # Rollback 1 migration
alembic downgrade base       # Rollback all migrations
alembic downgrade <revision> # Rollback to specific revision
```
**Use case**: Undo a migration if something went wrong.

---

#### 5. View Migration History
```powershell
alembic history
```
**Output**: Shows all migrations in chronological order.

```powershell
alembic history --verbose
```
**Output**: Shows detailed info including file paths.

---

#### 6. Generate SQL Without Applying (Dry Run)
```powershell
alembic upgrade head --sql
```
**What it does**: Shows the SQL that would be executed without actually running it.

---

### Migration Workflow (Step-by-Step)

**Scenario**: You want to add a new column to the `User` model.

#### Step 1: Modify the model
```python
# models.py
class User(Base):
    __tablename__ = "users"
    steam_id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=False)
    country = Column(String(2), nullable=True)  # NEW COLUMN
```

#### Step 2: Generate migration
```powershell
alembic revision --autogenerate -m "Add country column to users"
```

#### Step 3: Review the generated migration
```powershell
# Open alembic/versions/<timestamp>_add_country_column_to_users.py
# Check the upgrade() and downgrade() functions
```

#### Step 4: Apply the migration
```powershell
alembic upgrade head
```

#### Step 5: Verify
```powershell
alembic current  # Should show the new revision
```

Done! Your database now has the new column.

---

## Common Operations

### Adding a New Table

**Step 1**: Create the model in `models.py`
```python
class GameTag(Base):
    __tablename__ = "game_tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    appid = Column(Integer, ForeignKey("catalog_cache.appid"), nullable=False)
    tag_name = Column(String(100), nullable=False)
    
    def __repr__(self):
        return f"<GameTag(appid={self.appid}, tag='{self.tag_name}')>"
```

**Step 2**: Generate and apply migration
```powershell
alembic revision --autogenerate -m "Add game_tags table"
alembic upgrade head
```

---

### Modifying a Column

**Step 1**: Update the model
```python
# Change column type from String(255) to Text
username = Column(Text, nullable=False)  # Was: String(255)
```

**Step 2**: Generate and apply
```powershell
alembic revision --autogenerate -m "Change username to Text type"
alembic upgrade head
```

**Note**: Some changes require manual migration edits (e.g., renaming columns).

---

### Adding an Index

**In the model**:
```python
class UserGame(Base):
    __tablename__ = "user_games"
    
    user_steam_id = Column(BigInteger, ForeignKey("users.steam_id"))
    appid = Column(Integer, nullable=False)
    
    # Add index
    __table_args__ = (
        Index('idx_user_appid', 'user_steam_id', 'appid'),
    )
```

**Or using `index=True`**:
```python
appid = Column(Integer, nullable=False, index=True)
```

---

### Dropping a Table (BE CAREFUL!)

**Step 1**: Remove the model class from `models.py`

**Step 2**: Generate migration
```powershell
alembic revision --autogenerate -m "Drop old_table"
```

**Step 3**: Review the migration (make sure it's dropping the right table!)

**Step 4**: Apply
```powershell
alembic upgrade head
```

---

## Query Examples

### Filtering and Sorting

```python
# Get users who synced in the last 7 days
from datetime import datetime, timedelta
recent = datetime.now() - timedelta(days=7)
active_users = db.query(User).filter(User.last_sync >= recent).all()

# Get top 10 most played games for a user
top_games = db.query(UserGame)\
    .filter(UserGame.user_steam_id == steam_id)\
    .order_by(UserGame.playtime_hours.desc())\
    .limit(10)\
    .all()

# Get users with more than 100 games
power_users = db.query(User)\
    .join(UserGame)\
    .group_by(User.steam_id)\
    .having(func.count(UserGame.id) > 100)\
    .all()
```

---

### Joins

```python
# Get user with their games (eager loading)
user_with_games = db.query(User)\
    .options(joinedload(User.games))\
    .filter(User.steam_id == steam_id)\
    .first()

# Get all recommendations with game names
from sqlalchemy import join
recs = db.query(Recommendation, CatalogCache.name)\
    .join(CatalogCache, Recommendation.appid == CatalogCache.appid)\
    .filter(Recommendation.user_steam_id == steam_id)\
    .all()
```

---

### Aggregations

```python
# Total playtime for a user
total_hours = db.query(func.sum(UserGame.playtime_hours))\
    .filter(UserGame.user_steam_id == steam_id)\
    .scalar()

# Average engagement score
avg_engagement = db.query(func.avg(UserGame.engagement_score))\
    .filter(UserGame.user_steam_id == steam_id)\
    .scalar()

# Count by playtime category
category_counts = db.query(
    UserGame.playtime_category,
    func.count(UserGame.id)
).filter(UserGame.user_steam_id == steam_id)\
 .group_by(UserGame.playtime_category)\
 .all()
```

---

### Bulk Operations

```python
# Bulk insert (efficient for many rows)
games_to_insert = [
    UserGame(user_steam_id=steam_id, appid=app['appid'], playtime_hours=app['hours'])
    for app in games_data
]
db.bulk_save_objects(games_to_insert)
db.commit()

# Bulk update
db.query(UserGame)\
    .filter(UserGame.user_steam_id == steam_id)\
    .filter(UserGame.playtime_hours == 0)\
    .update({'playtime_category': 'unplayed'})
db.commit()
```

---

## Best Practices

### ✅ DO

1. **Always use migrations** - Never manually modify the database schema
   ```powershell
   alembic revision --autogenerate -m "Add column"
   alembic upgrade head
   ```

2. **Use transactions** - SQLAlchemy handles this automatically with `db.commit()`

3. **Close sessions** - Use `Depends(get_db)` in FastAPI (auto-closes)

4. **Use relationships** - Let SQLAlchemy handle joins
   ```python
   user.games  # Instead of manual JOIN query
   ```

5. **Add indexes** - For columns used in WHERE, JOIN, ORDER BY
   ```python
   appid = Column(Integer, index=True)
   ```

6. **Review auto-generated migrations** - Alembic isn't perfect, check the SQL!

7. **Test migrations on dev first** - Never run untested migrations on production

8. **Keep models and database in sync** - Run migrations after model changes

---

### ❌ DON'T

1. **Don't use raw SQL** - Unless absolutely necessary
   ```python
   # Bad
   db.execute("DELETE FROM users WHERE steam_id = 123")
   
   # Good
   user = db.query(User).filter(User.steam_id == 123).first()
   db.delete(user)
   ```

2. **Don't forget to commit**
   ```python
   db.add(new_user)
   # db.commit()  # DON'T FORGET THIS!
   ```

3. **Don't leave sessions open** - Always close or use context managers

4. **Don't use reserved words** - Like `metadata` (conflicts with SQLAlchemy)

5. **Don't skip migration reviews** - Always check auto-generated migrations

6. **Don't modify old migrations** - Create a new migration to fix issues

7. **Don't use `upgrade --sql` in production** - Apply migrations directly

---

## Troubleshooting

### Issue: "ImportError: attempted relative import with no known parent package"
**Cause**: Relative imports (`from .database import Base`) don't work when Alembic loads files.

**Solution**: Use absolute imports
```python
# Bad
from .database import Base

# Good
from database import Base
```

---

### Issue: "Attribute name 'metadata' is reserved"
**Cause**: `metadata` is reserved by SQLAlchemy's Base class.

**Solution**: Rename the column
```python
# Bad
metadata = Column(JSON)

# Good
game_metadata = Column(JSON)
```

---

### Issue: "Can't load plugin: sqlalchemy.dialects:driver"
**Cause**: Database URL is missing or incorrect.

**Solution**: Check `alembic.ini` and `.env`
```ini
# alembic.ini
sqlalchemy.url = postgresql+psycopg://user:pass@localhost/dbname
```

---

### Issue: "No module named 'psycopg2'"
**Cause**: Using `postgresql://` URL with psycopg3 installed.

**Solution**: Use `postgresql+psycopg://` URL format
```python
# .env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/steam_rec_db
```

---

### Issue: "Target database is not up to date"
**Cause**: Database is behind the code (migrations not applied).

**Solution**: Run migrations
```powershell
alembic upgrade head
```

---

### Issue: "Can't locate revision identified by '<revision>'"
**Cause**: Migration file is missing or database is out of sync.

**Solution**: Check migration history
```powershell
alembic history
alembic current
```

If database is corrupt, might need to `stamp` to reset:
```powershell
alembic stamp head  # Mark database as up-to-date (BE CAREFUL!)
```

---

### Issue: "Alembic detected added column but it already exists"
**Cause**: Database and models are out of sync.

**Solution**:
1. Drop the manually added column from database
2. OR: Edit the migration to skip that column
3. OR: Use `alembic stamp head` to mark as current (risky!)

---

## Useful Resources

### Official Documentation
- **SQLAlchemy 2.0 Docs**: https://docs.sqlalchemy.org/en/20/
- **Alembic Docs**: https://alembic.sqlalchemy.org/en/latest/
- **FastAPI with SQLAlchemy**: https://fastapi.tiangolo.com/tutorial/sql-databases/

### Quick References
- **SQLAlchemy Cheat Sheet**: https://www.pythonsheets.com/notes/python-sqlalchemy.html
- **Alembic Tutorial**: https://alembic.sqlalchemy.org/en/latest/tutorial.html

---

## Next Steps

Now that you understand SQLAlchemy and Alembic, you can:

1. ✅ **Day 1-2: Project Setup** - COMPLETE!
   - ✅ Backend structure created
   - ✅ PostgreSQL database created
   - ✅ SQLAlchemy models defined
   - ✅ Alembic migrations working
   - ✅ Environment variables configured

2. 🚀 **Day 3-4: Steam OAuth** - NEXT!
   - Implement Steam OpenID authentication
   - Create auth routes (login, callback, logout)
   - JWT token generation
   - User session management

Ready to move forward! 🎯
