import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { DayAheadRecord } from "../api";

export function ErrorDist({ records }: { records: DayAheadRecord[] }) {
  const data = records.map((record) => ({
    time: new Date(record.startTime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    residual: record.residual_mw,
  }));

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Residual analysis</p>
          <h2>Error distribution</h2>
        </div>
      </div>
      <div className="small-chart">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <XAxis dataKey="time" hide />
            <YAxis stroke="#718096" tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ background: "#131d2b", border: "1px solid #2b3a4e" }} />
            <Bar dataKey="residual" name="Residual (MW)" fill="#f2a65a" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
