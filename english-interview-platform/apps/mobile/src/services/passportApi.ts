import { apiBaseUrl } from "@/services/api";
import { getDeviceId } from "@/storage/deviceId";
import type { PassportStamp } from "@/storage/passportStamps";

type StampDto = {
  id: string;
  sessionId: string;
  missionId: string;
  missionLabel: string;
  roleId: string;
  roleLabel: string;
  readiness: number;
  scores: PassportStamp["scores"];
  earnedAt: string;
  isNew?: boolean;
};

function mapStamp(dto: StampDto): PassportStamp {
  return {
    id: dto.id,
    sessionId: dto.sessionId,
    missionId: dto.missionId,
    missionLabel: dto.missionLabel,
    roleId: dto.roleId,
    roleLabel: dto.roleLabel,
    readiness: dto.readiness,
    scores: dto.scores,
    earnedAt: dto.earnedAt
  };
}

async function apiHeaders(): Promise<HeadersInit> {
  return {
    "Content-Type": "application/json",
    "X-Device-Id": await getDeviceId()
  };
}

export async function fetchPassportStampsFromApi(): Promise<PassportStamp[] | null> {
  try {
    const response = await fetch(`${apiBaseUrl}/v1/mobile/passport/stamps`, {
      headers: await apiHeaders()
    });
    if (!response.ok) {
      return null;
    }

    const payload = (await response.json()) as { stamps: StampDto[] };
    return (payload.stamps ?? []).map(mapStamp);
  } catch {
    return null;
  }
}

export async function issuePassportStampOnApi(input: {
  sessionId: string;
  missionLabel: string;
  roleLabel: string;
}): Promise<{ stamp: PassportStamp; isNew: boolean } | null> {
  try {
    const response = await fetch(`${apiBaseUrl}/v1/mobile/passport/stamps`, {
      method: "POST",
      headers: await apiHeaders(),
      body: JSON.stringify(input)
    });
    if (!response.ok) {
      return null;
    }

    const dto = (await response.json()) as StampDto;
    return { stamp: mapStamp(dto), isNew: Boolean(dto.isNew) };
  } catch {
    return null;
  }
}
