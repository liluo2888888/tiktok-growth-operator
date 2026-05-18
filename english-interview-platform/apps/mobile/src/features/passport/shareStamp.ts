import type { RefObject } from "react";
import { Platform, Share, type View } from "react-native";
import { captureRef } from "react-native-view-shot";

import { buildShareMessage } from "@/features/passport/stampPresentation";
import { track } from "@/services/analytics";
import type { PassportStamp } from "@/storage/passportStamps";

export type ShareChannel = "image" | "text_web" | "text_fallback";

export async function sharePassportStamp(
  stamp: PassportStamp,
  posterRef: RefObject<View>
): Promise<ShareChannel> {
  const message = buildShareMessage(stamp);
  const title = "Quest English — Passport Stamp";

  if (Platform.OS === "web") {
    await Share.share({ title, message });
    await track("passport_share", { channel: "text_web" });
    return "text_web";
  }

  try {
    const uri = await captureRef(posterRef, {
      format: "png",
      quality: 1,
      result: "tmpfile"
    });

    await Share.share({
      title,
      message,
      url: uri
    });
    await track("passport_share", { channel: "image" });
    return "image";
  } catch {
    await Share.share({ title, message });
    await track("passport_share", { channel: "text_fallback" });
    return "text_fallback";
  }
}
