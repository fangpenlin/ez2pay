from __future__ import unicode_literals

from .helper import ModelTestCase

import transaction


class TestPermissionModel(ModelTestCase):
        
    def make_one(self):
        from ez2pay.models.permission import PermissionModel
        return PermissionModel(self.session)
    
    def test_create(self):
        model = self.make_one()
        
        permission_name = 'test'
        description = permission_name
        
        with transaction.manager:
            permission_id = model.create(
                permission_name=permission_name,
                description=description,
            )
        permission = model.get(permission_id)
        
        self.assertEqual(permission.permission_name, permission_name)
        self.assertEqual(permission.description, description)
