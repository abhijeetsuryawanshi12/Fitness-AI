export type Token = {
  access_token: string
  token_type: string
}

const TOKEN_KEY = 'fitness_ai_token'

export function setToken(token: Token) {
  localStorage.setItem(TOKEN_KEY, JSON.stringify(token))
}

export function getToken(): Token | null {
  const raw = localStorage.getItem(TOKEN_KEY)
  return raw ? JSON.parse(raw) as Token : null
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export function isAuthenticated(): boolean {
  return !!getToken()?.access_token
} 