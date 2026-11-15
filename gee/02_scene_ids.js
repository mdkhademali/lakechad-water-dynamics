/**
 * 02_scene_ids.js */

var STUDY_AREA_ASSET = "projects/khadem-gis-rs/assets/LakeChad_Shp";
var EXPORT_FOLDER = "LakeChad";

var OBSERVATIONS = [
  {
    year: 1990,
    collection: "LANDSAT/LT05/C02/T1_L2",
    start: "1990-04-01",
    end: "1990-06-30",
    maxCloud: 20,
  },
  {
    year: 2003,
    collection: "LANDSAT/LE07/C02/T1_L2",
    start: "2003-04-01",
    end: "2003-06-30",
    maxCloud: 20,
  },
  {
    year: 2013,
    collection: "LANDSAT/LC08/C02/T1_L2",
    start: "2013-04-01",
    end: "2013-06-30",
    maxCloud: 20,
  },
  {
    year: 2023,
    collection: "LANDSAT/LC08/C02/T1_L2",
    start: "2023-04-01",
    end: "2023-06-30",
    maxCloud: 20,
  },
];

var geometry = ee.FeatureCollection(STUDY_AREA_ASSET).geometry();

var perYear = OBSERVATIONS.map(function (obs) {
  var scenes = ee
    .ImageCollection(obs.collection)
    .filterBounds(geometry)
    .filterDate(obs.start, obs.end)
    .filter(ee.Filter.lt("CLOUD_COVER", obs.maxCloud))
    .sort("system:time_start");

  return ee.FeatureCollection(
    scenes.map(function (img) {
      return ee.Feature(null, {
        year: obs.year,
        collection: obs.collection,
        scene_id: img.get("system:index"),
        acquisition_date: ee
          .Date(img.get("system:time_start"))
          .format("YYYY-MM-dd"),
        cloud_cover: img.get("CLOUD_COVER"),
        wrs_path: img.get("WRS_PATH"),
        wrs_row: img.get("WRS_ROW"),
      });
    }),
  );
});

// merge the per-year collections into one table
var table = perYear.reduce(function (a, b) {
  return a.merge(b);
});

print(
  "Scenes per observation year:",
  ee.Dictionary(table.aggregate_histogram("year")),
);
print("Scene list:", table);

Export.table.toDrive({
  collection: table,
  description: "LakeChad_scene_ids",
  folder: EXPORT_FOLDER,
  fileFormat: "CSV",
  selectors: [
    "year",
    "collection",
    "scene_id",
    "acquisition_date",
    "cloud_cover",
    "wrs_path",
    "wrs_row",
  ],
});
