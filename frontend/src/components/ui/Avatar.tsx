
import { useState } from "react";
import "./Avatar.css";

type AvatarProps = {
  name: string;
  src?: string;
};

export function Avatar({ name, src }: AvatarProps) {
  const [failedSrc, setFailedSrc] = useState<string | null>(null);

  const initials = name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((word) => word.charAt(0))
    .join("")
    .toUpperCase();

  const showImage = Boolean(src && failedSrc !== src);

  return (
    <div
      className="ui-avatar"
      role="img"
      aria-label={name || "User avatar"}
    >
      {showImage ? (
        <img
          src={src}
          alt=""
          className="ui-avatar-image"
          onError={() => setFailedSrc(src ?? null)}
        />
      ) : (
        initials || "?"
      )}
    </div>
  );
}
