from pprint import pprint;

from tree.walk import walk;

obj = walk(r".");


import pickle as pkl;
with open("test/out/test-walk.pkl", "wb") as f:
    pkl.dump(obj, f);

import json;
class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)
with open("test/out/test-walk.json", "w") as f:
    json.dump(obj, f, cls=SetEncoder);