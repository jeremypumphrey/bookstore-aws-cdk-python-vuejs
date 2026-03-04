<template>
  <section class="card">
    <div class="list-header">
      <h2>Books</h2>
      <div class="search-bar">
        <input
          v-model.trim="query"
          type="search"
          placeholder="Search by title, author or ISBN…"
          @input="onSearchInput"
        />
      </div>
    </div>

    <p v-if="loading" class="state-msg">Loading…</p>
    <p v-else-if="error" class="state-msg error">{{ error }}</p>
    <p v-else-if="books.length === 0" class="state-msg muted">
      {{ query ? "No books match your search." : "No books yet. Add one above!" }}
    </p>

    <ul v-else class="book-list">
      <li v-for="book in books" :key="book.bookId" class="book-item">
        <div class="book-info">
          <strong class="book-title">{{ book.title }}</strong>
          <span class="book-author">by {{ book.author }}</span>
          <span v-if="book.isbn" class="book-isbn">ISBN: {{ book.isbn }}</span>
          <p v-if="book.description" class="book-desc">{{ book.description }}</p>
        </div>
        <button
          class="delete-btn"
          :disabled="deleting === book.bookId"
          @click="remove(book.bookId)"
          title="Delete book"
        >
          {{ deleting === book.bookId ? "…" : "🗑" }}
        </button>
      </li>
    </ul>

    <p v-if="!loading && books.length > 0" class="count">
      {{ books.length }} book{{ books.length !== 1 ? "s" : "" }}
    </p>
  </section>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { searchBooks, deleteBook } from "../api.js";

const books = ref([]);
const query = ref("");
const loading = ref(false);
const error = ref("");
const deleting = ref(null);

let debounceTimer = null;

async function load(q = "") {
  loading.value = true;
  error.value = "";
  try {
    const data = await searchBooks(q);
    books.value = data.books || [];
  } catch (err) {
    error.value = err.message || "Failed to load books.";
  } finally {
    loading.value = false;
  }
}

function onSearchInput() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => load(query.value), 300);
}

async function remove(bookId) {
  if (!confirm("Delete this book?")) return;
  deleting.value = bookId;
  try {
    await deleteBook(bookId);
    books.value = books.value.filter((b) => b.bookId !== bookId);
  } catch (err) {
    error.value = err.message || "Failed to delete book.";
  } finally {
    deleting.value = null;
  }
}

/** Called by parent when a new book is added. */
function refresh() {
  load(query.value);
}

defineExpose({ refresh });

onMounted(() => load());
</script>

<style scoped>
.card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem 2rem;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

h2 {
  font-size: 1.2rem;
  color: #2d3748;
}

.search-bar input {
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  font-size: 0.9rem;
  width: 260px;
  font-family: inherit;
}

.search-bar input:focus {
  outline: none;
  border-color: #3182ce;
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.15);
}

.book-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.book-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 1.25rem;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  gap: 1rem;
}

.book-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.book-title {
  font-size: 1rem;
  color: #1a202c;
}

.book-author {
  font-size: 0.875rem;
  color: #4a5568;
}

.book-isbn {
  font-size: 0.8rem;
  color: #718096;
}

.book-desc {
  font-size: 0.85rem;
  color: #4a5568;
  margin-top: 0.25rem;
  max-width: 560px;
}

.delete-btn {
  background: none;
  border: 1px solid #fed7d7;
  color: #c53030;
  border-radius: 6px;
  padding: 0.3rem 0.55rem;
  cursor: pointer;
  font-size: 1rem;
  flex-shrink: 0;
  transition: background 0.15s;
}

.delete-btn:hover:not(:disabled) {
  background: #fff5f5;
}

.delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.state-msg {
  font-size: 0.95rem;
  padding: 1rem 0;
}

.muted {
  color: #718096;
}

.error {
  color: #c53030;
}

.count {
  margin-top: 0.75rem;
  font-size: 0.8rem;
  color: #718096;
  text-align: right;
}
</style>
