from hackernews import HackerNews
from hackernews import Item 
from elasticsearch import Elasticsearch 
import json
import os

HOST=os.environ['ELASTICSEARCH_HOST']

hn = HackerNews()

mapping = {
    "mappings": {
    "hndoc":{
        "properties": {
            "title": {"type": "text"},
            "text": {"type":"text" },
            "submission_time": {"type": "date",
                                "format": "yyyy-MM-dd'T'HH:mm'Z'"},
            "time": {"type": "date",
                                "format": "yyyy-MM-dd'T'HH:mm'Z'"},
            "by": {"type": "text"},
            "dead": {"type": "boolean"},
            "parent": {"type": "text"},
            "poll": {"type":"text"},
            "url": {"type": "text"},
            "score": {"type":"integer" },
            "parts": {"type": "text"},
            "descendants": {"type": "text"},
            "kids": { 
                "properteis": {
                    "dynamic": "true"
                }
            }
        }
    }
  }
}

class DocumentEncoder(json.JSONEncoder): 
    def default(self,obj): 
        if isinstance(obj,Item):
            retDict = { "item_id": obj.item_id,
                     "text": obj.text, 
                     "deleted": obj.deleted,
                     "by": obj.by,
                     "submission_time": obj.submission_time.isoformat(), 
                     "dead" : obj.dead,
                     "parent" : obj.parent, 
                     "poll": obj.poll,
                     "score": obj.score, 
                     "title": obj.title, 
                     "descendants": obj.descendants, 
                     "time": obj.time.isoformat(), 
                    } 
            if obj.kids: 
                kids = [DocumentEncoder().encode(kid) for kid in obj.kids]
                retDict['kids'] = kids 
            return retDict
        else: 
            return json.JSONEncoder.default(self,obj)

def load_kids(hn,item,loaded_comments,flattened=None):
    flattened_kids = flattened or [] 
    to_load = [] 
    if (item.kids):
        for kid in item.kids: 
            if kid in loaded_comments: 
                flattened_kids.append(loaded_comments[kid]) 
            else: 
                to_load.append(kid)        
        loaded_kids = hn.get_items_by_ids(to_load)
        for kid in loaded_kids: 
            flattened_kids.append(kid)
        for kid in flattened_kids: 
            flattened_kids.extend(load_kids(hn,kid,loaded_comments))
    return flattened_kids 

def get_search_documents(): 
    items = hn.get_last(10000)
    comments = {} 
    parents = []
    for item in items: 
        if item.item_type == "comment": 
            comments[item.parent] = item
        else:
            parents.append(item) 
    for parent in parents:
        parent.kids = load_kids(hn,parent,comments) 
    return parents 
es = Elasticsearch(HOST)     
es.indices.create(index="hnindex",body=mapping)
search_documents=get_search_documents()
for document in search_documents: 
    es.index(index="hnindex",body=DocumentEncoder().encode(document))
# documents = [DocumentEncoder().encode(parent) for parent in parents]    
#     return documents