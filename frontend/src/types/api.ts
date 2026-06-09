// API wrapper types + auth request/response types
// Derived from: backend/app/schemas/user.py

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  code?: string;
}

/** Backend: LoginRequest – POST /auth/login */
export interface LoginRequest {
  username: string;
  password: string;
}

/** Backend: TokenResponse – POST /auth/login response */
export interface TokenResponse {
  access_token: string;
  refresh_token: string | null;
  token_type: string;
}

/** Backend: RegisterRequest – POST /auth/register */
export interface RegisterRequest {
  username: string;
  email?: string | null;
  password: string;
  display_name?: string | null;
}

/** Backend: RefreshTokenRequest – POST /auth/refresh */
export interface RefreshTokenRequest {
  refresh_token: string;
}

/** Backward-compatible alias */
export type LoginResponse = TokenResponse;
