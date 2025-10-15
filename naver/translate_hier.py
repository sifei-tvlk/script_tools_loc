from googletrans import Translator
import json

translator = Translator()
print(translator.translate("서울", src="ko", dest="en").text)

with open("./hier_dict.json", "r", encoding="utf-8") as json_file:
    hier_dict = json.load(json_file)

hier_dict_en = {}

for l1 in hier_dict:
    l1_en = translator.translate(l1, src="ko", dest="en").text
    print(l1, l1_en)
    hier_dict_en[l1_en] = {}
    for l2 in hier_dict[l1]:
        l2_en = translator.translate(l2, src="ko", dest="en").text
        print(" ", l2, l2_en)
        hier_dict_en[l1_en][l2_en] = {}
        for l3 in hier_dict[l1][l2]:
            l3_en = translator.translate(l3, src="ko", dest="en").text
            print("    ", l3, l3_en)
            hier_dict_en[l1_en][l2_en][l3_en] = {}
            for l4 in hier_dict[l1][l2][l3]:
                l4_en = translator.translate(l4, src="ko", dest="en").text
                print("        ", l4, l4_en)
                hier_dict_en[l1_en][l2_en][l3_en][l4_en] = {}

with open("./hier_dict_en.json", "w", encoding="utf-8") as json_file:
    json.dump(hier_dict_en, json_file, indent=4, ensure_ascii=False)