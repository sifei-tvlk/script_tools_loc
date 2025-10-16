from googletrans import Translator
import json

translator = Translator()
print(translator.translate("서울", src="ko", dest="en").text)

with open("./hier_dict.json", "r", encoding="utf-8") as json_file:
    hier_dict = json.load(json_file)

with open("./hier_dict_test.json", "r", encoding="utf-8") as json_file:
    hier_dict_test = json.load(json_file)

hier_dict_en = {}

for l1, l1_value in hier_dict_test.items():
    l1_kr = l1_value['kr_name']
    l1_en = translator.translate(l1_kr, src="ko", dest="en").text
    print(l1_kr, l1_en)
    hier_dict_test[l1]['en_name'] = l1_en
    # for l2, l2_value in l1_value['sub_regions'].items():
    #     l2_kr = l2_value['kr_name']
    #     l2_en = translator.translate(l2_kr, src="ko", dest="en").text
    #     print(" ", l2_kr, l2_en)
    #     l2_value['en_name'] = l2_en
    #     for l3, l3_value in l2_value['sub_regions'].items():
    #         l3_kr = l3_value['kr_name']
    #         l3_en = translator.translate(l3_kr, src="ko", dest="en").text
    #         print("    ", l3_kr, l3_en)
    #         l3_value['en_name'] = l3_en
    #         for l4, l4_value in l3_value['sub_regions'].items():
    #             l4_kr = l4_value['kr_name']
    #             l4_en = translator.translate(l4_kr, src="ko", dest="en").text
    #             print("        ", l4_kr, l4_en)
    #             l4_value['en_name'] = l4_en
json.dump(hier_dict_test, open('hier_dict_test.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
# for l1 in hier_dict:
#     l1_en = translator.translate(l1, src="ko", dest="en").text
#     print(l1, l1_en)
#     hier_dict_en[l1_en] = {}
#     for l2 in hier_dict[l1]:
#         l2_en = translator.translate(l2, src="ko", dest="en").text
#         print(" ", l2, l2_en)
#         hier_dict_en[l1_en][l2_en] = {}
#         for l3 in hier_dict[l1][l2]:
#             l3_en = translator.translate(l3, src="ko", dest="en").text
#             print("    ", l3, l3_en)
#             hier_dict_en[l1_en][l2_en][l3_en] = {}
#             for l4 in hier_dict[l1][l2][l3]:
#                 l4_en = translator.translate(l4, src="ko", dest="en").text
#                 print("        ", l4, l4_en)
#                 hier_dict_en[l1_en][l2_en][l3_en][l4_en] = {}

# with open("./hier_dict_en.json", "w", encoding="utf-8") as json_file:
#     json.dump(hier_dict_en, json_file, indent=4, ensure_ascii=False)