"use client";

import { useState } from "react";
import { offerCompare, type OfferCompareResult } from "@/lib/api";
import RequireAuth from "@/lib/RequireAuth";

interface Offer { company: string; salary: string; benefits: string; commute: string; growth: string }

const EMPTY_OFFER: Offer = { company: "", salary: "", benefits: "", commute: "", growth: "" };

const FIELDS: { key: keyof Offer; label: string; placeholder: string }[] = [
  { key: "company", label: "公司名", placeholder: "例如：字节跳动" },
  { key: "salary", label: "薪资", placeholder: "例如：35K x 15" },
  { key: "benefits", label: "福利", placeholder: "例如：六险一金、年假15天" },
  { key: "commute", label: "通勤", placeholder: "例如：40分钟地铁" },
  { key: "growth", label: "发展前景", placeholder: "例如：核心业务线、晋升明确" },
];

export default function OfferComparePage() {
  return <RequireAuth><OfferCompareContent /></RequireAuth>;
}

function OfferCompareContent() {
  const [offers, setOffers] = useState<Offer[]>([{ ...EMPTY_OFFER }, { ...EMPTY_OFFER }]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<OfferCompareResult | null>(null);

  function updateOffer(i: number, field: keyof Offer, value: string) {
    setOffers(offers.map((o, idx) => (idx === i ? { ...o, [field]: value } : o)));
  }

  async function handleCompare() {
    const filled = offers.filter((o) => o.company.trim());
    if (filled.length < 2) return setError("请至少填写 2 个 Offer");
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const data = await offerCompare(filled);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "请求失败");
    } finally {
      setLoading(false);
    }
  }

  const sc = (s: number) => (s >= 8 ? "text-green-600" : s >= 6 ? "text-yellow-600" : "text-red-500");

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Offer 对比</h1>
        <p className="mt-1 text-gray-500">多维度对比 Offer，AI 生成评分表与综合建议</p>
      </div>

      {/* Offer cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {offers.map((o, i) => (
          <div key={i} className="rounded-xl border bg-white p-5 shadow-sm">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-semibold text-gray-500">Offer {i + 1}</span>
              {offers.length > 2 && (
                <button onClick={() => setOffers(offers.filter((_, idx) => idx !== i))} className="text-xs text-red-400 hover:text-red-600">移除</button>
              )}
            </div>
            {FIELDS.map((f) => (
              <div key={f.key} className="mb-2">
                <label className="mb-0.5 block text-xs text-gray-400">{f.label}</label>
                <input
                  className="w-full rounded border px-2.5 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  placeholder={f.placeholder}
                  value={o[f.key]}
                  onChange={(e) => updateOffer(i, f.key, e.target.value)}
                />
              </div>
            ))}
          </div>
        ))}
        {offers.length < 5 && (
          <button
            onClick={() => setOffers([...offers, { ...EMPTY_OFFER }])}
            className="flex min-h-[200px] items-center justify-center rounded-xl border-2 border-dashed border-gray-300 text-gray-400 hover:border-blue-400 hover:text-blue-400"
          >
            + 添加 Offer
          </button>
        )}
      </div>

      <div className="flex items-center gap-4">
        <button onClick={handleCompare} disabled={loading} className="rounded-lg bg-blue-600 px-6 py-2.5 font-medium text-white hover:bg-blue-700 disabled:opacity-50">
          {loading ? "分析中..." : "开始对比分析"}
        </button>
        {error && <p className="text-sm text-red-500">{error}</p>}
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          <div className="overflow-x-auto rounded-xl border bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead className="border-b bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium">公司</th>
                  <th className="px-3 py-3 text-center">薪资</th>
                  <th className="px-3 py-3 text-center">福利</th>
                  <th className="px-3 py-3 text-center">通勤</th>
                  <th className="px-3 py-3 text-center">发展</th>
                  <th className="px-4 py-3 text-center font-medium">综合</th>
                </tr>
              </thead>
              <tbody>
                {result.score_table.map((row, i) => (
                  <tr key={i} className="border-b last:border-0">
                    <td className="px-4 py-3 font-medium">{row.company}</td>
                    <td className={`px-3 py-3 text-center font-mono ${sc(row.salary_score)}`}>{row.salary_score}</td>
                    <td className={`px-3 py-3 text-center font-mono ${sc(row.benefits_score)}`}>{row.benefits_score}</td>
                    <td className={`px-3 py-3 text-center font-mono ${sc(row.commute_score)}`}>{row.commute_score}</td>
                    <td className={`px-3 py-3 text-center font-mono ${sc(row.growth_score)}`}>{row.growth_score}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-bold text-white ${row.overall >= 8 ? "bg-green-500" : row.overall >= 6 ? "bg-yellow-500" : "bg-red-400"}`}>
                        {row.overall}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h3 className="mb-3 font-semibold text-blue-700">综合分析建议</h3>
            <div className="whitespace-pre-wrap text-sm leading-relaxed text-gray-700">{result.analysis}</div>
          </div>
        </div>
      )}
    </div>
  );
}
