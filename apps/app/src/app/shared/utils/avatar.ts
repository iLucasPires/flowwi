import { Style, Avatar } from '@dicebear/core'
import initials from '@dicebear/styles/initials.json' with { type: 'json' }

export function getAvatar(seed: string = 'default') {
  const style = new Style(initials)

  const avatar = new Avatar(style, {
    seed: seed,
    size: 64,
  })

  return avatar.toDataUri()
}
