// 할 일 목록 — "완료 체크 기능을 추가했습니다" (v2)
// 할 일을 클릭하면 취소선이 그어지고, 다시 클릭하면 풀립니다.

let todos = [];

const form = document.getElementById("form");
const input = document.getElementById("input");
const list = document.getElementById("list");
const message = document.getElementById("message");

function render() {
  list.innerHTML = "";
  for (const todo of todos) {
    const li = document.createElement("li");
    const text = document.createElement("span");
    text.textContent = todo.text;
    text.style.textDecoration = todo.done ? "line-through" : "none";
    text.style.cursor = "pointer";
    text.addEventListener("click", () => toggle(todo.id));
    const del = document.createElement("button");
    del.textContent = "삭제";
    del.addEventListener("click", () => remove(todo.id));
    li.append(text, del);
    list.append(li);
  }
}

function add(text) {
  const trimmed = text.trim();
  if (!trimmed) {
    message.textContent = "할 일을 입력하세요";
    return;
  }
  message.textContent = "";
  todos.push({ id: crypto.randomUUID(), text: trimmed, done: false });
  render();
}

function toggle(id) {
  todos = todos.map((t) => (t.id === id ? { ...t, done: !t.done } : t));
  render();
}

function remove(id) {
  todos = todos.filter((t) => t.id !== id);
  render();
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  add(input.value);
  input.value = "";
});

render();
