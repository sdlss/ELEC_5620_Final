// result.tsx
// Result page: display structured analysis returned by the backend/AI.

// @ts-nocheck
import React, { useEffect, useState } from 'react';
import Link from 'next/link';

const ResultPage: React.FC = () => {
	const [loaded, setLoaded] = useState(false);
	const [caseId, setCaseId] = useState<string>('');
	const [model, setModel] = useState<string>('');
	const [issueDescription, setIssueDescription] = useState<string>('');
	const [analysis, setAnalysis] = useState<string>('');
	const [keyPoints, setKeyPoints] = useState<string[]>([]);
	const [steps, setSteps] = useState<string[]>([]);

	useEffect(() => {
		try {
			const raw = localStorage.getItem('lastAnalysis');
			if (!raw) {
				setLoaded(true);
				return;
			}
			const parsed = JSON.parse(raw);
			const a = parsed?.analysis;
			setCaseId(parsed?.case_id || '');
			setModel(a?.model || '');
			setIssueDescription(a?.issue_description || '');
			setAnalysis(a?.analysis || '');
			setKeyPoints(Array.isArray(a?.key_points) ? a.key_points : []);
			setSteps(Array.isArray(a?.steps) ? a.steps : []);
		} catch (e) {
			// ignore parse errors
		} finally {
			setLoaded(true);
		}
	}, []);

	if (!loaded) return <div style={{ maxWidth: 800, margin: '24px auto', padding: 16 }}>Loading…</div>;

	const hasData = !!analysis || (keyPoints?.length ?? 0) > 0 || (steps?.length ?? 0) > 0;

	return (
		<div style={{ maxWidth: 800, margin: '24px auto', padding: 16 }}>
			<h1>Analysis Result</h1>
			{!hasData && (
				<>
					<p>No analysis data found. Please go to the upload page and submit your issue.</p>
					<Link href="/upload">Go to Upload</Link>
				</>
			)}

			{hasData && (
				<>
					{caseId && <p><strong>Case ID:</strong> {caseId}</p>}
					{model && <p><strong>Model:</strong> {model}</p>}
					{issueDescription && (
						<div style={{ marginTop: 12 }}>
							<h3>Issue Description</h3>
							<p style={{ whiteSpace: 'pre-wrap' }}>{issueDescription}</p>
						</div>
					)}
					{analysis && (
						<div style={{ marginTop: 12 }}>
							<h3>Raw Analysis</h3>
							<p style={{ whiteSpace: 'pre-wrap' }}>{analysis}</p>
						</div>
					)}
					{keyPoints?.length > 0 && (
						<div style={{ marginTop: 12 }}>
							<h3>Key Points</h3>
							<ul>
								{keyPoints.map((k, i) => <li key={i}>{k}</li>)}
							</ul>
						</div>
					)}
					{steps?.length > 0 && (
						<div style={{ marginTop: 12 }}>
							<h3>Next Steps</h3>
							<ol>
								{steps.map((s, i) => <li key={i}>{s}</li>)}
							</ol>
						</div>
					)}

					<div style={{ marginTop: 24 }}>
						<Link href="/upload">Upload another</Link>
					</div>
				</>
			)}
		</div>
	);
};

export default ResultPage;