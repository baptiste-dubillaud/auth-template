const apiBaseUrl = process?.env?.NEXT_PUBLIC_BACKEND_URL;

export function resolveBackendUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;

  if (!apiBaseUrl) {
    return normalizedPath;
  }

  console.log('Resolved backend URL:', `${apiBaseUrl}${normalizedPath}`);

  return `${apiBaseUrl}${normalizedPath}`;
}

export function getBackendBaseUrl(): string | null {
  return apiBaseUrl;
}
