const AUTH_PREFIX = '/account/'

export const NO_WORKPLACE_PAGES = [AUTH_PREFIX, '/setup/', '/settings/']

export function isPublicPage(path: string) {
  return path.startsWith('/public/')
}

export function isAuthPage(path: string) {
  return path.startsWith(AUTH_PREFIX)
}

export function isNoWorkplacePage(path: string) {
  return NO_WORKPLACE_PAGES.some((prefix) => path.startsWith(prefix))
}
