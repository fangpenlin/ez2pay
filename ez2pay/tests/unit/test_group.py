from __future__ import unicode_literals

from .helper import ModelTestCase

import transaction


class TestGroupModel(ModelTestCase):
        
    def make_one(self):
        from ez2pay.models.group import GroupModel
        return GroupModel(self.session)
    
    def make_permission_model(self):
        from ez2pay.models.permission import PermissionModel
        return PermissionModel(self.session)
    
    def test_create(self):
        model = self.make_one()
        
        group_name = 'tester'
        display_name = group_name
        
        with transaction.manager:
            group_id = model.create(
                group_name=group_name,
                display_name=display_name,
            )
        group = model.get(group_id)
        
        self.assertEqual(group.group_name, group_name)
        self.assertEqual(group.display_name, display_name)
        
    def test_update_permissions(self):
        model = self.make_one()
        permission_model = self.make_permission_model()
        
        group_name = 'tester'
        display_name = group_name
        
        with transaction.manager:
            group_id = model.create(
                group_name=group_name,
                display_name=display_name,
            )
            pid1 = permission_model.create('p1')
            pid2 = permission_model.create('p2')
            pid3 = permission_model.create('p3')
            
        group = model.get(group_id)
        pids = set([p.permission_id for p in group.permissions])
        self.assertEqual(pids, set([]))
            
        def assert_update(new_permissions):
            with transaction.manager:
                model.update_permissions(group_id, new_permissions)
            group = model.get(group_id)
            pids = set([p.permission_id for p in group.permissions])
            self.assertEqual(pids, set(new_permissions))
        
        assert_update([pid1])
        assert_update([pid1, pid2])
        assert_update([pid1, pid2, pid3])
        assert_update([pid1, pid3])
        assert_update([pid1])
        assert_update([])
        assert_update([pid1])
