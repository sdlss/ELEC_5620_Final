// @ts-nocheck
// utils/api.ts
// 说明：封装与后端 FastAPI 的交互方法（最小可用实现）。
// 注意：实际项目可将 baseURL 抽取到环境变量，并统一处理鉴权/错误。

export interface CreateCaseResponse {
	case_id: string;
	status: string;
}

const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function uploadCase(formData: FormData): Promise<CreateCaseResponse> {
	const res = await fetch(`${baseURL}/cases`, {
		method: 'POST',
		body: formData,
	});
	if (!res.ok) {
		const text = await res.text().catch(() => '');
		throw new Error(`后端返回错误：${res.status} ${text}`);
	}
	return res.json();
}
