from google.cloud import datastore

class DatastoreClient(object):
    def __init__(self):
        self.datastore_client = datastore.Client()

    def page_to_list(self, page):
        entities = []
        while page.remaining > 0:
            entities.append(next(page))
        return entities

    def query(self, kind, cursor=None, filters=None, limit=10):
        query = self.datastore_client.query(kind=kind)
        if filters:
            for filter in filters:
                query.add_filter(*filter)
        query_iterator = query.fetch(limit=limit, start_cursor=cursor)
        page = next(query_iterator.pages)
        entities = self.page_to_list(page)
        return entities

    def get_from_id(self, kind, id):
        key = self.datastore_client.key(kind, id)
        results = self.datastore_client.get(key)
        return results

    def update(self, key, data, id=None):
        if id:
            key = self.datastore_client.key(key, id)
        else:
            key = self.datastore_client.key(key)
        entity = datastore.Entity(
            key=key,
            exclude_from_indexes=['description'])
        entity.update(data)
        self.datastore_client.put(entity)
