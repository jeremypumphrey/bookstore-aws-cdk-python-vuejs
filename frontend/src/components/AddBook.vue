<template>
  <section class="card">
    <h2>Add a Book</h2>
    <form @submit.prevent="submit" novalidate>
      <div class="form-row">
        <label for="title">Title *</label>
        <input
          id="title"
          v-model.trim="form.title"
          type="text"
          placeholder="e.g. Clean Code"
          required
        />
      </div>
      <div class="form-row">
        <label for="author">Author *</label>
        <input
          id="author"
          v-model.trim="form.author"
          type="text"
          placeholder="e.g. Robert C. Martin"
          required
        />
      </div>
      <div class="form-row">
        <label for="isbn">ISBN</label>
        <input
          id="isbn"
          v-model.trim="form.isbn"
          type="text"
          placeholder="e.g. 978-0-13-235088-4"
        />
      </div>
      <div class="form-row">
        <label for="description">Description</label>
        <textarea
          id="description"
          v-model.trim="form.description"
          rows="3"
          placeholder="A brief description of the book…"
        />
      </div>

      <p v-if="error" class="msg error">{{ error }}</p>
      <p v-if="success" class="msg success">✓ Book added successfully!</p>

      <button type="submit" :disabled="loading">
        {{ loading ? "Adding…" : "Add Book" }}
      </button>
    </form>
  </section>
</template>

<script setup>
import { ref, reactive } from "vue";
import { createBook } from "../api.js";

const emit = defineEmits(["book-added"]);

const form = reactive({ title: "", author: "", isbn: "", description: "" });
const loading = ref(false);
const error = ref("");
const success = ref(false);

async function submit() {
  error.value = "";
  success.value = false;

  if (!form.title || !form.author) {
    error.value = "Title and Author are required.";
    return;
  }

  loading.value = true;
  try {
    await createBook({ ...form });
    success.value = true;
    form.title = "";
    form.author = "";
    form.isbn = "";
    form.description = "";
    emit("book-added");
  } catch (err) {
    error.value = err.message || "Failed to add book.";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem 2rem;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
}

h2 {
  margin-bottom: 1.25rem;
  font-size: 1.2rem;
  color: #2d3748;
}

form {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #4a5568;
}

input,
textarea {
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  padding: 0.55rem 0.75rem;
  font-size: 0.95rem;
  transition: border-color 0.15s;
  font-family: inherit;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #3182ce;
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.15);
}

button {
  align-self: flex-start;
  background: #2b6cb0;
  color: white;
  border: none;
  padding: 0.65rem 1.5rem;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

button:hover:not(:disabled) {
  background: #2c5282;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.msg {
  font-size: 0.9rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
}

.error {
  color: #c53030;
  background: #fff5f5;
  border: 1px solid #fed7d7;
}

.success {
  color: #276749;
  background: #f0fff4;
  border: 1px solid #c6f6d5;
}
</style>
