// upload.tsx
// Description: Upload page with three inputs: receipt files, product images, and issue description.
// Purpose:
// - Select receipt files (multiple, images/PDF).
// - Select product images (multiple, image/*).
// - Fill in the issue description.
// - Submit to backend /cases via FormData.
// Note: Minimal, lightweight example focusing on basic functionality.

// @ts-nocheck
import React, { useRef, useState } from 'react';
import { useRouter } from 'next/router'
import { uploadCase, analyzeIssue } from '../utils/api';

const card: React.CSSProperties = {
	background: '#fff',
	border: '1px solid #e5e7eb',
	borderRadius: 12,
	padding: 20,
	boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
};

const dropzoneBase: React.CSSProperties = {
	border: '2px dashed #cbd5e1',
	borderRadius: 12,
	padding: 20,
	background: '#fafafa',
	cursor: 'pointer'
};

const primaryBtn: React.CSSProperties = {
	background: '#111827', color: '#fff', padding: '10px 16px', borderRadius: 8,
	border: '1px solid #111827', cursor: 'pointer', fontWeight: 600
};

const secondaryBtn: React.CSSProperties = {
	background: '#f3f4f6', color: '#111827', padding: '10px 16px', borderRadius: 8,
	border: '1px solid #e5e7eb', cursor: 'pointer', fontWeight: 600
};

const UploadPage: React.FC = () => {
	const [receiptFiles, setReceiptFiles] = useState<FileList | null>(null);
	const [productImages, setProductImages] = useState<FileList | null>(null);
	const [issueDescription, setIssueDescription] = useState<string>('');
	const [submitting, setSubmitting] = useState(false);
	const [message, setMessage] = useState<string>('');
	const router = useRouter();
	const receiptInputRef = useRef<HTMLInputElement>(null);
	const imageInputRef = useRef<HTMLInputElement>(null);

	const summarize = (fl: FileList | null) => {
		if (!fl || fl.length === 0) return 'No files selected';
		const names = Array.from(fl).map(f => f.name);
		if (names.length <= 2) return names.join(', ');
		return `${names.slice(0,2).join(', ')} +${names.length - 2} more`;
	};

	const onSubmit: React.FormEventHandler<HTMLFormElement> = async (e) => {
		e.preventDefault();
		setMessage('');
		setSubmitting(true);
		try {
			const fd = new FormData();
			if (receiptFiles) {
				Array.from(receiptFiles).forEach(f => fd.append('receipt_files', f));
			}
			if (productImages) {
				Array.from(productImages).forEach(f => fd.append('product_images', f));
			}
			fd.append('issue_description', issueDescription || '');

			// 1) Create the case (saves files and description)
			const created = await uploadCase(fd);
			if (!created?.case_id) {
				setMessage('Submission finished but no case_id returned');
				return;
			}
			setMessage(`Submitted successfully, case_id: ${created.case_id}. Running analysis...`);

			// 2) Call analysis directly using the same description
			const analysis = await analyzeIssue(issueDescription || '');
			// Persist result locally for the result page
			const entry = { case_id: created.case_id, analysis, created_at: new Date().toISOString(), status: 'Analyzed' };
			localStorage.setItem('lastAnalysis', JSON.stringify(entry));
			// Append to history list for Quick View
			try {
				const raw = localStorage.getItem('analysisHistory');
				const list = raw ? JSON.parse(raw) : [];
				list.unshift(entry);
				// keep only recent 50
				while (list.length > 50) list.pop();
				localStorage.setItem('analysisHistory', JSON.stringify(list));
			} catch {}
			// Navigate to result page
			router.push('/result');
		} catch (err: any) {
			setMessage(err?.message || 'Submission failed');
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<div style={{ minHeight: '100vh', background: '#f7f7f9' }}>
			<div style={{ maxWidth: 860, margin: '0 auto', padding: '24px 16px' }}>
				<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
					<div>
						<h1 style={{ margin: 0 }}>Upload Receipts and Issue Details</h1>
						<p style={{ color: '#6b7280', margin: '4px 0 0' }}>Select files and describe your issue. You can drag and drop files into the area.</p>
					</div>
				</div>

				<form onSubmit={onSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
					<div style={card}>
						<div style={{ color: '#6b7280', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>Receipt files</div>
						<div
							style={dropzoneBase}
							onClick={() => receiptInputRef.current?.click()}
							onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); }}
							onDrop={(e) => { e.preventDefault(); setReceiptFiles(e.dataTransfer.files); }}
						>
							<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
								<div>
									<div style={{ fontWeight: 600 }}>Click to choose files or drag and drop</div>
									<div style={{ color: '#6b7280', fontSize: 12 }}>Accepted: images/PDF, multiple</div>
								</div>
								<button type="button" style={secondaryBtn} onClick={(e) => { e.preventDefault(); receiptInputRef.current?.click(); }}>Browse</button>
							</div>
							<div style={{ marginTop: 8, color: '#111827' }}>{summarize(receiptFiles)}</div>
							<input
								ref={receiptInputRef}
								type="file"
								accept="image/*,application/pdf"
								multiple
								style={{ display: 'none' }}
								onChange={(e) => setReceiptFiles(e.target.files)}
							/>
						</div>
						<div style={{ marginTop: 8 }}>
							<button type="button" style={secondaryBtn} onClick={() => setReceiptFiles(null)}>Clear receipts</button>
						</div>
					</div>

					<div style={card}>
						<div style={{ color: '#6b7280', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>Product images</div>
						<div
							style={dropzoneBase}
							onClick={() => imageInputRef.current?.click()}
							onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); }}
							onDrop={(e) => { e.preventDefault(); setProductImages(e.dataTransfer.files); }}
						>
							<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
								<div>
									<div style={{ fontWeight: 600 }}>Click to choose files or drag and drop</div>
									<div style={{ color: '#6b7280', fontSize: 12 }}>Accepted: images, multiple</div>
								</div>
								<button type="button" style={secondaryBtn} onClick={(e) => { e.preventDefault(); imageInputRef.current?.click(); }}>Browse</button>
							</div>
							<div style={{ marginTop: 8, color: '#111827' }}>{summarize(productImages)}</div>
							<input
								ref={imageInputRef}
								type="file"
								accept="image/*"
								multiple
								style={{ display: 'none' }}
								onChange={(e) => setProductImages(e.target.files)}
							/>
						</div>
						<div style={{ marginTop: 8 }}>
							<button type="button" style={secondaryBtn} onClick={() => setProductImages(null)}>Clear images</button>
						</div>
					</div>

					<div style={card}>
						<div style={{ color: '#6b7280', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>Issue description</div>
						<textarea
							rows={6}
							style={{ width: '100%', marginTop: 8, border: '1px solid #e5e7eb', borderRadius: 8, padding: 12 }}
							placeholder="Briefly describe the issue, time, and your communication with the seller"
							value={issueDescription}
							onChange={(e) => setIssueDescription(e.target.value)}
						/>
						<div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
							<button type="submit" disabled={submitting} style={primaryBtn}>
								{submitting ? 'Submitting…' : 'Submit'}
							</button>
							<button type="button" style={secondaryBtn} onClick={() => { setReceiptFiles(null); setProductImages(null); setIssueDescription(''); setMessage(''); }}>Reset</button>
						</div>
						{message && (
							<p style={{ marginTop: 12 }}>{message}</p>
						)}
					</div>
				</form>
			</div>
		</div>
	);
};

export default UploadPage;