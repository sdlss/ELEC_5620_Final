// index.tsx
// User Dashboard: show last analysis summary and quick actions.

// @ts-nocheck
import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { getToken } from '../utils/auth';

type LastAnalysis = {
	case_id?: string;
	status?: string;
	analysis?: {
		model?: string;
		issue_description?: string;
		analysis?: string;
		key_points?: string[];
		steps?: string[];
	}
}

type HistoryItem = {
	case_id: string;
	analysis: LastAnalysis['analysis'];
	created_at?: string;
	status?: string;
}

const cardStyle: React.CSSProperties = {
	background: '#fff',
	border: '1px solid #e5e7eb',
	borderRadius: 12,
	padding: 16,
	boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
};

const IndexPage: React.FC = () => {
	const [last, setLast] = useState<LastAnalysis | null>(null);
		const [loaded, setLoaded] = useState(false);
		const [history, setHistory] = useState<HistoryItem[]>([]);
		const router = useRouter();

		// If user visits '/', redirect them to the login page only when not authenticated
		useEffect(() => {
			try {
				const token = getToken();
				if (!token && router && router.replace) {
					router.replace('/login');
				}
			} catch {}
		}, [router]);

	useEffect(() => {
		try {
			const raw = localStorage.getItem('lastAnalysis');
			if (raw) {
				try {
					const parsed = JSON.parse(raw);
					// Only accept persisted analyses that include a created_at timestamp
					if (parsed && parsed.created_at) {
						setLast(parsed);
					}
				} catch {}
			}
				const hraw = localStorage.getItem('analysisHistory');
				if (hraw) {
					try {
						const arr = JSON.parse(hraw);
						if (Array.isArray(arr)) {
							// Only keep history items that look like real user uploads (have created_at)
							const filtered = arr.filter((it: any) => it && it.created_at);
							setHistory(filtered);
						}
					} catch {}
				}
		} catch {}
		setLoaded(true);
	}, []);

	const handleClear = () => {
		localStorage.removeItem('lastAnalysis');
		setLast(null);
	};

	const keyPoints = last?.analysis?.key_points ?? [];
	const steps = last?.analysis?.steps ?? [];

	// Helper: extract a leading JSON object from a string and return parsed + remainder
	const extractLeadingJson = (s: string): { parsed: any | null; remainder: string | null } => {
		if (!s || typeof s !== 'string') return { parsed: null, remainder: null };
		const str = s.trim();
		if (!str.startsWith('{')) return { parsed: null, remainder: str };
		let depth = 0;
		let inString = false;
		let escape = false;
		for (let i = 0; i < str.length; i++) {
			const ch = str[i];
			if (escape) { escape = false; continue; }
			if (ch === '\\') { escape = true; continue; }
			if (ch === '"') { inString = !inString; continue; }
			if (inString) continue;
			if (ch === '{') depth += 1;
			if (ch === '}') depth -= 1;
			if (depth === 0) {
				const candidate = str.substring(0, i + 1);
				try {
					const parsed = JSON.parse(candidate);
					const remainder = str.substring(i + 1).trim();
					return { parsed, remainder: remainder.length ? remainder : null };
				} catch (e) {
					// continue
				}
			}
		}
		// fallback: try parse whole
		try { return { parsed: JSON.parse(str), remainder: null }; } catch (e) { return { parsed: null, remainder: str }; }
	};

	// Status helpers: color mapping + optional progress
	const lastStatus = last?.status || (last?.analysis ? 'Analyzed' : '—');

	const getStatusStyle = (status: string) => {
		const s = (status || '').toLowerCase();
		// success
		if (['refund_completed', 'platform_decision_approved'].includes(s)) {
			return { bg: '#d1fae5', color: '#065f46', border: '#10b981' }; // green
		}
		// in-progress
		if ([
			'submitted_to_platform', 'return_in_transit', 'seller_warehouse_received',
			'refund_processing', 'platform_investigating',
		].includes(s) || s.startsWith('analyzing_') || s === 'analysis_completed') {
			return { bg: '#dbeafe', color: '#1e40af', border: '#3b82f6' }; // blue
		}
		// user action pending
		if (['awaiting_user_evidence', 'buyer_ship_return'].includes(s)) {
			return { bg: '#fffbeb', color: '#92400e', border: '#f59e0b' }; // amber
		}
		// error/closed
		if ([
			'refund_rejected', 'platform_decision_rejected', 'closed_no_action', 'analysis_failed'
		].includes(s)) {
			return { bg: '#fee2e2', color: '#991b1b', border: '#ef4444' }; // red
		}
		// default neutral
		return { bg: '#f3f4f6', color: '#111827', border: '#e5e7eb' }; // gray
	};

	const statusStyle = getStatusStyle(lastStatus);
	const progressPercentRaw = (
		last?.progress_percent ??
		last?.progressPercent ??
		(last && last.progress && (last.progress.percent ?? last.progress.progress_percent)) ??
		(last && last.analysis && (last.analysis.progress_percent ?? last.analysis.progressPercent))
	);
	let progressPercent: number | null = null;
	if (typeof progressPercentRaw === 'number' && isFinite(progressPercentRaw)) {
		progressPercent = Math.max(0, Math.min(100, Math.round(progressPercentRaw)));
	}

		const openHistoryItem = (item: HistoryItem) => {
			try {
				localStorage.setItem('lastAnalysis', JSON.stringify(item));
			} catch {}
			router.push('/result');
		};

		const clearHistory = () => {
			// Remove stored history and also clear the last analysis to avoid stale UI
			localStorage.removeItem('analysisHistory');
			localStorage.removeItem('lastAnalysis');
			setHistory([]);
			setLast(null);
		};

	return (
		<div style={{ minHeight: '100vh', background: '#f7f7f9' }}>
			<div style={{ maxWidth: 1040, margin: '0 auto', padding: '24px 16px' }}>
				{/* Header */}
				<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
					<div>
						<h1 style={{ margin: 0 }}>User Dashboard</h1>
						<p style={{ color: '#6b7280', margin: '4px 0 0' }}>Manage your cases and view latest analysis.</p>
					</div>
					<Link href="/upload" style={{
						background: '#111827', color: '#fff', padding: '10px 14px', borderRadius: 8,
						textDecoration: 'none', fontWeight: 600
					}}>+ Create New Case</Link>
				</div>

				{/* Quick stats */}
				<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 16 }}>
					<div style={cardStyle}>
						<div style={{ color: '#6b7280', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>Latest Case</div>
						<div style={{ marginTop: 8, fontSize: 18, fontWeight: 600 }}>{last?.case_id || '—'}</div>
					</div>
								<div style={cardStyle}>
									<div style={{ color: '#6b7280', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>Status</div>
									<div style={{ marginTop: 8 }}>
										<span style={{
											display: 'inline-block',
											padding: '4px 10px',
											borderRadius: 999,
											fontWeight: 700,
											fontSize: 14,
											background: statusStyle.bg,
											color: statusStyle.color,
											border: `1px solid ${statusStyle.border}`,
										}}>{lastStatus}</span>
									</div>
									{(progressPercent !== null) && (
										<div style={{ marginTop: 10 }}>
											<div style={{ height: 8, background: '#f3f4f6', borderRadius: 999, overflow: 'hidden', border: '1px solid #e5e7eb' }}>
												<div style={{ width: `${progressPercent}%`, height: '100%', background: statusStyle.border }} />
											</div>
											<div style={{ marginTop: 6, color: '#6b7280', fontSize: 12 }}>{progressPercent}%</div>
										</div>
									)}
								</div>
					<div style={cardStyle}>
						<div style={{ color: '#6b7280', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>Key Points</div>
						<div style={{ marginTop: 8 }}>
							{(keyPoints.length > 0) ? (
								<ul style={{ margin: 0, paddingLeft: 18 }}>
									{keyPoints.slice(0,3).map((k, i) => <li key={i}>{k}</li>)}
								</ul>
							) : '—'}
						</div>
					</div>
				</div>

				{/* Panels */}
				<div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
					<div style={cardStyle}>
						<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
							<h3 style={{ margin: 0 }}>Latest Analysis</h3>
							{last && (
								<Link href="/result" style={{ textDecoration: 'none', fontWeight: 600 }}>View Details →</Link>
							)}
						</div>
						{!last && (
							<p style={{ color: '#6b7280' }}>No analysis yet. Create a new case to get started.</p>
						)}
						{last && (
							<div style={{ marginTop: 8 }}>
								{last?.analysis?.issue_description && (
									<>
										<div style={{ color: '#6b7280', fontSize: 12, marginTop: 8 }}>Issue Description</div>
										<p style={{ whiteSpace: 'pre-wrap', marginTop: 4 }}>{last.analysis.issue_description}</p>
									</>
								)}
								{last?.analysis?.analysis && (() => {
									// Avoid rendering raw JSON-like content. Extract leading JSON if present and render human-friendly report.
									const txt: string = last.analysis.analysis;
									const extracted = extractLeadingJson(txt);
									const parsed = extracted.parsed;
									const remainder = extracted.remainder;
									let displayText: string | null = null;
									let localKeyPoints: string[] = last?.analysis?.key_points ?? [];
									let localSteps: string[] = last?.analysis?.steps ?? [];
									if (parsed && typeof parsed === 'object') {
										displayText = remainder || parsed.analysis || parsed.summary || parsed.explanation || null;
										if (Array.isArray(parsed.key_points) && parsed.key_points.length) localKeyPoints = parsed.key_points;
										if (Array.isArray(parsed.steps) && parsed.steps.length) localSteps = parsed.steps;
									} else {
										// remove any {...} blocks to avoid showing raw JSON-looking text
										const cleaned = txt.replace(/\{[\s\S]*?\}/g, '').trim();
										displayText = cleaned || null;
									}
									return (
										<>
											{displayText && (
												<>
													<div style={{ color: '#6b7280', fontSize: 12, marginTop: 8 }}>Analysis</div>
													<p style={{ whiteSpace: 'pre-wrap', marginTop: 4 }}>{displayText}</p>
												</>
											)}
											{(localSteps.length > 0) && (
												<>
													<div style={{ color: '#6b7280', fontSize: 12, marginTop: 8 }}>Next Steps</div>
													<ol style={{ marginTop: 4, paddingLeft: 18 }}>
														{localSteps.slice(0,5).map((s, i) => <li key={i}>{s}</li>)}
													</ol>
												</>
											)}
											{(localKeyPoints.length > 0) && (
												<>
													<div style={{ color: '#6b7280', fontSize: 12, marginTop: 8 }}>Key Points</div>
													<ul style={{ marginTop: 4, paddingLeft: 18 }}>
														{localKeyPoints.slice(0,5).map((k, i) => <li key={i}>{k}</li>)}
													</ul>
												</>
											)}
										</>
									);
								})()}
							</div>
						)}
					</div>

								<div style={cardStyle}>
									<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
										<h3 style={{ marginTop: 0, marginBottom: 0 }}>Quick View</h3>
										<Link href="/upload" style={{ textDecoration: 'none', fontWeight: 600 }}>+ New</Link>
									</div>
									{history.length === 0 && (
										<p style={{ color: '#6b7280', marginTop: 8 }}>No history yet. Create a case to see it here.</p>
									)}
									{history.length > 0 && (
										<div style={{ marginTop: 8 }}>
											<ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 8 }}>
												{history.slice(0, 8).map((item, idx) => (
													<li key={idx} style={{
														border: '1px solid #e5e7eb', borderRadius: 8, padding: 10,
														display: 'flex', alignItems: 'center', justifyContent: 'space-between'
													}}>
														<div style={{ minWidth: 0 }}>
															<div style={{ fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
																{item.case_id}
															</div>
																					<div style={{ color: '#6b7280', fontSize: 12 }}>
																						{(item.status || (item.analysis ? 'Analyzed' : '—'))}{item.created_at ? ` · ${new Date(item.created_at).toLocaleString()}` : ''}
																					</div>
														</div>
														<div style={{ display: 'flex', gap: 8, marginLeft: 12 }}>
															<button onClick={() => openHistoryItem(item)} style={{
																background: '#2563eb', color: '#fff', padding: '8px 10px', borderRadius: 8,
																border: '1px solid #1d4ed8', cursor: 'pointer', fontWeight: 600
															}}>Open</button>
														</div>
													</li>
												))}
											</ul>
											<div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
												<button onClick={clearHistory} style={{
													background: '#f3f4f6', color: '#111827', padding: '8px 10px', borderRadius: 8,
													border: '1px solid #e5e7eb', cursor: 'pointer', fontWeight: 600
												}}>Clear History</button>
												<button onClick={handleClear} style={{
													background: '#f3f4f6', color: '#111827', padding: '8px 10px', borderRadius: 8,
													border: '1px solid #e5e7eb', cursor: 'pointer', fontWeight: 600
												}}>Clear Last</button>
											</div>
										</div>
									)}
								</div>
				</div>
			</div>
		</div>
	);
};

export default IndexPage;