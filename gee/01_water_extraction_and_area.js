/**
 * 01_water_extraction_and_area.js
 * -----------------------------------------------------------------------------
 * Lake Chad open-water extent from Landsat Collection 2 Level-2 (MNDWI).
 * Observation years: 1990 (Landsat 5 TM), 2003 (Landsat 7 ETM+),
 *                    2013 and 2023 (Landsat 8 OLI); April-June composites.
 *
 * Run in the Google Earth Engine Code Editor (https://code.earthengine.google.com).
 *
 * Method (see manuscript, Section 2.5):
 *   - scene-level cloud filter (CLOUD_COVER < maxCloud), median composite
 *   - Collection 2 scale factor 0.0000275 and offset -0.2 (surface reflectance)
 *   - MNDWI = (Green - SWIR1) / (Green + SWIR1)
 *   - water = MNDWI > MNDWI_THRESHOLD (single threshold for all years)
 *   - area = sum of pixel areas of water pixels inside the study polygon
 *   - no pixel-level cloud/shadow mask is applied (as in the manuscript)
 *
 * Note: ee.Filter / filterDate treats the end date as EXCLUSIVE, so the
 * windows below end on 30 June without including that day. These are the
 * settings used for the reported results.
 * -----------------------------------------------------------------------------
 */

// ============================== CONFIGURATION ===============================
// Replace with the path of your own copy of the study-area polygon
// (the polygon is provided in data/study_area/ of the repository).
var STUDY_AREA_ASSET = 'projects/khadem-gis-rs/assets/LakeChad_Shp';

var MNDWI_THRESHOLD = 0.2;   // identical for all years
var SCALE_M         = 30;    // Landsat native resolution (m)
var EXPORT_MASKS    = false; // true: export binary water masks (GeoTIFF) to Drive
var EXPORT_FOLDER   = 'LakeChad';

// Landsat 5/7: Green = SR_B2, SWIR1 = SR_B5.  Landsat 8: Green = SR_B3, SWIR1 = SR_B6.
var OBSERVATIONS = [
  {year: 1990, collection: 'LANDSAT/LT05/C02/T1_L2', green: 'SR_B2', swir: 'SR_B5',
   start: '1990-04-01', end: '1990-06-30', maxCloud: 20,
   expectedKm2: 1860.40, expectedScenes: 4},
  {year: 2003, collection: 'LANDSAT/LE07/C02/T1_L2', green: 'SR_B2', swir: 'SR_B5',
   start: '2003-04-01', end: '2003-06-30', maxCloud: 20,
   expectedKm2: 1733.56, expectedScenes: 4},
  {year: 2013, collection: 'LANDSAT/LC08/C02/T1_L2', green: 'SR_B3', swir: 'SR_B6',
   start: '2013-04-01', end: '2013-06-30', maxCloud: 20,
   expectedKm2: 1440.44, expectedScenes: 14},
  {year: 2023, collection: 'LANDSAT/LC08/C02/T1_L2', green: 'SR_B3', swir: 'SR_B6',
   start: '2023-04-01', end: '2023-06-30', maxCloud: 20,
   expectedKm2: 1427.51, expectedScenes: 17}
];
var TOLERANCE_KM2 = 0.05;    // reproduction check tolerance
// ============================================================================

var studyArea = ee.FeatureCollection(STUDY_AREA_ASSET);
var geometry  = studyArea.geometry();

Map.centerObject(geometry, 7);
Map.addLayer(studyArea, {color: 'red'}, 'Study area', true);
print('Study-area polygon (km2):', geometry.area(1).divide(1e6));

/** Build the scene collection, MNDWI composite and binary water mask. */
function buildObservation(obs) {
  var scenes = ee.ImageCollection(obs.collection)
    .filterBounds(geometry)
    .filterDate(obs.start, obs.end)
    .filter(ee.Filter.lt('CLOUD_COVER', obs.maxCloud));

  var composite = scenes.select([obs.green, obs.swir])
    .median()
    .multiply(0.0000275).add(-0.2);

  var mndwi = composite.normalizedDifference([obs.green, obs.swir]).rename('MNDWI');
  var water = mndwi.gt(MNDWI_THRESHOLD).clip(geometry).rename('water');
  return {scenes: scenes, mndwi: mndwi, water: water};
}

/** Water area (km2) inside the study polygon. */
function waterAreaKm2(water) {
  var sum = water.multiply(ee.Image.pixelArea()).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: geometry,
    scale: SCALE_M,
    maxPixels: 1e13
  });
  return ee.Number(sum.get('water')).divide(1e6);
}

var palette = {1990: '003087', 2003: '0055AA', 2013: '0088CC', 2023: '00BBFF'};

OBSERVATIONS.forEach(function (obs) {
  var o = buildObservation(obs);
  var area = waterAreaKm2(o.water);
  var nScenes = o.scenes.size();

  Map.addLayer(o.water.selfMask(), {palette: [palette[obs.year]]}, 'Water ' + obs.year, false);

  print('--- ' + obs.year + ' (' + obs.collection + ') ---');
  print('Scenes used:', nScenes, '(expected ' + obs.expectedScenes + ')');
  print('Water area (km2):', area, '(expected ' + obs.expectedKm2.toFixed(2) + ')');
  print('Reproduction check:', ee.Algorithms.If(
    area.subtract(obs.expectedKm2).abs().lt(TOLERANCE_KM2), 'OK', 'DIFFERS - see README'));

  if (EXPORT_MASKS) {
    Export.image.toDrive({
      image: o.water.toByte(),
      description: 'LakeChad_water_' + obs.year,
      folder: EXPORT_FOLDER,
      fileNamePrefix: 'water_' + obs.year,
      region: geometry,
      scale: SCALE_M,
      crs: 'EPSG:4326',
      maxPixels: 1e13
    });
  }
});
