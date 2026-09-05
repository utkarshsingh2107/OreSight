import { useEffect, useRef } from "react";
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { Mine } from "../api/client";

export default function MapView({ mine }: { mine: Mine | null }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);

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
        },
        layers: [{ id: "osm", type: "raster", source: "osm" }],
      },
      center: [79.85, 21.8],
      zoom: 8,
    });
  }, []);

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
    <div className="overflow-hidden rounded-lg border border-white/10">
      <div ref={containerRef} style={{ height: 280, width: "100%" }} />
    </div>
  );
}
