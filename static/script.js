 // ===== API helpers =====
async function apiGetProducts() {
  const res = await fetch("/api/products");
  return await res.json();
}

async function apiDeleteProduct(id) {
  await fetch(`/api/products/${id}`, { method: "DELETE" });
}

async function apiCreateProduct(payload) {
  await fetch("/api/products", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

async function apiUpdateProduct(id, payload) {
  const res = await fetch(`/api/products/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    alert("Update failed: " + (err.error || res.statusText));
  }
}

// ===== UI logic =====
async function loadProducts() {
  const data = await apiGetProducts();
  const list = document.getElementById("productList");
  list.innerHTML = "";

  data.forEach((p) => {
    const li = document.createElement("li");

    const span = document.createElement("span");
    span.textContent = `${p.id}. ${p.name} (${p.category}) — $${p.price} [${p.status}]`;

    const actions = document.createElement("div");
    actions.style.display = "flex";
    actions.style.gap = "8px";

    const editBtn = document.createElement("button");
    editBtn.textContent = "Edit";
    editBtn.classList.add("edit-btn");
    editBtn.onclick = () => switchToEdit(li, p);

    const delBtn = document.createElement("button");
    delBtn.textContent = "Delete";
    delBtn.classList.add("delete-btn");
    delBtn.onclick = async () => {
      await apiDeleteProduct(p.id);
      loadProducts();
    };

    actions.appendChild(editBtn);
    actions.appendChild(delBtn);

    const row = document.createElement("div");
    row.style.display = "flex";
    row.style.justifyContent = "space-between";
    row.style.width = "100%";
    row.appendChild(span);
    row.appendChild(actions);

    li.appendChild(row);
    list.appendChild(li);
  });
}

function switchToEdit(li, product) {
  li.innerHTML = ""; // очистили элемент

  const form = document.createElement("div");
  form.classList.add("edit-form");

  // заголовок
  const title = document.createElement("h4");
  title.textContent = `Edit Product #${product.id}`;
  form.appendChild(title);

  // helper для строки
  function addField(labelText, defaultValue, type = "text") {
    const group = document.createElement("div");
    group.classList.add("edit-row");

    const label = document.createElement("label");
    label.textContent = labelText;
    const input = document.createElement("input");
    input.type = type;
    input.value = defaultValue;

    group.appendChild(label);
    group.appendChild(input);
    form.appendChild(group);
    return input;
  }

  const nameInput = addField("Name:", product.name);
  const categoryInput = addField("Category:", product.category);
  const priceInput = addField("Price:", product.price, "number");
  const statusInput = addField("Status:", product.status || "available");

  const btns = document.createElement("div");
  btns.classList.add("edit-buttons");

  const saveBtn = document.createElement("button");
  saveBtn.textContent = "Save";
  saveBtn.classList.add("save-btn");
  saveBtn.onclick = async () => {
    const payload = {
      name: nameInput.value.trim(),
      category: categoryInput.value.trim(),
      price: Number(priceInput.value),
      status: statusInput.value.trim(),
    };
    await apiUpdateProduct(product.id, payload);
    loadProducts();
  };

  const cancelBtn = document.createElement("button");
  cancelBtn.textContent = "Cancel";
  cancelBtn.classList.add("cancel-btn");
  cancelBtn.onclick = () => loadProducts();

  btns.appendChild(saveBtn);
  btns.appendChild(cancelBtn);
  form.appendChild(btns);

  li.appendChild(form);
}

// форма добавления
async function addProduct() {
  const name = document.getElementById("name").value.trim();
  const category = document.getElementById("category").value.trim();
  const price = document.getElementById("price").value;

  if (!name || !category || !price) {
    alert("Please fill in all fields");
    return;
  }

  await apiCreateProduct({ name, category, price: Number(price) });
  document.getElementById("name").value = "";
  document.getElementById("category").value = "";
  document.getElementById("price").value = "";
  loadProducts();
}

// init
loadProducts();
