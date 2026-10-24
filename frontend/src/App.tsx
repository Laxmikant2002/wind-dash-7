import { useEffect, useState } from "react";
import { Activity, RefreshCw, Wind } from "lucide-react";
import { getDayAhead, type DayAheadResponse } from "./api";
import { DayAheadView } from "./components/DayAheadView";
import { ErrorDist } from "./components/ErrorDist";
import { MetricsCard } from "./components/MetricsCard";
import "./styles.css";

export default function App() {
  const [data, setData] = useState<DayAheadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [deliveryDate, setDeliveryDate] = useState("2026-01-15");

  const refresh = async () => {
    try {
      setError(null);
      setData(await getDayAhead(deliveryDate));
    } catch {
      setError("Unable to reach the data service. Check that the backend is running.");
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark"><Wind size={21} /></span><span>Grid / Elexon</span></div>
        <button className="refresh-button" onClick={() => void refresh()}><RefreshCw size={16} /> Refresh</button>
      </header>
      <div className="content">
        <div className="hero">
          <div><p className="eyebrow">Decision cockpit / UK wind</p><h1>Day-ahead performance</h1><p className="subtitle">January 2026 forecast accuracy at the 11:00 GMT purchase decision cut-off.</p></div>
          <div className="status"><Activity size={16} /> Live monitoring</div>
        </div>
        {error && <div className="error">{error}</div>}
        <div className="date-picker"><label htmlFor="delivery-date">Delivery day</label><input id="delivery-date" type="date" min="2026-01-01" max="2026-01-31" value={deliveryDate} onChange={(event) => setDeliveryDate(event.target.value)} /><button className="refresh-button" onClick={() => void refresh()}>Load day</button></div>
        {data && <><MetricsCard metrics={data.metrics} /><div className="main-grid"><DayAheadView records={data.records} /><ErrorDist records={data.records} /></div></>}
        {!data && !error && <div className="loading">Loading generation data…</div>}
      </div>
    </main>
  );
}
