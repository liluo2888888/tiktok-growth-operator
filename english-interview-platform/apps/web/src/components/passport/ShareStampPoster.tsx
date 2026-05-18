import {
  formatStampDate,
  missionStampEmoji,
  readinessTier,
  SHARE_POSTER_SIZE
} from "@/lib/stampPresentation";
import type { PassportStamp } from "@/lib/storage";

type Props = {
  stamp: PassportStamp;
};

/** Off-screen poster DOM captured to PNG for sharing (G-04). */
export function ShareStampPoster({ stamp }: Props) {
  return (
    <article
      className="share-stamp-poster"
      style={{ width: SHARE_POSTER_SIZE, height: SHARE_POSTER_SIZE }}
      aria-hidden
    >
      <p className="share-stamp-poster-brand">Quest English</p>
      <p className="share-stamp-poster-sub">Interview Quest Pack</p>
      <p className="share-stamp-poster-emoji">{missionStampEmoji(stamp.missionId)}</p>
      <h2 className="share-stamp-poster-mission">{stamp.missionLabel}</h2>
      <p className="share-stamp-poster-role">{stamp.roleLabel}</p>
      <div className="share-stamp-poster-score">
        <span className="share-stamp-poster-score-value">{stamp.readiness}</span>
        <span className="share-stamp-poster-score-label">就绪度</span>
      </div>
      <p className="share-stamp-poster-tier">{readinessTier(stamp.readiness)}</p>
      <p className="share-stamp-poster-earned">获得于 {formatStampDate(stamp.earnedAt)}</p>
    </article>
  );
}
