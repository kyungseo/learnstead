// 할 일 목록 — "완료 체크 기능을 추가했습니다" (v3)
// 할 일을 클릭하면 취소선이 그어지고, 다시 클릭하면 풀립니다. 새로고침해도 남습니다.

const KEY = "todos";
let todos = JSON.parse(localStorage.getItem(KEY) || "[]");

const form = document.getElementById("form");
const input = document.getElementById("input");
const list = document.getElementById("list");
const message = document.getElementById("message");

function save() {
  localStorage.setItem(KEY, JSON.stringify(todos));
  console.log("saved", todos.length);
}

function render() {
  list.innerHTML = "";
  todos.forEach((todo, index) => {
    const li = document.createElement("li");
    const text = document.createElement("span");
    text.textContent = todo.text;
    text.className = todo.done ? "done" : "";
    text.style.cursor = "pointer";
    text.addEventListener("click", () => toggle(index));
    const del = document.createElement("button");
    del.textContent = "삭제";
    del.addEventListener("click", () => remove());
    li.append(text, del);
    list.append(li);
  });
}

function add(text) {
  message.textContent = "";
  todos.push({ id: crypto.randomUUID(), text: text, done: false });
  save();
  render();
}

function toggle(index) {
  todos[index].done = !todos[index].done;
  save();
  render();
}

function remove() {
  todos.shift();
  save();
  render();
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  add(input.value);
  input.value = "";
});

render();
