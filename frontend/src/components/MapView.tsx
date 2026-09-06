import { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { Mine } from "../api/client";

type LayerType = "osm" | "satellite" | "geology" | "prospectivity" | "ndvi";

export default function MapView({ mine }: { mine: Mine | null }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [activeLayer, setActiveLayer] = useState<LayerType>("osm");
  const [showProspects, setShowProspects] = useState(false);
  const [showLineaments, setShowLineaments] = useState(false);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    mapRef.current = new maplibregl.Map({
      container: containerRef.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
            attribution: "© OpenStreetMap contributors",
          },
          satellite: {
            type: "raster",
            tiles: [
              "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            ],
            tileSize: 256,
            attribution: "© Esri",
          },
          sentinel2: {
            type: "raster",
            tiles: [
              "https://tiles.sentinel-hub.com/v1/wms?REQUEST=GetTile&BBOX={bbox}&WIDTH=256&HEIGHT=256&layers=TRUE_COLOR",
            ],
            tileSize: 256,
            attribution: "© ESA Sentinel-2",
          },
          geology: {
            type: "raster",
            tiles: [
              "https://tiles.example.com/geology/{z}/{x}/{y}.png",
            ],
            tileSize: 256,
            attribution: "© GSI Geology Map",
          },
          prospectivity: {
            type: "raster",
            tiles: [
              "https://tiles.example.com/prospectivity/{z}/{x}/{y}.png",
            ],
            tileSize: 256,
            attribution: "© OreSight Prospectivity Model",
          },
          ndvi: {
            type: "raster",
            tiles: [
              "https://tiles.example.com/ndvi/{z}/{x}/{y}.png",
            ],
            tileSize: 256,
            attribution: "© Sentinel-2 NDVI",
          },
        },
        layers: [
          { id: "osm", type: "raster", source: "osm", layout: { visibility: "visible" } },
          { id: "satellite", type: "raster", source: "satellite", layout: { visibility: "none" } },
          { id: "sentinel2", type: "raster", source: "sentinel2", layout: { visibility: "none" } },
          { id: "geology", type: "raster", source: "geology", layout: { visibility: "none" }, paint: { "raster-opacity": 0.7 } },
          { id: "prospectivity", type: "raster", source: "prospectivity", layout: { visibility: "none" }, paint: { "raster-opacity": 0.6 } },
          { id: "ndvi", type: "raster", source: "ndvi", layout: { visibility: "none" }, paint: { "raster-opacity": 0.65 } },
        ],
      },
      center: [79.85, 21.8],
      zoom: 8,
    });
  }, []);

  // Handle layer visibility changes
  useEffect(() => {
    if (!mapRef.current) return;

    // Hide all base layers
    ["osm", "satellite", "sentinel2"].forEach((layer) => {
      try {
        mapRef.current!.setLayoutProperty(layer, "visibility", "none");
      } catch {
        // Layer might not exist yet
      }
    });

    // Show selected base layer
    try {
      mapRef.current.setLayoutProperty(activeLayer, "visibility", "visible");
    } catch {
      // Fallback to OSM
      setActiveLayer("osm");
    }

    // Handle overlay layers
    try {
      mapRef.current.setLayoutProperty(
        "geology",
        "visibility",
        activeLayer === "geology" ? "visible" : "none"
      );
      mapRef.current.setLayoutProperty(
        "prospectivity",
        "visibility",
        showProspects ? "visible" : "none"
      );
      mapRef.current.setLayoutProperty(
        "ndvi",
        "visibility",
        activeLayer === "ndvi" ? "visible" : "none"
      );
    } catch {
      // Overlays might not exist yet
    }
  }, [activeLayer, showProspects]);

  useEffect(() => {
    if (!mapRef.current || !mine) return;
    mapRef.current.flyTo({ center: [mine.longitude, mine.latitude], zoom: 11 });

    const marker = new maplibregl.Marker({ color: "#38bdf8" })
      .setLngLat([mine.longitude, mine.latitude])
      .setPopup(new maplibregl.Popup().setText(`${mine.name} (${mine.mine_type})`))
      .addTo(mapRef.current);

    return () => {
      marker.remove();
    };
  }, [mine]);

  return (
    <div className="overflow-hidden rounded-lg border border-gray-700 bg-gray-800/50">
      {/* Layer Controls */}
      <div className="bg-gray-900/80 border-b border-gray-700 p-3 space-y-2">
        <p className="text-xs font-medium text-gray-300">Base Layer</p>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setActiveLayer("osm")}
            className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
              activeLayer === "osm"
                ? "bg-blue-600/80 text-white"
                : "bg-gray-700/50 text-gray-300 hover:bg-gray-700"
            }`}
          >
            🗺️ OSM
          </button>
          <button
            onClick={() => setActiveLayer("satellite")}
            className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
              activeLayer === "satellite"
                ? "bg-blue-600/80 text-white"
                : "bg-gray-700/50 text-gray-300 hover:bg-gray-700"
            }`}
          >
            🛰️ Satellite
          </button>
          <button
            onClick={() => setActiveLayer("geology")}
            className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
              activeLayer === "geology"
                ? "bg-blue-600/80 text-white"
                : "bg-gray-700/50 text-gray-300 hover:bg-gray-700"
            }`}
          >
            🪨 Geology
          </button>
          <button
            onClick={() => setActiveLayer("ndvi")}
            className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
              activeLayer === "ndvi"
                ? "bg-blue-600/80 text-white"
                : "bg-gray-700/50 text-gray-300 hover:bg-gray-700"
            }`}
          >
            🌱 NDVI
          </button>
        </div>

        <p className="text-xs font-medium text-gray-300 mt-3">Overlays</p>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setShowProspects(!showProspects)}
            className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
              showProspects
                ? "bg-green-600/80 text-white"
                : "bg-gray-700/50 text-gray-300 hover:bg-gray-700"
            }`}
          >
            💎 Prospectivity
          </button>
          <button
            onClick={() => setShowLineaments(!showLineaments)}
            className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
              showLineaments
                ? "bg-purple-600/80 text-white"
                : "bg-gray-700/50 text-gray-300 hover:bg-gray-700"
            }`}
          >
            ⚡ Lineaments
          </button>
        </div>
      </div>

      {/* Map Container */}
      <div ref={containerRef} style={{ height: 280, width: "100%" }} />

      {/* Legend */}
      <div className="bg-gray-900/80 border-t border-gray-700 p-3 text-xs text-gray-400">
        <p className="text-gray-300 font-medium mb-2">Active Layers:</p>
        <ul className="space-y-1 text-xs">
          <li>🔵 Base: <span className="text-blue-400">{activeLayer.toUpperCase()}</span></li>
          {showProspects && <li>💎 <span className="text-green-400">Prospectivity Heatmap (opacity 60%)</span></li>}
          {showLineaments && <li>⚡ <span className="text-purple-400">Structural Lineaments</span></li>}
        </ul>
      </div>
    </div>
  );
}
