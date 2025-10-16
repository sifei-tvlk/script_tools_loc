import subprocess, json

def query_ollama_same_name(name_naver, list_db_name) -> bool:
    prompt = f"You are an expert in korean administrative geography. \
    I'm giving you a korean first level administrative region, and another list of first level administrative region alias, \
    find the best match region in the list for the given region. \
    There might be no best match. \
    Answer by the index in the list, or -1 if no best match. \n\
    Given region: {name_naver}\n\
    List of region alias: [{', '.join(list_db_name)}]\n\
    "
    result = subprocess.run(
        ["ollama", "run", "phi", prompt],
        capture_output=True, text=True
    )
    response = result.stdout
    return response


hier_dict_test = {}
hier_dict_test_file = 'hier_dict_test.json'
with open(hier_dict_test_file, 'r') as file:
    hier_dict_test = json.load(file)


db_data = {}
db_data_file = 'geojson/db/l1_infos.json'
with open(db_data_file, 'r') as file:
    db_data = json.load(file)

for naver_code in hier_dict_test:
    db_names = [x[1] for x in db_data]
    db_name_with_idx = [[idx, x[1]] for idx, x in enumerate(db_data)]
    naver_name = hier_dict_test[naver_code]['en_name']
    print(">>>naver_code", naver_code, "; naver_name:", naver_name)
    print(db_name_with_idx)
    print(query_ollama_same_name(naver_name, db_names))

# print(query_ollama_same_name("Seoul", "Seoul special city"))
