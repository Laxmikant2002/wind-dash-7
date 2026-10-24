import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { DayAheadRecord } from "../api";

export function DayAheadView({ records }: { records: DayAheadRecord[] }) {
  const data = records.map((record) => ({
    ...record,
    time: new Date(record.startTime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
  }));

  return (
    <section className="panel chart-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Generation profile</p>
          <h2>Forecast vs actuals</h2>
        </div>
        <span className="badge">Last 24 hours</span>
      </div>
      <div className="chart">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 16, right: 12, left: -16, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#243142" vertical={false} />
            <XAxis dataKey="time" stroke="#718096" tickLine={false} axisLine={false} />
            <YAxis stroke="#718096" tickLine={false} axisLine={false} unit=" MW" />
            <Tooltip contentStyle={{ background: "#131d2b", border: "1px solid #2b3a4e" }} />
            <Legend />
            <Line type="monotone" dataKey="actual_mw" name="Actual" stroke="#45d6a4" strokeWidth={3} dot={false} />
            <Line type="monotone" dataKey="forecast_mw" name="Forecast" stroke="#65a9ff" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
