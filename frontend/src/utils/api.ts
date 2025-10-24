// @ts-nocheck
// utils/api.ts
// Purpose: Minimal wrapper for talking to the FastAPI backend.
// Note: In real projects, move baseURL to env and centralize auth/error handling.

export interface CreateCaseResponse {
	case_id: string;
	status: string;
	timestamps?: Record<string, string>;
	progress_percent?: number;
}

export interface AnalyzeResponse {
	model: string;
	issue_description: string;
	analysis: string;
	key_points?: string[];
	steps?: string[];
	// optional status fields from backend
	status?: string;
	timestamps?: Record<string, string>;
	progress_percent?: number;
}


const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function uploadCase(formData: FormData): Promise<CreateCaseResponse> {
	const res = await fetch(`${baseURL}/cases`, {
		method: 'POST',
		body: formData,
	});
	if (!res.ok) {
		const text = await res.text().catch(() => '');
		throw new Error(`Backend error: ${res.status} ${text}`);
	}
	return res.json();
}

export async function analyzeIssue(issue_description: string, case_id?: string): Promise<AnalyzeResponse> {
	const form = new FormData();
	form.append('issue_description', issue_description || '');
	if (case_id) form.append('case_id', case_id);
	const res = await fetch(`${baseURL}/analyze`, {
		method: 'POST',
		body: form,
	});
	if (!res.ok) {
		const text = await res.text().catch(() => '');
		throw new Error(`Backend error: ${res.status} ${text}`);
	}
	return res.json();
}

// Note: healthCheck removed per request
