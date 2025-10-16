# import sys
# import json
# import osmium

# geojson_factory = osmium.geom.GeoJSONFactory()

# class PolygonHandler(osmium.SimpleHandler):
#     def __init__(self):
#         super().__init__()
#         self.features = []

#     def area(self, a):
#         # Only keep areas with tags (otherwise it's just geometry with no meaning)
#         if a.tags:
#             try:
#                 geom = geojson_factory.create_multipolygon(a)
#                 g = json.loads(geom)
#                 feature = {
#                     "type": "Feature",
#                     "geometry": g,
#                     "properties": dict(a.tags)
#                 }
#                 self.features.append(feature)
#             except Exception as e:
#                 # Some geometries may be invalid or incomplete
#                 print(f"Skipping area {a.id}: {e}")

# def convert(osmfile, outfile):
#     handler = PolygonHandler()
#     handler.apply_file(osmfile, locations=True)
#     fc = {
#         "type": "FeatureCollection",
#         "features": handler.features
#     }
#     with open(outfile, "w", encoding="utf-8") as f:
#         json.dump(fc, f, ensure_ascii=False, indent=2)

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print(f"Usage: python {sys.argv[0]} input.osm.pbf output.geojson")
#         sys.exit(1)
#     convert(sys.argv[1], sys.argv[2])

import sys
import json
import osmium

geojson_factory = osmium.geom.GeoJSONFactory()

class AdminBoundaryHandler(osmium.SimpleHandler):
    def __init__(self, levels):
        super().__init__()
        self.levels = set(str(l) for l in levels)
        self.features = []

    def area(self, a):
        if a.tags.get("boundary") == "administrative":
            print(a)
            level = a.tags.get("admin_level")
            if level in self.levels:
                try:
                    geom = geojson_factory.create_multipolygon(a)
                    g = json.loads(geom)
                    feature = {
                        "type": "Feature",
                        "geometry": g,
                        "properties": {
                            "id": a.id,
                            "name": a.tags.get("name"),
                            "admin_level": level,
                            **dict(a.tags)
                        }
                    }
                    self.features.append(feature)
                except Exception as e:
                    print(f"Skipping area {a.id}: {e}")
            return

def convert(osmfile, outfile, levels):
    handler = AdminBoundaryHandler(levels)
    handler.apply_file(osmfile, locations=True)
    fc = {
        "type": "FeatureCollection",
        "features": handler.features
    }
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} input.osm.pbf output.geojson [levels...]")
        sys.exit(1)

    osmfile = sys.argv[1]
    outfile = sys.argv[2]
    levels = sys.argv[3:] if len(sys.argv) > 3 else [2,4,6,8]

    convert(osmfile, outfile, levels)
