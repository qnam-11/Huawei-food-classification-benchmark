import type { ModelsResponse, PredictResponse } from "@/types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  code: string;

  constructor(code: string) {
    super(code);
    this.code = code;
  }
}

async function readErrorCode(response: Response): Promise<string> {
  try {
    const body = await response.json();
    return body?.error?.code ?? "inference_failed";
  } catch {
    return "inference_failed";
  }
}

export async function fetchModels(signal?: AbortSignal): Promise<ModelsResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/models`, { signal });
  } catch {
    throw new ApiError("network_error");
  }
  if (!response.ok) {
    throw new ApiError(await readErrorCode(response));
  }
  return response.json();
}

export async function predict(
  file: File,
  modelId: string,
  signal?: AbortSignal,
): Promise<PredictResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("model_id", modelId);

  let response: Response;
  const timeout = AbortSignal.timeout(60_000);
  try {
    response = await fetch(`${API_URL}/api/predict`, {
      method: "POST",
      body: form,
      signal: signal ? AbortSignal.any([signal, timeout]) : timeout,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiError("network_error");
  }
  if (!response.ok) {
    throw new ApiError(await readErrorCode(response));
  }
  return response.json();
}
