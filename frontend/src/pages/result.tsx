// result.tsx
// Result page: Refund Eligibility Report based on backend AI (classification/eligibility).

// @ts-nocheck
import React, { useEffect, useState } from 'react';
import Link from 'next/link';

const ResultPage: React.FC = () => {
	const [loaded, setLoaded] = useState(false);
	const [caseId, setCaseId] = useState<string>('');
	const [issueDescription, setIssueDescription] = useState<string>('');
	const [report, setReport] = useState<any>(null); // { classification, eligibility, final_report }
	const [finalReport, setFinalReport] = useState<any>(null);
	const [receipts, setReceipts] = useState<any[]>([]);

	useEffect(() => {
		try {
			const raw = localStorage.getItem('lastAnalysis');
			if (!raw) {
				setLoaded(true);
				return;
			}
			const parsed = JSON.parse(raw);
			// Use backend-generated case_id recorded by upload page
			setCaseId(parsed?.case_id || '');
			setIssueDescription(parsed?.analysis?.issue_description || '');
			// Prefer structured report saved by upload page; fallback to derive minimal report from analysis text
			const structured = parsed?.report || null;
			setReport(structured || null);
			setFinalReport(structured?.final_report || null);
			setReceipts(Array.isArray(parsed?.receipts) ? parsed?.receipts : []);
		} catch (e) {
			// ignore parse errors
		} finally {
			setLoaded(true);
		}
	}, []);

	if (!loaded) return <div style={{ maxWidth: 1040, margin: '24px auto', padding: 16 }}>Loading…</div>;

	const hasData = !!(report || finalReport);

	const pageBg = { minHeight: '100vh', background: '#f7f7f9' } as React.CSSProperties;
	const container = { maxWidth: 1040, margin: '0 auto', padding: '24px 16px' } as React.CSSProperties;
	const card = { background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: 16, boxShadow: '0 1px 2px rgba(0,0,0,0.05)' } as React.CSSProperties;
	const badge = (ok: boolean) => ({
		display: 'inline-block',
		padding: '4px 10px',
		borderRadius: 999,
		fontWeight: 700,
		fontSize: 14,
		background: ok ? '#d1fae5' : '#fee2e2',
		color: ok ? '#065f46' : '#991b1b',
		border: `1px solid ${ok ? '#10b981' : '#ef4444'}`,
	} as React.CSSProperties);

	const eligible = !!report?.eligibility?.eligible;

	return (
		<div style={pageBg}>
			<div style={container}>
				{/* Header */}
				<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
					<div>
						<h1 style={{ margin: 0 }}>Refund Handling Report</h1>
						<p style={{ color: '#6b7280', margin: '4px 0 0' }}>AI-generated case summary, decision and suggestions.</p>
					</div>
					<div />
				</div>
			{!hasData && (
				<>
					<p>No report data found. Please go to the upload page and submit your receipt and issue.</p>
					<Link href="/upload">Go to Upload</Link>
				</>
			)}

			{hasData && (
				<>
					{/* Summary strip */}
					<div style={{ ...card, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
						<div style={{ minWidth: 0 }}>
							<div style={{ color: '#6b7280', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>Case</div>
							<div style={{ fontSize: 18, fontWeight: 700, marginTop: 4, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{caseId || '—'}</div>
						</div>
						<div>
							<span style={badge(eligible)}>{eligible ? 'Eligible for refund' : 'Not eligible'}</span>
						</div>
					</div>

					{/* Decision only (remove issue description panel) */}
					<div style={{ ...card, marginTop: 16 }}>
						<h3 style={{ marginTop: 0 }}>Decision</h3>
						{report?.eligibility ? (
							<div>
								<div><strong>Status:</strong> {report.eligibility.eligible ? 'Eligible for refund' : 'Not eligible'}</div>
								{report.eligibility.model ? (
									<div style={{ marginTop: 6 }}><strong>Model:</strong> {report.eligibility.model}</div>
								) : null}
							</div>
						) : (
							<p style={{ color: '#6b7280' }}>No eligibility data.</p>
						)}
					</div>
					{/* Swap order: show Receipt Summary (OCR) first, then Reason (AI final report) */}
					{/* Receipt Summary from OCR parsed results */}
					<div style={{ ...card, marginTop: 16 }}>
						<h3 style={{ marginTop: 0 }}>Receipt Summary</h3>
						{Array.isArray(receipts) && receipts.length > 0 && receipts[0]?.pages?.length > 0 ? (
							(() => {
								const firstPage = receipts[0].pages[0];
								const parsed = firstPage?.parsed || {};
								const items = Array.isArray(parsed.item_list) ? parsed.item_list : [];
								return (
									<div>
										<ul style={{ marginTop: 8 }}>
											{parsed.seller_name ? <li><strong>Seller:</strong> {parsed.seller_name}</li> : null}
											{parsed.receipt_id ? <li><strong>Receipt ID:</strong> {parsed.receipt_id}</li> : null}
											{parsed.purchase_date ? <li><strong>Date:</strong> {parsed.purchase_date}</li> : null}
											{parsed.payment_method ? <li><strong>Payment:</strong> {parsed.payment_method}</li> : null}
											{parsed.purchase_total?.value != null ? <li><strong>Total:</strong> {parsed.purchase_total.currency || 'USD'} {parsed.purchase_total.value}</li> : null}
										</ul>
										{items.length > 0 && (
											<div style={{ marginTop: 8 }}>
												<h4 style={{ margin: '8px 0' }}>Items</h4>
												<ul>
													{items.map((it: any, i: number) => (
														<li key={i}>{it.description} {typeof it.price === 'number' ? `- $${it.price.toFixed(2)}` : ''}</li>
													))}
												</ul>
											</div>
										)}
									</div>
								);
							})()
						) : (
							<p style={{ color: '#6b7280' }}>No OCR results available.</p>
						)}
					</div>

					{/* Decision */}
					{/* Decision Reason */}

					{/* Reason: now show AI Agent final report */}
					<div style={{ ...card, marginTop: 16 }}>
						<h3 style={{ marginTop: 0 }}>Reason</h3>
										{(() => {
											// Normalize final report display: prefer human-readable fields and hide raw JSON
											if (!finalReport) return <p style={{ color: '#6b7280' }}>No AI report available.</p>;
											// Determine if finalReport is a string containing JSON
											let parsed: any = null;
											if (typeof finalReport === 'string') {
												try {
													parsed = JSON.parse(finalReport);
												} catch (e) {
													// plain text
													return <p style={{ whiteSpace: 'pre-wrap', marginTop: 8 }}>{finalReport}</p>;
												}
											} else if (typeof finalReport === 'object') {
												parsed = finalReport;
											}
											// If parsed is object, show human-friendly fields only (no raw JSON)
											if (parsed && typeof parsed === 'object') {
												// Prefer an explicit analysis/summary field if present
												const analysisField = parsed.analysis || parsed.summary || parsed.explanation || null;
												return (
													<>
														{analysisField ? <p style={{ whiteSpace: 'pre-wrap', marginTop: 8 }}>{analysisField}</p> : <p style={{ color: '#6b7280' }}>AI returned structured analysis. See key points and recommended steps below.</p>}
														{Array.isArray(parsed.key_points) && parsed.key_points.length > 0 && (
															<>
																<h4>Key Points</h4>
																<ul style={{ marginTop: 6 }}>
																	{parsed.key_points.map((k: string, i: number) => <li key={i}>{k}</li>)}
																</ul>
															</>
														)}
														{Array.isArray(parsed.steps) && parsed.steps.length > 0 && (
															<>
																<h4>Recommended Steps</h4>
																<ol style={{ marginTop: 6 }}>
																	{parsed.steps.map((s: string, i: number) => <li key={i}>{s}</li>)}
																</ol>
															</>
														)}
													</>
												);
											}
											// Fallback: if we couldn't parse and didn't return earlier, show minimal message
											return <p style={{ color: '#6b7280' }}>AI returned an unrecognized format.</p>;
										})()}
					</div>

					{/* Classification (optional, if backend provided) */}
					{report?.classification && (
						<div style={{ ...card, marginTop: 16 }}>
							<h3 style={{ marginTop: 0 }}>Issue Classification</h3>
							{/* Render classification in a human-friendly form instead of raw JSON */}
							<div style={{ marginTop: 8 }}>
								<div><strong>Category:</strong> {report.classification.category ?? '—'}</div>
								{report.classification.reason ? <div style={{ marginTop: 6 }}><strong>Reason:</strong> {report.classification.reason}</div> : null}
								{typeof report.classification.requires_manual_review !== 'undefined' && (
									<div style={{ marginTop: 6 }}><strong>Requires manual review:</strong> {report.classification.requires_manual_review ? 'Yes' : 'No'}</div>
								)}
								{typeof report.classification.confidence_score !== 'undefined' && (
									<div style={{ marginTop: 6 }}><strong>Confidence:</strong> {Number(report.classification.confidence_score).toFixed(2)}</div>
								)}
								{Array.isArray(report.classification.keywords) && report.classification.keywords.length > 0 && (
									<div style={{ marginTop: 6 }}>
										<strong>Keywords:</strong>
										<ul style={{ marginTop: 6 }}>
											{report.classification.keywords.map((k: string, i: number) => <li key={i}>{k}</li>)}
										</ul>
									</div>
								)}
								{report.classification.model_used ? <div style={{ marginTop: 6 }}><strong>Model:</strong> {report.classification.model_used}</div> : null}
							</div>
						</div>
					)}

					{/* keep classification card if present */}

					<div style={{ display: 'flex', gap: 8, marginTop: 20 }}>
						<Link href="/" style={{
							background: '#f3f4f6', color: '#111827', padding: '10px 12px', borderRadius: 8,
							textDecoration: 'none', border: '1px solid #e5e7eb', fontWeight: 600
						}}>← Back to Dashboard</Link>
						<Link href="/upload" style={{
							background: '#111827', color: '#fff', padding: '10px 12px', borderRadius: 8,
							textDecoration: 'none', border: '1px solid #111827', fontWeight: 600
						}}>+ New Upload</Link>
					</div>
				</>
			)}
			</div>
		</div>
	);
};

export default ResultPage;