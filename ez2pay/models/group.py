from __future__ import unicode_literals

from . import tables
from .base import BaseTableModel


class GroupModel(BaseTableModel):
    """Group data model
    
    """
    TABLE = tables.Group

    def get_by_name(self, group_name):
        """Get a group by name
        
        """
        group = (
            self.session
            .query(tables.Group)
            .filter_by(group_name=group_name)
            .first()
        )
        return group
    
    def create(
        self, 
        group_name, 
        display_name=None,
    ):
        """Create a new group and return its id
        
        """
        group = tables.Group(
            group_name=unicode(group_name), 
            display_name=unicode(display_name) if display_name is not None else None, 
            created=tables.now_func()
        )
        self.session.add(group)
        # flush the change, so we can get real user id
        self.session.flush()
        assert group.group_id is not None, 'Group id should not be none here'
        group_id = group.group_id
        
        self.logger.info('Create group %s', group_name)
        return group_id
    
    def update_group(self, group_id, **kwargs):
        """Update attributes of a group
        
        """
        group = self.get(group_id, raise_error=True)
        if 'display_name' in kwargs:
            group.display_name = kwargs['display_name']
        if 'group_name' in kwargs:
            group.group_name = kwargs['group_name']
        self.session.add(group)
    
    def update_permissions(self, group_id, permission_ids):
        """Update permissions of this group
        
        """
        group = self.get(group_id, raise_error=True)
        new_permissions = (
            self.session
            .query(tables.Permission)
            .filter(tables.Permission.permission_id.in_(permission_ids))
        )
        group.permissions = new_permissions.all()
        self.session.flush()
