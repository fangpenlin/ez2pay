from __future__ import unicode_literals

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import func


DeclarativeBase = declarative_base()
    
_now_func = [func.utc_timestamp]


def set_now_func(func):
    """Replace now function and return the old function
    
    """
    old = _now_func[0]
    _now_func[0] = func
    return old


def get_now_func():
    """Return current now func
    
    """
    return _now_func[0]


def now_func():
    """Return current datetime
    
    """
    func = get_now_func()
    return func()

# This is the association table for the many-to-many relationship between
# groups and permissions. This is required by repoze.what.
group_permission_table = Table(
    'group_permission', DeclarativeBase.metadata,
    Column(
        'group_id', 
        Integer, 
        ForeignKey(
            'group.group_id',
            onupdate='CASCADE', 
            ondelete='CASCADE'
        )
    ),
    Column(
        'permission_id', 
        Integer, 
        ForeignKey(
            'permission.permission_id',
            onupdate='CASCADE', 
            ondelete='CASCADE'
        )
    )
)

# This is the association table for the many-to-many relationship between
# groups and members - this is, the memberships. It's required by repoze.what.
user_group_table = Table(
    'user_group', 
    DeclarativeBase.metadata,
    Column(
        'user_id', 
        Integer, 
        ForeignKey(
            'user.user_id',
            onupdate='CASCADE', 
            ondelete='CASCADE'
        )
    ),
    Column(
        'group_id', 
        Integer, 
        ForeignKey(
            'group.group_id',
            onupdate='CASCADE', 
            ondelete='CASCADE'
        )
    )
)


class Group(DeclarativeBase):
    """A group is a bundle of users sharing same permissions
    
    """
    
    __tablename__ = 'group'
    
    group_id = Column(Integer, autoincrement=True, primary_key=True)
    
    group_name = Column(Unicode(16), unique=True, nullable=False)
    
    display_name = Column(Unicode(255))
    
    created = Column(DateTime, default=now_func)
    
    users = relationship('User', secondary=user_group_table, backref='groups')

    def __unicode__(self):
        return self.group_name


class User(DeclarativeBase):
    """A user is the entity contains attributes of a member account
    
    """
    __tablename__ = 'user'

    user_id = Column(Integer, autoincrement=True, primary_key=True)
    
    user_name = Column(Unicode(16), unique=True, nullable=False)
    
    email = Column(Unicode(255), unique=True)
    
    display_name = Column(Unicode(255))
    
    password = Column('password', String(80))

    verified = Column(Boolean, default=False)
    
    created = Column(DateTime, default=now_func)
    
    def __unicode__(self):
        return self.display_name or self.user_name
    
    @property
    def permissions(self):
        """Return a set of strings for the permissions granted."""
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms


class Permission(DeclarativeBase):
    """A permission indicates the operation can be performed by specific users
    
    """
    
    __tablename__ = 'permission'

    permission_id = Column(Integer, autoincrement=True, primary_key=True)
    
    permission_name = Column(Unicode(16), unique=True, nullable=False)
    
    description = Column(Unicode(255))
    
    groups = relationship(
        Group, 
        secondary=group_permission_table,
        backref='permissions'
    )

    def __unicode__(self):
        return self.permission_name
