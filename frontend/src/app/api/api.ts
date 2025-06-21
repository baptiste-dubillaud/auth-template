const getBackendUrl = (): string => {
  // Server side only
  if (typeof window === 'undefined') {
    return process.env.BACKEND_URL;
  }
  
  throw new Error('Backend URL should not be accessed from client side');
};

export const BACKEND_URL = getBackendUrl();


/**
 * Makes an HTTP request to the backend API with automatic JSON handling and error processing.
 * 
 * @param endpoint - The API endpoint path to append to the backend URL
 * @param options - Optional fetch configuration options (headers, method, body, etc.)
 * @returns A promise that resolves to the parsed JSON response
 * @throws {Error} Throws an error if the HTTP response is not ok (status >= 400)
 * 
 * @example
 * ```typescript
 * // GET request
 * const data = await backendRequest('/users');
 * 
 * // POST request with body
 * const result = await backendRequest('/users', {
 *   method: 'POST',
 *   body: JSON.stringify({ name: 'John' })
 * });
 * ```
 */
export async function backendRequest(endpoint: string, options: RequestInit = {}) {
  const url = `${BACKEND_URL}${endpoint}`;
  
  console.log(`Making request to: ${url}`);
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error('Backend request failed:', errorText);
    throw new Error(`Backend request failed: ${response.status}`);
  }

  return response.json();
}