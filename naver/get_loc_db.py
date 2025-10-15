from ../LocgiApi import get_geo_with_geometry_by_id, get_children_geo_by_id
from UserUtils import get_locgi_url
from llm_tool import get_llm_response

locgi_url = get_locgi_url('staging')

hier_dict_test = {}
hier_dict_test_file = 'hier_dict_test.json'
with open(hier_dict_test_file, 'r') as file:
    hier_dict_test = json.load(file)

sk_id = 20004311

l1_ids = get_children_geo_by_id(sk_id, locgi_url)

for l1_id in l1_ids:
    result = get_geo_with_geometry_by_id(l1_id, locgi_url)
    print(result)

# level 1 name checking
get_llm_response(result.name, )