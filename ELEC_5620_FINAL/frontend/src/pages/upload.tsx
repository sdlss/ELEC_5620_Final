// upload.tsx
// 说明：上传页面，包含收据文件、商品图片与问题描述三个输入项。
// 作用：
// - 选择收据（可多文件，图片/PDF）。
// - 选择商品图片（可多文件，image/*）。
// - 填写问题描述。
// - 通过 FormData 提交到后端 /cases 接口。
// 注意：为保持轻量，本示例仅包含最小可运行的前端逻辑骨架。

// @ts-nocheck
import React, { useState } from 'react';
// 提示：实际项目建议用路由跳转至结果页，这里仅演示提交与基本反馈
// import { useRouter } from 'next/router'
import { uploadCase } from '../../utils/api';

const UploadPage: React.FC = () => {
	const [receiptFiles, setReceiptFiles] = useState<FileList | null>(null);
	const [productImages, setProductImages] = useState<FileList | null>(null);
	const [issueDescription, setIssueDescription] = useState<string>('');
	const [submitting, setSubmitting] = useState(false);
	const [message, setMessage] = useState<string>('');

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

			const res = await uploadCase(fd);
			if (res?.case_id) {
				setMessage(`提交成功，case_id: ${res.case_id}`);
				// TODO: 可跳转到 /result?case_id=xxx
			} else {
				setMessage('提交完成，但未返回 case_id');
			}
		} catch (err: any) {
			setMessage(err?.message || '提交失败');
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<div style={{ maxWidth: 720, margin: '24px auto', padding: 16 }}>
			<h1>上传收据与问题信息</h1>
			<form onSubmit={onSubmit}>
				<div style={{ marginBottom: 12 }}>
					<label>收据文件（可多选，图片/PDF）：</label><br />
					<input
						type="file"
						accept="image/*,application/pdf"
						multiple
						onChange={(e) => setReceiptFiles(e.target.files)}
					/>
				</div>
				<div style={{ marginBottom: 12 }}>
					<label>商品图片（可多选，仅图片）：</label><br />
					<input
						type="file"
						accept="image/*"
						multiple
						onChange={(e) => setProductImages(e.target.files)}
					/>
				</div>
				<div style={{ marginBottom: 12 }}>
					<label>问题描述：</label><br />
					<textarea
						rows={6}
						style={{ width: '100%' }}
						placeholder="请简要描述遇到的问题、时间、与商家沟通情况等"
						value={issueDescription}
						onChange={(e) => setIssueDescription(e.target.value)}
					/>
				</div>
				<button type="submit" disabled={submitting}>
					{submitting ? '提交中…' : '提交'}
				</button>
			</form>
			{message && (
				<p style={{ marginTop: 12 }}>{message}</p>
			)}
		</div>
	);
};

export default UploadPage;