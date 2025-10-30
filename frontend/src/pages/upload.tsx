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
import { analyzeReceipt } from '../utils/api';

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
	const [receiptId, setReceiptId] = useState<string>('');
	const [productImages, setProductImages] = useState<FileList | null>(null);
	const [receiptFiles, setReceiptFiles] = useState<FileList | null>(null);
    const [issueDescription, setIssueDescription] = useState<string>('');
    const [submitting, setSubmitting] = useState(false);
    const [message, setMessage] = useState<string>('');
    const router = useRouter();
    const imageInputRef = useRef<HTMLInputElement>(null);
	const receiptInputRef = useRef<HTMLInputElement>(null);
	const [showReceiptDialog, setShowReceiptDialog] = useState(false);

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
			// Build FormData for new OCR + eligibility endpoint
			const fd = new FormData();
			if (receiptFiles) {
				Array.from(receiptFiles).forEach(f => fd.append('receipt_files', f));
			}
			fd.append('issue_description', issueDescription || '');
			// Pass user-provided case id to backend
			fd.append('case_id', receiptId || '');

			const resp = await analyzeReceipt(fd);
			const eligible = resp?.eligibility?.eligible;
			const reason = resp?.eligibility?.reason || '';
			const model = resp?.eligibility?.model || '';
			const summary = resp?.eligibility?.summary || {};
			const caseIdFromServer = resp?.case_id || '';

			// Adapt backend response for result page: prefer final_report for main content
			const analysisObj: any = resp?.final_report || {
				model,
				issue_description: issueDescription,
				analysis: `Eligible: ${eligible ? 'Yes' : 'No'}\nReason: ${reason}\nItem: ${summary?.item ?? ''}\nPrice: ${summary?.price ? (summary?.price.currency + ' ' + summary?.price.value) : ''}\nDate: ${summary?.date?.raw ?? ''}`,
				key_points: reason ? [reason] : [],
				steps: [],
			};

			const entry: any = {
				case_id: caseIdFromServer || receiptId || '',
				created_at: new Date().toISOString(),
				status: 'analyzed',
				progress_percent: 100,
				analysis: analysisObj,
				report: {
					classification: resp?.classification || resp?.eligibility?.classification || null,
					eligibility: resp?.eligibility || null,
					final_report: resp?.final_report || null,
				},
				receipts: resp?.receipts || [],
			};
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
		<>
		<div style={{ minHeight: '100vh', background: '#f7f7f9' }}>
			<div style={{ maxWidth: 860, margin: '0 auto', padding: '24px 16px' }}>
				<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
					<div>
						<h1 style={{ margin: 0 }}>Upload Receipts and Issue Details</h1>
						<p style={{ color: '#6b7280', margin: '4px 0 0' }}>Select files and describe your issue. You can drag and drop files into the area.</p>
					</div>
				</div>

				<form onSubmit={onSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
					{/* Receipt files selector (PDF/PNG/JPEG) */}
					<div style={card}>
						<div style={{ color: '#6b7280', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>Receipt files</div>
						<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, marginTop: 8 }}>
							<div>
								<div style={{ fontWeight: 600 }}>PDF, PNG, JPEG supported</div>
								<div style={{ color: '#6b7280', fontSize: 12 }}>Click to open dialog and choose files</div>
							</div>
							<div style={{ display: 'flex', gap: 8 }}>
								<button type="button" style={secondaryBtn} onClick={() => setShowReceiptDialog(true)}>Upload receipt image</button>
								<button type="button" style={secondaryBtn} onClick={() => setReceiptFiles(null)}>Clear</button>
							</div>
						</div>
						<div style={{ marginTop: 8, color: '#111827' }}>
							{summarize(receiptFiles)}
						</div>
					</div>

					<div style={card}>
						<div style={{ color: '#6b7280', fontSize: 12, textTransform: 'uppercase', letterSpacing: 0.5 }}>Case ID</div>
						<input
							type="text"
							value={receiptId}
							onChange={(e) => setReceiptId(e.target.value)}
							placeholder="e.g., CASE-20251024-0001"
							style={{ width: '100%', marginTop: 8, border: '1px solid #e5e7eb', borderRadius: 8, padding: 12 }}
						/>
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
							<button type="button" style={secondaryBtn} onClick={() => { setReceiptId(''); setProductImages(null); setIssueDescription(''); setMessage(''); }}>Reset</button>
						</div>
						{message && (
							<p style={{ marginTop: 12 }}>{message}</p>
						)}
					</div>
				</form>
			</div>
		</div>

		{/* Modal dialog for selecting receipt files */}
		{showReceiptDialog && (
			<div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }}>
				<div style={{ width: 520, background: '#fff', borderRadius: 12, padding: 16, boxShadow: '0 10px 30px rgba(0,0,0,0.2)' }}>
					<h3 style={{ marginTop: 0, marginBottom: 8 }}>Upload receipt image</h3>
					<p style={{ color: '#6b7280', marginTop: 0 }}>Supported formats: PDF, PNG, JPEG. You can select multiple files.</p>
					<input
						ref={receiptInputRef}
						type="file"
						accept=".pdf,application/pdf,image/png,image/jpeg,.png,.jpg,.jpeg"
						multiple
						onChange={(e) => setReceiptFiles(e.target.files)}
					/>
					<div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 16 }}>
						<button type="button" style={secondaryBtn} onClick={() => setShowReceiptDialog(false)}>Done</button>
					</div>
				</div>
			</div>
		)}
	</>
	);
};

export default UploadPage;