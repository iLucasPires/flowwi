export function isEmoji(value: string): boolean {
  const emojiRegex = /^(?:\p{Emoji_Presentation}|\p{Emoji}\uFE0F)$/u
  return emojiRegex.test(value)
}
