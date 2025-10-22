// index.tsx
// User Dashboard: show last analysis summary and quick actions.

// @ts-nocheck
import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

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

	useEffect(() => {
		try {
			const raw = localStorage.getItem('lastAnalysis');
			if (raw) {
				setLast(JSON.parse(raw));
			}
				const hraw = localStorage.getItem('analysisHistory');
				if (hraw) {
					const arr = JSON.parse(hraw);
					if (Array.isArray(arr)) setHistory(arr);
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
		const lastStatus = last?.status || (last?.analysis ? 'Analyzed' : '—');

		const openHistoryItem = (item: HistoryItem) => {
			try {
				localStorage.setItem('lastAnalysis', JSON.stringify(item));
			} catch {}
			router.push('/result');
		};

		const clearHistory = () => {
			localStorage.removeItem('analysisHistory');
			setHistory([]);
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
									<div style={{ marginTop: 8, fontSize: 18, fontWeight: 600 }}>{lastStatus}</div>
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
								{last?.analysis?.analysis && (
									<>
										<div style={{ color: '#6b7280', fontSize: 12, marginTop: 8 }}>Raw Analysis</div>
										<p style={{ whiteSpace: 'pre-wrap', marginTop: 4 }}>{last.analysis.analysis}</p>
									</>
								)}
								{(steps.length > 0) && (
									<>
										<div style={{ color: '#6b7280', fontSize: 12, marginTop: 8 }}>Next Steps</div>
										<ol style={{ marginTop: 4, paddingLeft: 18 }}>
											{steps.slice(0,5).map((s, i) => <li key={i}>{s}</li>)}
										</ol>
									</>
								)}
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