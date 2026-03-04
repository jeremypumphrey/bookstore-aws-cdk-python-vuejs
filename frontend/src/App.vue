<template>
  <div class="app">
    <header class="app-header">
      <h1>📚 Bookstore</h1>
    </header>

    <main class="app-main">
      <AddBook @book-added="onBookAdded" />
      <BookList ref="bookListRef" />
    </main>
  </div>
</template>

<script setup>
import { ref } from "vue";
import AddBook from "./components/AddBook.vue";
import BookList from "./components/BookList.vue";

const bookListRef = ref(null);

function onBookAdded() {
  bookListRef.value?.refresh();
}
</script>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
  background: #f0f4f8;
  color: #1a202c;
  min-height: 100vh;
}

.app-header {
  background: #2b6cb0;
  color: white;
  padding: 1.25rem 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.app-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.app-main {
  max-width: 860px;
  margin: 2rem auto;
  padding: 0 1rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
</style>
