import { createRoot } from "react-dom/client";
import { toPng } from "html-to-image";

import { ShareStampPoster } from "@/components/passport/ShareStampPoster";
import { SHARE_POSTER_SIZE, stampPosterFilename } from "@/lib/stampPresentation";
import type { PassportStamp } from "@/lib/storage";

export async function renderStampPosterPng(stamp: PassportStamp): Promise<{
  blob: Blob;
  filename: string;
}> {
  const host = document.createElement("div");
  host.setAttribute("aria-hidden", "true");
  host.style.cssText =
    "position:fixed;left:-10000px;top:0;z-index:-1;pointer-events:none;opacity:1;";
  document.body.appendChild(host);

  const root = createRoot(host);
  root.render(<ShareStampPoster stamp={stamp} />);

  await document.fonts.ready;
  await new Promise<void>((resolve) => {
    requestAnimationFrame(() => requestAnimationFrame(() => resolve()));
  });

  const poster = host.querySelector(".share-stamp-poster");
  if (!poster || !(poster instanceof HTMLElement)) {
    root.unmount();
    host.remove();
    throw new Error("无法生成分享海报");
  }

  try {
    const dataUrl = await toPng(poster, {
      cacheBust: true,
      pixelRatio: 2,
      width: SHARE_POSTER_SIZE,
      height: SHARE_POSTER_SIZE
    });
    const response = await fetch(dataUrl);
    const blob = await response.blob();
    return { blob, filename: stampPosterFilename(stamp) };
  } finally {
    root.unmount();
    host.remove();
  }
}
