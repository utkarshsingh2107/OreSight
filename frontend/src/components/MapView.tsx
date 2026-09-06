import { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { Mine, ProspectivityTarget } from "../api/client";

const CONFIDENCE_COLORS: Record<string, string> = {
  high: "#f59e0b",
  medium: "#fb923c",
  low: "#94a3b8",
};

export default function MapView({
  mine,
  allMines = [],
  onSelectMine,
  prospectivityTargets,
}: {
  mine: Mine | null;
  allMines?: Mine[];
  onSelectMine?: (mine: Mine) => void;
  prospectivityTargets: ProspectivityTarget[];
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const mineMarkersRef = useRef<maplibregl.Marker[]>([]);

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

    mapRef.current.addControl(new maplibregl.NavigationControl(), "top-right");
  }, []);

  // Center on active mine if selected
  useEffect(() => {
    if (!mapRef.current || !mine) return;
    mapRef.current.flyTo({ center: [mine.longitude, mine.latitude], zoom: 10, essential: true });
  }, [mine]);

  // Render all mine markers
  useEffect(() => {
    if (!mapRef.current) return;

    // Clear previous mine markers
    mineMarkersRef.current.forEach((m) => m.remove());
    mineMarkersRef.current = [];

    const minesToDisplay = allMines.length > 0 ? allMines : (mine ? [mine] : []);

    minesToDisplay.forEach((m) => {
      const isSelected = mine?.id === m.id;
      const el = document.createElement("div");
      el.style.cursor = "pointer";
      el.innerHTML = isSelected
        ? `<div style="background:#38bdf8;width:18px;height:18px;border-radius:50%;border:2.5px solid white;box-shadow:0 0 12px #38bdf8;animation:pulse 2s infinite"></div>`
        : `<div style="background:#0284c7;width:12px;height:12px;border-radius:50%;border:2px solid #e0f2fe;box-shadow:0 0 4px #0284c7"></div>`;

      if (onSelectMine) {
        el.addEventListener("click", () => onSelectMine(m));
      }

      const popupHtml = `
        <div style="font-family:sans-serif;padding:4px">
          <strong style="color:${isSelected ? "#38bdf8" : "#0284c7"}">${m.name}</strong><br/>
          <span style="font-size:11px;color:#94a3b8">${m.mine_type} · ${m.state}</span><br/>
          <span style="font-size:10px;color:#64748b">Target: ${m.monthly_target_tonnes.toLocaleString()} t/mo</span>
        </div>
      `;

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([m.longitude, m.latitude])
        .setPopup(new maplibregl.Popup({ offset: 12 }).setHTML(popupHtml))
        .addTo(mapRef.current!);

      mineMarkersRef.current.push(marker);
    });

    return () => {
      mineMarkersRef.current.forEach((m) => m.remove());
      mineMarkersRef.current = [];
    };
  }, [allMines, mine, onSelectMine]);

  // Prospectivity target markers
  useEffect(() => {
    if (!mapRef.current || prospectivityTargets.length === 0) return;

    const newMarkers: maplibregl.Marker[] = [];

    prospectivityTargets.forEach((t) => {
      const color = CONFIDENCE_COLORS[t.confidence] ?? "#94a3b8";
      const el = document.createElement("div");
      el.innerHTML = `
        <div style="
          background:${color};
          width:${t.rank <= 3 ? 16 : 12}px;
          height:${t.rank <= 3 ? 16 : 12}px;
          border-radius:3px;
          border:2px solid white;
          box-shadow:0 0 6px ${color};
          cursor:pointer;
          display:flex;align-items:center;justify-content:center;
          font-size:8px;font-weight:bold;color:white;
        ">${t.rank}</div>`;

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([t.lon, t.lat])
        .setPopup(
          new maplibregl.Popup({ offset: 12 }).setHTML(
            `<div style="font-family:sans-serif;padding:4px;min-width:160px">
              <strong style="color:${color}">Target #${t.rank}</strong><br/>
              <span style="font-size:11px;color:#94a3b8">Probability: ${Math.round(t.probability * 100)}%</span><br/>
              <span style="font-size:11px;color:#94a3b8">Confidence: ${t.confidence}</span><br/>
              <span style="font-size:11px;color:#94a3b8">Near: ${t.nearest_mine ?? "—"}</span><br/>
              <span style="font-size:11px;color:#64748b">Iron oxide: ${t.evidence.iron_oxide_index.toFixed(2)} · NDVI Δ: ${t.evidence.ndvi_anomaly.toFixed(2)}</span>
            </div>`,
          ),
        )
        .addTo(mapRef.current!);

      newMarkers.push(marker);
    });

    return () => {
      newMarkers.forEach((m) => m.remove());
    };
  }, [prospectivityTargets]);

  return (
    <div className="rounded-xl border border-white/10 bg-slate-800/60 overflow-hidden">
      {/* Map header with legend */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-white/10">
        <div className="flex items-center gap-2">
          <span className="text-sm">🗺️</span>
          <span className="text-xs font-semibold text-slate-300">Balaghat District, MP</span>
        </div>
        <div className="flex items-center gap-3 text-[10px] text-slate-400">
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-sky-400 shadow-[0_0_4px_#38bdf8]" />
            Active mine
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded bg-amber-400 shadow-[0_0_4px_#f59e0b]" />
            High confidence target
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded bg-orange-400" />
            Medium
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded bg-slate-400" />
            Low
          </span>
        </div>
      </div>
      <div ref={containerRef} style={{ height: 360, width: "100%" }} />
    </div>
  );
}
