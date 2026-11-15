/**
 * 03_accuracy_sampling.js */

var STUDY_AREA_ASSET = "projects/khadem-gis-rs/assets/LakeChad_Shp";
var MNDWI_THRESHOLD = 0.2;
var SCALE_M = 30;
var POINTS_PER_CLASS = 100;
var SEED = 42;
var EXPORT_FOLDER = "LakeChad";

var OBSERVATIONS = [
  {
    year: 1990,
    collection: "LANDSAT/LT05/C02/T1_L2",
    green: "SR_B2",
    swir: "SR_B5",
    start: "1990-04-01",
    end: "1990-06-30",
    maxCloud: 20,
  },
  {
    year: 2003,
    collection: "LANDSAT/LE07/C02/T1_L2",
    green: "SR_B2",
    swir: "SR_B5",
    start: "2003-04-01",
    end: "2003-06-30",
    maxCloud: 20,
  },
  {
    year: 2013,
    collection: "LANDSAT/LC08/C02/T1_L2",
    green: "SR_B3",
    swir: "SR_B6",
    start: "2013-04-01",
    end: "2013-06-30",
    maxCloud: 20,
  },
  {
    year: 2023,
    collection: "LANDSAT/LC08/C02/T1_L2",
    green: "SR_B3",
    swir: "SR_B6",
    start: "2023-04-01",
    end: "2023-06-30",
    maxCloud: 20,
  },
];

var geometry = ee.FeatureCollection(STUDY_AREA_ASSET).geometry();

function waterMask(obs) {
  var composite = ee
    .ImageCollection(obs.collection)
    .filterBounds(geometry)
    .filterDate(obs.start, obs.end)
    .filter(ee.Filter.lt("CLOUD_COVER", obs.maxCloud))
    .select([obs.green, obs.swir])
    .median()
    .multiply(0.0000275)
    .add(-0.2);
  return composite
    .normalizedDifference([obs.green, obs.swir])
    .gt(MNDWI_THRESHOLD)
    .clip(geometry)
    .rename("mapped")
    .toInt();
}

var samples = OBSERVATIONS.map(function (obs) {
  return waterMask(obs)
    .stratifiedSample({
      numPoints: POINTS_PER_CLASS,
      classBand: "mapped",
      region: geometry,
      scale: SCALE_M,
      classValues: [0, 1],
      classPoints: [POINTS_PER_CLASS, POINTS_PER_CLASS],
      seed: SEED,
      geometries: true,
    })
    .map(function (f) {
      return f.set("year", obs.year);
    });
});

// merge the per-year samples into one table
var points = samples.reduce(function (a, b) {
  return a.merge(b);
});

print("Points per year and mapped class:", points.aggregate_histogram("year"));
Map.addLayer(
  points.filter(ee.Filter.eq("mapped", 1)),
  { color: "blue" },
  "Mapped water points",
  false,
);
Map.addLayer(
  points.filter(ee.Filter.eq("mapped", 0)),
  { color: "orange" },
  "Mapped non-water points",
  false,
);

Export.table.toDrive({
  collection: points,
  description: "LakeChad_accuracy_points",
  folder: EXPORT_FOLDER,
  fileFormat: "CSV",
});
