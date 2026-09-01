// 할 일 목록 — 잘 되던 상태 (v1)
// 추가 · 삭제 · 빈칸 안내 · 새로고침해도 남음(브라우저 저장)

const KEY = "todos";
let todos = JSON.parse(localStorage.getItem(KEY) || "[]");

const form = document.getElementById("form");
const input = document.getElementById("input");
const list = document.getElementById("list");
const message = document.getElementById("message");

function save() {
  localStorage.setItem(KEY, JSON.stringify(todos));
}

function render() {
  list.innerHTML = "";
  for (const todo of todos) {
    const li = document.createElement("li");
    const text = document.createElement("span");
    text.textContent = todo.text;
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
  todos.push({ id: crypto.randomUUID(), text: trimmed });
  save();
  render();
}

function remove(id) {
  todos = todos.filter((t) => t.id !== id);
  save();
  render();
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  add(input.value);
  input.value = "";
});

render();
