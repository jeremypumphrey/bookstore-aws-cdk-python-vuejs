/**
 * api.js – thin wrapper around the Bookstore REST API.
 *
 * The API base URL is injected at build time via the VITE_API_URL
 * environment variable.  During local development you can create a
 * .env.local file with:
 *
 *   VITE_API_URL=https://<your-api-id>.execute-api.<region>.amazonaws.com/prod
 */

const BASE_URL = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }

  return data;
}

/** Create a new book. */
export function createBook(book) {
  return request("/books", {
    method: "POST",
    body: JSON.stringify(book),
  });
}

/**
 * Search / list books.
 * @param {string} [query] – optional free-text search term
 */
export function searchBooks(query = "") {
  const qs = query ? `?q=${encodeURIComponent(query)}` : "";
  return request(`/books${qs}`);
}

/** Delete a book by its ID. */
export function deleteBook(bookId) {
  return request(`/books/${encodeURIComponent(bookId)}`, {
    method: "DELETE",
  });
}
