export interface Customer {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  company_name?: string;
  verification_status: string;
  email_verified: boolean;
  profile_picture_url?: string;
  preferred_auth_method: string;
  created_at: string;
  updated_at: string;
}

export interface CustomerRegistration {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  company_name?: string;
}

export interface CustomerLogin {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  customer: Customer;
}

export interface SSOProvider {
  name: string;
  provider: string;
  icon: string;
  color: string;
}

export interface SSOInitiateResponse {
  auth_url: string;
  state: string;
  provider: string;
}

export interface LinkedSSOAccount {
  provider: string;
  provider_email: string;
  provider_name: string;
  is_primary: boolean;
  linked_at: string;
  last_login?: string;
}