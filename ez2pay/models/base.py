from __future__ import unicode_literals
import logging


class BaseTableModel(object):
    """Base model for table
    
    """

    #: the table object
    TABLE = None
    
    def __init__(self, session, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.session = session
        assert self.TABLE is not None, 'Table is not set'

    def get(self, record_id, raise_error=False):
        """Get a record by id
        
        """
        record = (
            self.session
            .query(self.TABLE)
            .get(record_id)
        )
        if raise_error and record is None:
            raise KeyError(
                '{0} {1} does not exist'
                .format(self.TABLE.__name__, record_id)
            )
        return record 

    def get_list(self, ids=None, offset=None, limit=None):
        """Get record list

        """
        from sqlalchemy.orm import class_mapper
        query = (
            self.session
            .query(self.TABLE)
        )
        if ids is not None:
            pk = class_mapper(self.TABLE).primary_key[0]
            query = query.filter(pk.in_(ids))
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query
