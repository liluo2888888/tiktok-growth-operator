export type AsrResult = {
  transcript: string;
  confidence?: number;
  durationMs: number;
};

export type AsrErrorCode =
  | "network"
  | "timeout"
  | "empty_audio"
  | "provider_error"
  | "quota_exceeded"
  | "missing_api_key";

export class AsrError extends Error {
  code: AsrErrorCode;

  constructor(code: AsrErrorCode, message: string) {
    super(message);
    this.code = code;
  }
}

export interface AsrProvider {
  transcribe(localUri: string, durationMs: number): Promise<AsrResult>;
}
