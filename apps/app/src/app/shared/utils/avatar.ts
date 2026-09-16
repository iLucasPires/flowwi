import { Style, Avatar } from "@dicebear/core";
import lorelei from "@dicebear/styles/lorelei.json" with { type: "json" };

export function getAvatar(seed: string = "default") {
  const style = new Style(lorelei);

  const avatar = new Avatar(style, {
    seed: seed,
    size: 64,
  });

  return avatar.toDataUri();
}
